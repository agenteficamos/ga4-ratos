#!/usr/bin/env python3
"""
GA4 Ratos - Dados em tempo real
Subcomandos: now, events
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import (
    init_client,
    resolve_property_id,
    add_property_arg,
    format_realtime_response,
    print_json,
    print_error,
    handle_ga4_error,
)

from google.analytics.data_v1beta.types import (
    Dimension,
    Metric,
    MinuteRange,
    RunRealtimeReportRequest,
)


def _run_realtime_report(property_id, dimensions, metrics, minute_ranges=None):
    """Helper generico para rodar um RunRealtimeReportRequest."""
    client = init_client()

    request_params = {
        "property": f"properties/{property_id}",
        "dimensions": [Dimension(name=d) for d in dimensions],
        "metrics": [Metric(name=m) for m in metrics],
    }

    if minute_ranges:
        request_params["minute_ranges"] = minute_ranges

    request = RunRealtimeReportRequest(**request_params)
    response = client.run_realtime_report(request)
    return format_realtime_response(response)


# ---------------------------------------------------------------------------
# now — Usuarios ativos agora
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_now(args):
    """Usuarios ativos agora, paginas sendo vistas, fontes."""
    property_id = resolve_property_id(args.property)
    client = init_client()

    # 1. Total de usuarios ativos
    req_total = RunRealtimeReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
    )
    resp_total = client.run_realtime_report(req_total)
    total_users = 0
    if resp_total.rows:
        total_users = resp_total.rows[0].metric_values[0].value

    # 2. Por pagina
    pages = _run_realtime_report(
        property_id,
        dimensions=["unifiedScreenName"],
        metrics=["activeUsers"],
    )

    # 3. Por fonte
    sources = _run_realtime_report(
        property_id,
        dimensions=["source"],
        metrics=["activeUsers"],
    )

    # 4. Por dispositivo
    devices = _run_realtime_report(
        property_id,
        dimensions=["deviceCategory"],
        metrics=["activeUsers"],
    )

    # 5. Por pais
    countries = _run_realtime_report(
        property_id,
        dimensions=["country"],
        metrics=["activeUsers"],
    )

    result = {
        "active_users_now": total_users,
        "pages": pages["rows"],
        "sources": sources["rows"],
        "devices": devices["rows"],
        "countries": countries["rows"],
    }

    print_json(result)


# ---------------------------------------------------------------------------
# events — Eventos em tempo real
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_events(args):
    """Eventos em tempo real."""
    property_id = resolve_property_id(args.property)

    result = _run_realtime_report(
        property_id,
        dimensions=["eventName"],
        metrics=["eventCount", "activeUsers"],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GA4 Ratos - Tempo Real")
    sub = parser.add_subparsers(dest="command")

    # now
    p_now = sub.add_parser("now", help="Usuarios ativos agora")
    add_property_arg(p_now)

    # events
    p_events = sub.add_parser("events", help="Eventos em tempo real")
    add_property_arg(p_events)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "now": cmd_now,
        "events": cmd_events,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
