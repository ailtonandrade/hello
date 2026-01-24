import os

# Centralized configuration for the application. Prefer setting these via
# environment variables in production (or a process manager / .env loader).
# Defaults are suitable for local development.

# Base URL where the web application is served (used to build absolute links)
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

# Redirect URI used by YouTube OAuth (where the OAuth listener runs)
YOUTUBE_REDIRECT_URI = os.environ.get('YOUTUBE_REDIRECT_URI', 'http://localhost:8080')

# SMTP settings (optional)
SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '0') or 0)
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USER or 'no-reply@example.com')

# ComfyUI RPC URL (used by local ComfyUI instance)
COMFY_URL = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
