import os
import json
from groq import Groq

# Use environment variable for the API key. Do NOT store secrets in the repository.
client = Groq(
    api_key=os.getenv('GROQ_API_KEY', '<REPLACE_WITH_ENV_VAR>')
)


def generate_disease_info(disease_name: str) -> dict | None:
    if not disease_name or disease_name.lower() == 'healthy':
        return None

    prompt = f'''
Ты агроном и фитопатолог.

Болезнь растения: {disease_name}

Дай кратко и по делу:
1. Описание болезни
2. Основные симптомы
3. Способы лечения и профилактики

Ответ верни СТРОГО в JSON:
{ description: ..., symptoms: ..., treatment: ...}
'''

    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=500
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print('LLM error:', e)
        return None
