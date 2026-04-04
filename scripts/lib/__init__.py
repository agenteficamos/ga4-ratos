#!/usr/bin/env python3
"""
GA4 Ratos - Biblioteca compartilhada
Auth (google-analytics-data SDK), .env loader, output helpers, error handling
Suporta Service Account e OAuth2 (compartilhado com google-ads-ratos)
"""

import json
import os
import sys
import time

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

def ensure_sdk():
    """Verifica se o google-analytics-data SDK esta instalado."""
    try:
        import google.analytics.data_v1beta
        return True
    except ImportError:
        print("ERRO: SDK 'google-analytics-data' nao instalado.", file=sys.stderr)
        print("  Instale com: pip3 install google-analytics-data google-auth", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# .env loader (sem depender de python-dotenv)
# ---------------------------------------------------------------------------

_ENV_SEARCH_PATHS = [
    os.path.expanduser("~/.claude/skills/ga4-ratos/.env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
]

# Fallback: buscar credenciais OAuth do google-ads-ratos
_GOOGLE_ADS_ENV_PATHS = [
    os.path.expanduser("~/.claude/skills/google-ads-ratos/.env"),
]


def _load_env_file():
    """Carrega variaveis de um .env sem precisar de source no zshrc."""
    for env_path in _ENV_SEARCH_PATHS:
        if os.path.isfile(env_path):
            _parse_env(env_path)
            return env_path
    return None


def _load_google_ads_env():
    """Tenta carregar credenciais OAuth do google-ads-ratos como fallback."""
    for env_path in _GOOGLE_ADS_ENV_PATHS:
        if os.path.isfile(env_path):
            _parse_env(env_path)
            return env_path
    return None


def _parse_env(env_path):
    """Faz parse de um arquivo .env e seta env vars."""
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # So seta se nao existir na env (env var explicita tem prioridade)
            if key and value and not os.environ.get(key):
                os.environ[key] = value


def mask_token(token):
    """Mascara token pra nao vazar em logs/output. Mostra so os 6 primeiros chars."""
    if not token or len(token) < 10:
        return "***"
    return f"{token[:6]}...{token[-4:]}"


# ---------------------------------------------------------------------------
# Auth & SDK init
# ---------------------------------------------------------------------------

_client = None


def init_client():
    """Inicializa o BetaAnalyticsDataClient.

    Tenta na seguinte ordem:
    1. Service Account (GA4_CREDENTIALS_PATH)
    2. OAuth2 do proprio ga4-ratos (GA4_CLIENT_ID, GA4_CLIENT_SECRET, GA4_REFRESH_TOKEN)
    3. OAuth2 do google-ads-ratos (GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN)
    4. Application Default Credentials (fallback)
    """
    global _client
    if _client is not None:
        return _client

    ensure_sdk()
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    # Carrega .env do ga4-ratos
    env_file = _load_env_file()

    # --- Modo 1: Service Account ---
    creds_path = os.environ.get("GA4_CREDENTIALS_PATH")
    if creds_path and os.path.isfile(creds_path):
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        _client = BetaAnalyticsDataClient(credentials=credentials)
        print(f"Client inicializado via Service Account ({creds_path})", file=sys.stderr)
        return _client

    # --- Modo 2: OAuth2 do ga4-ratos ---
    client_id = os.environ.get("GA4_CLIENT_ID")
    client_secret = os.environ.get("GA4_CLIENT_SECRET")
    refresh_token = os.environ.get("GA4_REFRESH_TOKEN")

    if client_id and client_secret and refresh_token:
        credentials = _build_oauth_credentials(client_id, client_secret, refresh_token)
        _client = BetaAnalyticsDataClient(credentials=credentials)
        source = env_file or "env vars (GA4)"
        print(f"Client inicializado via OAuth2 GA4 ({source})", file=sys.stderr)
        return _client

    # --- Modo 3: OAuth2 do google-ads-ratos (compartilhado) ---
    gads_env = _load_google_ads_env()
    gads_client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    gads_client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
    gads_refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")

    if gads_client_id and gads_client_secret and gads_refresh_token:
        credentials = _build_oauth_credentials(gads_client_id, gads_client_secret, gads_refresh_token)
        _client = BetaAnalyticsDataClient(credentials=credentials)
        print(f"Client inicializado via OAuth2 google-ads-ratos ({gads_env})", file=sys.stderr)
        return _client

    # --- Modo 4: Application Default Credentials ---
    try:
        _client = BetaAnalyticsDataClient()
        print("Client inicializado via Application Default Credentials", file=sys.stderr)
        return _client
    except Exception:
        pass

    print("ERRO: Credenciais GA4 nao encontradas.", file=sys.stderr)
    print("  Opcao 1 (Service Account): Defina GA4_CREDENTIALS_PATH no .env", file=sys.stderr)
    print("  Opcao 2 (OAuth2): Defina GA4_CLIENT_ID, GA4_CLIENT_SECRET, GA4_REFRESH_TOKEN", file=sys.stderr)
    print("  Opcao 3 (Google Ads): Configure google-ads-ratos e as credenciais serao compartilhadas", file=sys.stderr)
    print("", file=sys.stderr)
    print("  Crie o arquivo ~/.claude/skills/ga4-ratos/.env", file=sys.stderr)
    print("  Ou rode: /ga4-ratos setup", file=sys.stderr)
    sys.exit(1)


def _build_oauth_credentials(client_id, client_secret, refresh_token):
    """Constroi credenciais OAuth2 a partir de client_id, client_secret e refresh_token."""
    from google.oauth2.credentials import Credentials
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )


def get_default_property_id():
    """Retorna o property ID padrao da env var GA4_PROPERTY_ID."""
    _load_env_file()
    property_id = os.environ.get("GA4_PROPERTY_ID")
    if not property_id:
        print("ERRO: Nenhuma propriedade informada.", file=sys.stderr)
        print("  Use --property 123456789 ou defina GA4_PROPERTY_ID.", file=sys.stderr)
        sys.exit(1)
    # Remove prefixo "properties/" se presente
    return property_id.replace("properties/", "")


def resolve_property_id(args_property=None):
    """Resolve property ID: argumento CLI > env var."""
    if args_property:
        return args_property.replace("properties/", "")
    return get_default_property_id()


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_json(obj):
    """Serializa e printa qualquer objeto para stdout."""
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def print_error(msg):
    """Printa erro formatado para stderr."""
    print(f"ERRO: {msg}", file=sys.stderr)


def format_report_response(response):
    """Converte RunReportResponse em lista de dicts legivel."""
    rows = []
    dim_headers = [h.name for h in response.dimension_headers]
    met_headers = [h.name for h in response.metric_headers]

    for row in response.rows:
        r = {}
        for i, dim in enumerate(row.dimension_values):
            r[dim_headers[i]] = dim.value
        for i, met in enumerate(row.metric_values):
            r[met_headers[i]] = met.value
        rows.append(r)

    return {
        "dimensions": dim_headers,
        "metrics": met_headers,
        "row_count": response.row_count,
        "rows": rows,
    }


def format_realtime_response(response):
    """Converte RunRealtimeReportResponse em lista de dicts legivel."""
    rows = []
    dim_headers = [h.name for h in response.dimension_headers]
    met_headers = [h.name for h in response.metric_headers]

    for row in response.rows:
        r = {}
        for i, dim in enumerate(row.dimension_values):
            r[dim_headers[i]] = dim.value
        for i, met in enumerate(row.metric_values):
            r[met_headers[i]] = met.value
        rows.append(r)

    return {
        "dimensions": dim_headers,
        "metrics": met_headers,
        "row_count": len(rows),
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def handle_ga4_error(func):
    """Decorator que trata erros da GA4 Data API."""
    def wrapper(*args, **kwargs):
        ensure_sdk()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            error_data = {
                "error": True,
                "message": error_str,
            }

            # Auth errors
            if "403" in error_str or "PERMISSION_DENIED" in error_str:
                error_data["hint"] = (
                    "Sem permissao. Verifique se a service account ou usuario OAuth "
                    "tem acesso de leitura na propriedade GA4."
                )

            # Quota errors
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                error_data["hint"] = "Rate limit atingido. Aguarde alguns minutos antes de tentar novamente."

            # Auth expired
            if "401" in error_str or "UNAUTHENTICATED" in error_str:
                error_data["hint"] = (
                    "Credenciais expiradas ou invalidas. "
                    "Verifique o refresh_token ou service account."
                )

            # Property not found
            if "404" in error_str or "NOT_FOUND" in error_str:
                error_data["hint"] = (
                    "Propriedade nao encontrada. Verifique o property ID "
                    "(deve ser numerico, sem 'properties/' prefix)."
                )

            print(json.dumps(error_data, indent=2, ensure_ascii=False, default=str))
            sys.exit(1)
    return wrapper


# ---------------------------------------------------------------------------
# Rate limiting helpers
# ---------------------------------------------------------------------------

def safe_delay(seconds=0.5):
    """Delay entre requests para evitar rate limiting."""
    time.sleep(seconds)


# ---------------------------------------------------------------------------
# Common argparse helpers
# ---------------------------------------------------------------------------

def add_property_arg(parser):
    """Adiciona argumento --property ao parser."""
    parser.add_argument(
        "--property",
        help="GA4 property ID (numerico, sem 'properties/'). Padrao: GA4_PROPERTY_ID"
    )


def add_date_args(parser):
    """Adiciona argumentos de data ao parser."""
    parser.add_argument(
        "--date-range",
        default="30daysAgo",
        help="Periodo relativo: 7daysAgo, 14daysAgo, 30daysAgo, 90daysAgo, 365daysAgo (default: 30daysAgo)"
    )
    parser.add_argument("--start-date", help="Data inicio (YYYY-MM-DD ou NdaysAgo)")
    parser.add_argument("--end-date", help="Data fim (YYYY-MM-DD ou 'today')")


def add_limit_arg(parser, default=25):
    """Adiciona argumento --limit ao parser."""
    parser.add_argument("--limit", type=int, default=default, help=f"Limite de resultados (default: {default})")


def build_date_range(args):
    """Constroi DateRange a partir dos argumentos."""
    from google.analytics.data_v1beta.types import DateRange

    if args.start_date:
        end = args.end_date or "today"
        return DateRange(start_date=args.start_date, end_date=end)

    return DateRange(start_date=args.date_range, end_date="today")
