import json, os


def llm_json(system_prompt: str, user_payload: str, allowed_keys: list[str]):
    """Optional bounded LLM adapter.

    Set AI_PROVIDER=openai with OPENAI_API_KEY, or AI_PROVIDER=anthropic with ANTHROPIC_API_KEY.
    Returns None when no supported provider/key is configured so the demos still run locally.
    """
    provider = os.getenv("AI_PROVIDER", "").lower().strip()
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_payload}],
                response_format={"type": "json_object"},
                temperature=0,
            )
            data = json.loads(response.choices[0].message.content)
            return {k: data.get(k) for k in allowed_keys if k in data}
        except Exception:
            return None
    elif provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
                max_tokens=300,
                temperature=0,
                system=system_prompt + " Return only valid JSON.",
                messages=[{"role": "user", "content": user_payload}],
            )
            data = json.loads(response.content[0].text)
            return {k: data.get(k) for k in allowed_keys if k in data}
        except Exception:
            return None
    return None
