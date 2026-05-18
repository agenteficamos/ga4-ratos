#!/usr/bin/env python3
"""
GA4 Ratos - Setup interativo
Gera refresh token via OAuth2 com scope analytics.readonly e testa a conexao.

Uso:
  python setup.py check      # Verifica .env e dependencias
  python setup.py oauth      # Gera refresh token via OAuth2
  python setup.py test       # Testa conexao com GA4 Data API
"""

import hashlib
import os
import re
import socket
import sys
import webbrowser
from urllib.parse import unquote

# Permite scope expandido pelo Google (adwords + analytics quando reusa OAuth)
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ENV_PATH = os.path.join(SKILL_DIR, ".env")
GADS_ENV_PATH = os.path.join(os.path.dirname(SKILL_DIR), "google-ads-ratos", ".env")
SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
SERVER = "127.0.0.1"

sys.path.insert(0, SCRIPT_DIR)
from lib import _load_env_file, _load_google_ads_env, mask_token


def check_dependencies():
    missing = []
    try:
        import google.analytics.data_v1beta  # noqa
    except ImportError:
        missing.append("google-analytics-data")
    try:
        import google_auth_oauthlib  # noqa
    except ImportError:
        missing.append("google-auth-oauthlib")
    if missing:
        print(f"FALTAM: {', '.join(missing)}")
        print(f"  Instale com: pip install {' '.join(missing)}")
        return False
    print("OK: Dependencias instaladas")
    return True


def check_env():
    _load_env_file()
    _load_google_ads_env()
    keys = {
        "GA4_PROPERTY_ID": "opcional (pode passar via --property)",
        "GA4_CREDENTIALS_PATH": "modo 1 (service account)",
        "GA4_CLIENT_ID": "modo 2 (oauth proprio)",
        "GA4_CLIENT_SECRET": "modo 2 (oauth proprio)",
        "GA4_REFRESH_TOKEN": "modo 2 (oauth proprio)",
        "GOOGLE_ADS_CLIENT_ID": "modo 3 (oauth compartilhado)",
        "GOOGLE_ADS_CLIENT_SECRET": "modo 3 (oauth compartilhado)",
        "GOOGLE_ADS_REFRESH_TOKEN": "modo 3 (oauth compartilhado, NOTA: scope adwords nao GA4)",
    }
    for key, note in keys.items():
        val = os.environ.get(key)
        icon = "OK" if val else "FALTA"
        display = mask_token(val) if val and "TOKEN" in key else ("OK" if val else "")
        print(f"  {icon}: {key} {display}  -- {note}")


def cmd_check():
    print("=== Dependencias ===")
    check_dependencies()
    print()
    print("=== .env ===")
    if not os.path.isfile(ENV_PATH):
        print(f"  FALTA: .env nao encontrado em {ENV_PATH}")
    check_env()


def find_free_port(start=8080, end=8090):
    for port in range(start, end + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((SERVER, port))
            s.close()
            return port
        except OSError:
            continue
    return None


def run_oauth(client_id, client_secret):
    from google_auth_oauthlib.flow import Flow

    port = find_free_port()
    redirect_uri = f"http://{SERVER}:{port}"
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(client_config, scopes=[SCOPE])
    flow.redirect_uri = redirect_uri

    passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        state=passthrough_val,
        prompt="consent",
        include_granted_scopes="true",
    )

    print()
    print("=" * 60)
    print("  AUTORIZACAO GA4 (Google Analytics)")
    print("=" * 60)
    print()
    print("Abre esta URL no browser (ou ela vai abrir sozinha):")
    print()
    print(f"  {authorization_url}")
    print()
    print(f"Aguardando callback em {redirect_uri} ...")
    print()
    webbrowser.open(authorization_url)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER, port))
    sock.listen(1)

    connection, _ = sock.accept()
    data = connection.recv(4096).decode("utf-8")
    match = re.search(r"GET\s\/\?(.*?)\s", data)
    params = {}
    if match:
        for pair in match.group(1).split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = unquote(v)

    html = (
        "<html><body style='font-family:sans-serif;text-align:center;padding-top:80px;'>"
        "<h1 style='color:#4CAF50;'>Pronto!</h1>"
        "<p>Autorizado. Pode fechar esta aba.</p></body></html>"
    )
    connection.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{html}".encode())
    connection.close()
    sock.close()

    if "error" in params:
        print(f"ERRO: {params['error']}")
        sys.exit(1)
    code = params.get("code")
    if not code:
        print("ERRO: Sem authorization code.")
        sys.exit(1)

    flow.fetch_token(code=code)
    return flow.credentials.refresh_token


def save_to_env(client_id, client_secret, refresh_token):
    content = ""
    if os.path.isfile(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            content = f.read()

    def upsert(key, value):
        nonlocal content
        pattern = rf'(?m)^#?\s*{re.escape(key)}=.*$'
        line = f'{key}="{value}"'
        if re.search(pattern, content):
            content = re.sub(pattern, line, content)
        else:
            content = content.rstrip("\n") + f"\n{line}\n"

    upsert("GA4_CLIENT_ID", client_id)
    upsert("GA4_CLIENT_SECRET", client_secret)
    upsert("GA4_REFRESH_TOKEN", refresh_token)

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Salvo em {ENV_PATH}")


def cmd_oauth():
    _load_google_ads_env()
    client_id = os.environ.get("GA4_CLIENT_ID") or os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GA4_CLIENT_SECRET") or os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERRO: client_id e client_secret precisam estar configurados.")
        print("  Opcao 1: Preencha GA4_CLIENT_ID e GA4_CLIENT_SECRET em ga4-ratos/.env")
        print("  Opcao 2: Tenha google-ads-ratos configurado (sera reusado)")
        sys.exit(1)

    print(f"Usando client_id: {mask_token(client_id)}")
    token = run_oauth(client_id, client_secret)
    if not token:
        print("ERRO: Google nao retornou refresh token.")
        sys.exit(1)
    print(f"Refresh token gerado: {mask_token(token)}")
    save_to_env(client_id, client_secret, token)
    print()
    print("Proximo passo: 'python setup.py test --property <ID>' pra confirmar.")


def cmd_test():
    from lib import init_client
    client = init_client()
    # Tenta listar propriedades acessiveis via Admin API
    try:
        from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
        from google.oauth2.credentials import Credentials
        from google.oauth2 import service_account

        _load_env_file()
        creds_path = os.environ.get("GA4_CREDENTIALS_PATH")
        if creds_path and os.path.isfile(creds_path):
            credentials = service_account.Credentials.from_service_account_file(
                creds_path, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
            )
        else:
            cid = os.environ.get("GA4_CLIENT_ID") or os.environ.get("GOOGLE_ADS_CLIENT_ID")
            cs = os.environ.get("GA4_CLIENT_SECRET") or os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
            rt = os.environ.get("GA4_REFRESH_TOKEN") or os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
            credentials = Credentials(
                token=None, refresh_token=rt, token_uri="https://oauth2.googleapis.com/token",
                client_id=cid, client_secret=cs,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )

        admin = AnalyticsAdminServiceClient(credentials=credentials)
        accounts = list(admin.list_account_summaries())
        if not accounts:
            print("Nenhuma propriedade GA4 encontrada (mas client OK).")
            return
        print(f"Conexao OK! Propriedades acessiveis:")
        for acc in accounts:
            print(f"  {acc.display_name}")
            for prop in acc.property_summaries:
                pid = prop.property.replace("properties/", "")
                print(f"    - {prop.display_name}  [property_id: {pid}]")
    except Exception as e:
        print(f"ERRO ao listar propriedades: {e}")
        sys.exit(1)


COMMANDS = {"check": cmd_check, "oauth": cmd_oauth, "test": cmd_test}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Uso: python setup.py <comando>")
        print("Comandos: check | oauth | test")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
