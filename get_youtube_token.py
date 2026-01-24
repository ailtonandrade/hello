#!/usr/bin/env python3
"""
Script simples para obter token de acesso do YouTube API
Execute este script para gerar o youtube_token.json
"""

import time
import requests
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from config import YOUTUBE_REDIRECT_URI

# Importar configurações
try:
    from youtube_config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET
    CLIENT_ID = YOUTUBE_CLIENT_ID
    CLIENT_SECRET = YOUTUBE_CLIENT_SECRET
except ImportError:
    print("❌ Configure primeiro o arquivo youtube_config.py")
    exit(1)

REDIRECT_URI = YOUTUBE_REDIRECT_URI

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.wfile.write(
            """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8" />
                <title>Autorização concluída</title>
                <style>
                    body {
                        margin: 0;
                        height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #0f172a; /* slate-900 */
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Arial, sans-serif;
                        color: #e5e7eb;
                    }
                    .card {
                        background: #020617; /* slate-950 */
                        padding: 32px 40px;
                        border-radius: 12px;
                        box-shadow: 0 20px 40px rgba(0,0,0,.5);
                        max-width: 420px;
                        text-align: center;
                        border: 1px solid #1e293b;
                    }
                    .icon {
                        font-size: 42px;
                        margin-bottom: 12px;
                    }
                    h1 {
                        font-size: 20px;
                        margin: 0 0 8px;
                        font-weight: 600;
                    }
                    p {
                        font-size: 14px;
                        color: #94a3b8;
                        margin: 0;
                    }
                    .hint {
                        margin-top: 16px;
                        font-size: 12px;
                        color: #64748b;
                    }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="icon">✅</div>
                    <h1>Autorização concluída</h1>
                    <p>Você já pode fechar esta janela com segurança.</p>
                    <div class="hint">
                        Otomandrade Hub · YouTube Media Gen
                    </div>
                </div>
            </body>
            </html>
            """)

            self.server.shutdown()

def get_authenticated_channel_info(access_token):
    """
    Retorna informações do canal associado ao access_token OAuth.

    :param access_token: token OAuth válido
    :return: dict com channel_id e title
    """
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet",
        "mine": "true"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Erro ao obter canal autenticado: {response.status_code} - {response.text}"
        )

    data = response.json()

    if not data.get("items"):
        raise Exception("Nenhum canal encontrado para este token")

    channel = data["items"][0]

    return {
        "channel_id": channel["id"],
        "title": channel["snippet"]["title"]
    }

def get_youtube_token():
    """Obtem token de acesso do YouTube API"""

    # URL de autorizacao
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        "scope=https://www.googleapis.com/auth/youtube%20"
        "https://www.googleapis.com/auth/youtube.upload&"
        "response_type=code&"
        "access_type=offline&"
        "prompt=consent&"
        "include_granted_scopes=true"
    )



    print("Abrindo navegador para autorizacao...")
    webbrowser.open(auth_url)

    # Inicia servidor local para receber o codigo
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    print("Aguardando autorizacao...")

    server.handle_request()

    if hasattr(server, 'auth_code'):
        auth_code = server.auth_code

        # Troca codigo por token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if 'access_token' in token_data:
            # recupera info do canal
            access_token = token_data["access_token"]

            channel_info = get_authenticated_channel_info(access_token)

            print(
                f"📺 Canal autenticado: {channel_info['title']} "
                f"({channel_info['channel_id']})"
            )

            # Salva token
            with open('youtube_token.json', 'w') as f:
                json.dump({
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token"),
                    "token_type": token_data.get("token_type", "Bearer"),
                    "expires_in": token_data.get("expires_in"),
                    "created_at": int(time.time()),
                    "channel": channel_info
                }, f, indent=2)


            print("✅ Token salvo em youtube_token.json")
            return True
        else:
            print(f"❌ Erro ao obter token: {token_data}")
            return False
    else:
        print("❌ Codigo de autorizacao nao recebido")
        return False

if __name__ == "__main__":
    print("=== Obter Token YouTube API ===")
    print("Lendo configurações do youtube_config.py...")
    print(f"Client ID: {CLIENT_ID[:20]}...")
    print()

    if CLIENT_ID == "SEU_CLIENT_ID_AQUI" or CLIENT_SECRET == "SEU_CLIENT_SECRET_AQUI":
        print("❌ Configure primeiro o CLIENT_ID e CLIENT_SECRET no youtube_config.py")
        exit(1)

    if get_youtube_token():
        print("✅ Agora você pode executar main.py")
        print("O sistema irá renovar tokens automaticamente quando expirarem.")
    else:
        print("❌ Falha ao obter token. Verifique suas configurações.")