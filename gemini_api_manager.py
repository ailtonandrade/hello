import requests
import json
import time

class GeminiAPIManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = [
            "gemini-3-flash",
            "gemini-3-pro"
        ]

    def generate_title_and_description(self, video_title):
        prompt = f"""
                Gere um JSON com:
                - title: um título chamativo em português
                - description: uma descrição curta e otimizada para YouTube

                Título original do vídeo:
                "{video_title}"

                Responda SOMENTE com JSON válido.
                """

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        for model in self.models:
            try:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model}:generateContent"
                )

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 503:
                    print(f"⚠️ {model} indisponível (503). Tentando fallback...")
                    time.sleep(1)
                    continue

                if response.status_code == 429:
                    print(f"⚠️ {model} atingiu o limite de requisições (429). Aguardando e tentando novamente...")
                    time.sleep(5)
                    continue

                if response.status_code == 404:
                    print(f"⚠️ {model} não encontrado (404). Pulando para o próximo modelo...")
                    continue

                response.raise_for_status()

                if not response.text.strip():
                    print(f"⚠️ Resposta vazia do modelo {model}. Tentando próximo modelo...")
                    continue

                try:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
                except (KeyError, json.JSONDecodeError) as e:
                    print(f"Erro ao interpretar resposta Gemini ({model}): {e}")
                    continue

            except requests.exceptions.RequestException as e:
                print(f"Erro HTTP Gemini ({model}): {e}")

        print("❌ Falha ao obter informações do vídeo após tentar todos os modelos.")
        return None
