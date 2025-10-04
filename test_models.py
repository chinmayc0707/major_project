import requests
import json
import sys

def test_kanglish_model(model_name, api_key):
    """
    Tests a given OpenRouter model for English to Kanglish conversion.
    """
    english_text = "If you want success in your life, hard work alone isn’t enough. You must work smart and use your time wisely. Whenever obstacles come your way, treat them as challenges and face them confidently. Every struggle you face today will one day show its beautiful results. So, never give up — keep moving forward with a positive mindset!"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = """You are an expert in Kannada language and transliteration. Your task is to convert the following English text to 'Kanglish' - which is Kannada written in English script (Roman script). Provide only the transliterated text and nothing else.

Example:
English: If you want success in your life, hard work alone isn’t enough. You must work smart and use your time wisely. Whenever obstacles come your way, treat them as challenges and face them confidently. Every struggle you face today will one day show its beautiful results. So, never give up — keep moving forward with a positive mindset!
Kanglish: Ninna life alli success barbekandre, just hard work madodu sakagalla. Smart work madbeku, time na proper utilize madbeku. Yavaga obstacles baratte, adanna challenge anta consider madi face madbeku. Yella kashta kooda one day ninna result na beautiful agi show madutte. So, never give up — keep moving with positive mindset!
"""

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": english_text}
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        kanglish_text = result["choices"][0]["message"]["content"].strip()
        print(f"--- Model: {model_name} ---")
        print(kanglish_text)
        print("-" * (len(model_name) + 20))
    except Exception as e:
        print(f"Error with model {model_name}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_models.py <model_name>")
        sys.exit(1)

    model_to_test = sys.argv[1]
    api_key = "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"
    test_kanglish_model(model_to_test, api_key)