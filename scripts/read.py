#!/usr/bin/env python3
"""
GA4 Ratos - Leitura de propriedades e contas
Subcomandos: properties, account
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import (
    init_client,
    resolve_property_id,
    add_property_arg,
    print_json,
    print_error,
    handle_ga4_error,
)


# ---------------------------------------------------------------------------
# properties — Lista propriedades GA4 acessiveis
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_properties(args):
    """Lista propriedades GA4 acessiveis pela conta autenticada.
    Usa a Admin API (google-analytics-admin) se disponivel,
    senao tenta acessar a propriedade do .env como fallback.
    """
    try:
        from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
        from lib import _load_env_file, _load_google_ads_env

        _load_env_file()

        # Tenta inicializar admin client com as mesmas credenciais
        creds_path = os.environ.get("GA4_CREDENTIALS_PATH")
        if creds_path and os.path.isfile(creds_path):
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )
            admin_client = AnalyticsAdminServiceClient(credentials=credentials)
        else:
            admin_client = AnalyticsAdminServiceClient()

        accounts = []
        for account in admin_client.list_account_summaries():
            for prop in account.property_summaries:
                accounts.append({
                    "account": account.display_name,
                    "account_id": account.name,
                    "property_name": prop.display_name,
                    "property_id": prop.property.replace("properties/", ""),
                })

        print_json({"properties": accounts, "total": len(accounts)})

    except ImportError:
        print_error(
            "Para listar propriedades, instale: pip3 install google-analytics-admin\n"
            "  Alternativa: use 'read.py account --property ID' para verificar acesso a uma propriedade especifica."
        )
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro ao listar propriedades: {e}")
        print_error(
            "Alternativa: use 'read.py account --property ID' para verificar acesso a uma propriedade especifica."
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# account — Detalhes de uma propriedade
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_account(args):
    """Mostra detalhes de uma propriedade GA4 (faz um report minimo para validar acesso)."""
    from google.analytics.data_v1beta.types import (
        DateRange, Metric, RunReportRequest,
    )

    property_id = resolve_property_id(args.property)
    client = init_client()

    # Faz um report minimo para validar acesso e pegar metadata
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="1daysAgo", end_date="today")],
    )
    response = client.run_report(request)

    # Tenta pegar metadata via Admin API
    property_info = {"property_id": property_id, "status": "acessivel"}

    try:
        from google.analytics.admin_v1beta import AnalyticsAdminServiceClient

        creds_path = os.environ.get("GA4_CREDENTIALS_PATH")
        if creds_path and os.path.isfile(creds_path):
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )
            admin_client = AnalyticsAdminServiceClient(credentials=credentials)
        else:
            admin_client = AnalyticsAdminServiceClient()

        prop = admin_client.get_property(name=f"properties/{property_id}")
        property_info.update({
            "display_name": prop.display_name,
            "time_zone": prop.time_zone,
            "currency_code": prop.currency_code,
            "industry_category": str(prop.industry_category) if prop.industry_category else None,
            "create_time": str(prop.create_time),
            "service_level": str(prop.service_level) if prop.service_level else None,
        })
    except ImportError:
        property_info["note"] = "Instale google-analytics-admin para mais detalhes"
    except Exception:
        property_info["note"] = "Propriedade acessivel mas metadata nao disponivel via Admin API"

    # Adiciona usuarios ativos como prova de acesso
    if response.rows:
        property_info["active_users_today"] = response.rows[0].metric_values[0].value

    print_json(property_info)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GA4 Ratos - Leitura")
    sub = parser.add_subparsers(dest="command")

    # properties
    p_props = sub.add_parser("properties", help="Lista propriedades GA4 acessiveis")

    # account
    p_account = sub.add_parser("account", help="Detalhes de uma propriedade")
    add_property_arg(p_account)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "properties": cmd_properties,
        "account": cmd_account,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
