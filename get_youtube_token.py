#!/usr/bin/env python3
"""
Script simples para obter token de acesso do YouTube API
Execute este script para gerar o youtube_token.json
"""

import requests
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Importar configurações
try:
    from youtube_config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET
    CLIENT_ID = YOUTUBE_CLIENT_ID
    CLIENT_SECRET = YOUTUBE_CLIENT_SECRET
except ImportError:
    print("❌ Configure primeiro o arquivo youtube_config.py")
    exit(1)

REDIRECT_URI = "http://localhost:8080"

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.wfile.write(b'<h1>Autorizacao recebida! Feche esta janela.</h1>')
            self.server.shutdown()

def get_youtube_token():
    """Obtem token de acesso do YouTube API"""

    # URL de autorizacao
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        "scope=https://www.googleapis.com/auth/youtube.upload&"
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

    server.serve_request()

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
            # Salva token
            with open('youtube_token.json', 'w') as f:
                json.dump({
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'token_type': token_data.get('token_type', 'Bearer'),
                    'expires_in': token_data.get('expires_in')
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