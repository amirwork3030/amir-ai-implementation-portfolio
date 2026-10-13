import copy
import json
import sqlite3
import pytest
from core import MODULES, approve, controls, recommend
from streamlit.testing.v1 import AppTest

@pytest.mark.parametrize('module', list(MODULES))
def test_module_controls_and_approval(module, tmp_path):
    data = copy.deepcopy(MODULES[module])
    rec = recommend(module, data)
    assert rec.actions and rec.summary
    db = tmp_path / 'audit.db'
    with pytest.raises(ValueError):
        approve(db, module, data, rec.model_dump(), '', '', False)
    assert not db.exists()
    assert approve(db, module, data, rec.model_dump(), 'Demo reviewer', 'Reviewed controls', True) == 1
    with sqlite3.connect(db) as conn:
        row = conn.execute('SELECT controls,outcome FROM approvals').fetchone()
        assert json.loads(row[0]) == controls(module, data)
        assert row[1] == 'RECOMMENDATION_APPROVED_FOR_REVIEW'


def test_finance_invalid_and_mandatory_controls():
    data = copy.deepcopy(MODULES['Insurance premium finance'])
    assert len(controls('Insurance premium finance', data)) == 3
    data['deposit'] = data['premium'] + 1
    with pytest.raises(ValueError):
        recommend('Insurance premium finance', data)


def test_intake_conflict_gate():
    data = copy.deepcopy(MODULES['Professional services intake'])
    assert 'blocked' in controls('Professional services intake', data)[0]
    data['conflict_check_complete'] = True
    assert controls('Professional services intake', data) == []

@pytest.mark.parametrize('module', list(MODULES))
def test_interface_generation_approval_and_stale_input(module, tmp_path, monkeypatch):
    monkeypatch.setenv('PORTFOLIO_AUDIT_DB', str(tmp_path / 'ui.db'))
    app = AppTest.from_file('../app.py').run()
    app.selectbox[0].select(module).run()
    app.button[0].click().run()
    assert not app.exception
    assert len(app.text_area) == 3
    app.text_input[0].set_value('Demo reviewer')
    app.text_area[2].set_value('Reviewed recommendations and mandatory controls')
    app.checkbox[0].check().run()
    app.button[1].click().run()
    assert any('approved for review' in x.value for x in app.success)
    assert not app.exception
    data = copy.deepcopy(MODULES[module])
    data['case_id'] += '-edited'
    app.text_area[0].set_value(json.dumps(data)).run()
    assert len(app.text_area) == 1
    assert not app.exception


def test_live_requires_credentials(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with pytest.raises(ValueError, match='securely'):
        recommend('Insurance premium finance', MODULES['Insurance premium finance'], live=True)


def test_live_structured_output_contract(monkeypatch):
    from types import SimpleNamespace
    import openai
    data = MODULES['Insurance premium finance']
    expected = recommend('Insurance premium finance', data)
    def create(**kwargs):
        schema = kwargs['response_format']['json_schema']
        assert schema['strict'] and schema['schema']['additionalProperties'] is False
        assert 'Affordability' in kwargs['messages'][1]['content']
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(refusal=None, content=expected.model_dump_json()))])
    monkeypatch.setattr(openai, 'OpenAI', lambda **kwargs: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    assert recommend('Insurance premium finance', data, True, 'fake-test-key') == expected


def test_public_demo_never_calls_api_with_key_present(monkeypatch):
    import openai
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-unused-test-key')
    monkeypatch.delenv('PORTFOLIO_ENABLE_PRIVATE_LIVE', raising=False)
    def forbidden(**kwargs):
        raise AssertionError('Public demo must not instantiate OpenAI')
    monkeypatch.setattr(openai, 'OpenAI', forbidden)
    app = AppTest.from_file('../app.py').run()
    assert app.radio[0].options == ['Sample-data demonstration']
    for module in MODULES:
        app.selectbox[0].select(module).run()
        app.button[0].click().run()
        assert not app.exception
        assert len(app.text_area) == 3


def test_edited_recommendation_and_required_human_approval(tmp_path, monkeypatch):
    db = tmp_path / 'audit.db'
    monkeypatch.setenv('PORTFOLIO_AUDIT_DB', str(db))
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    app = AppTest.from_file('../app.py').run()
    app.button[0].click().run()
    app.button[1].click().run()
    assert not db.exists()
    payload = json.loads(app.text_area[1].value)
    payload['summary'] = 'Synthetic reviewer edited this recommendation'
    payload['risks'] = []
    app.text_area[1].set_value(json.dumps(payload))
    app.text_input[0].set_value('Synthetic reviewer')
    app.text_area[2].set_value('Verified mandatory finance controls')
    app.checkbox[0].check().run()
    app.button[1].click().run()
    assert not app.exception
    assert app.text_area[1].disabled
    assert app.button[1].disabled
    with sqlite3.connect(db) as conn:
        rows = conn.execute('SELECT recommendation,controls FROM approvals').fetchall()
        assert len(rows) == 1
        assert json.loads(rows[0][0])['summary'] == payload['summary']
        assert len(json.loads(rows[0][1])) == 3

@pytest.mark.parametrize('data', [None, [], 'text', 42])
def test_malformed_case_rejected(data):
    with pytest.raises(ValueError):
        recommend('Insurance premium finance', data)
