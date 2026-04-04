#!/usr/bin/env python3
"""
GA4 Ratos - Relatorios (core da skill)
Subcomandos: overview, traffic-sources, landing-pages, campaigns, conversions,
             devices, geo, daily, custom
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import (
    init_client,
    resolve_property_id,
    add_property_arg,
    add_date_args,
    add_limit_arg,
    build_date_range,
    format_report_response,
    print_json,
    print_error,
    handle_ga4_error,
)

from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    OrderBy,
    RunReportRequest,
)


def _run_report(property_id, dimensions, metrics, date_range, limit=25, order_bys=None):
    """Helper generico para rodar um RunReportRequest."""
    client = init_client()

    request_params = {
        "property": f"properties/{property_id}",
        "dimensions": [Dimension(name=d) for d in dimensions],
        "metrics": [Metric(name=m) for m in metrics],
        "date_ranges": [date_range],
        "limit": limit,
    }

    if order_bys:
        request_params["order_bys"] = order_bys

    request = RunReportRequest(**request_params)
    response = client.run_report(request)
    return format_report_response(response)


# ---------------------------------------------------------------------------
# overview — Resumo geral
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_overview(args):
    """Resumo geral: sessoes, usuarios, pageviews, bounce rate, conversoes."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=[],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "screenPageViews",
            "bounceRate",
            "averageSessionDuration",
            "eventCount",
            "conversions",
        ],
        date_range=date_range,
        limit=1,
    )

    print_json(result)


# ---------------------------------------------------------------------------
# traffic-sources — Fontes de trafego
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_traffic_sources(args):
    """Fontes de trafego (source/medium) com metricas."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=["sessionSource", "sessionMedium"],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "bounceRate",
            "averageSessionDuration",
            "screenPageViews",
            "conversions",
        ],
        date_range=date_range,
        limit=args.limit,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# landing-pages — Paginas de destino
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_landing_pages(args):
    """Paginas de destino com bounce rate e conversoes."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=["landingPage"],
        metrics=[
            "sessions",
            "totalUsers",
            "bounceRate",
            "averageSessionDuration",
            "screenPageViews",
            "conversions",
        ],
        date_range=date_range,
        limit=args.limit,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# campaigns — Performance de campanhas UTM
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_campaigns(args):
    """Performance de campanhas UTM (source, medium, campaign)."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=["sessionSource", "sessionMedium", "sessionCampaignName"],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "bounceRate",
            "averageSessionDuration",
            "conversions",
        ],
        date_range=date_range,
        limit=args.limit,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# conversions — Eventos de conversao
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_conversions(args):
    """Eventos de conversao com contagem e valor."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=["eventName"],
        metrics=[
            "conversions",
            "eventCount",
            "eventValue",
            "totalUsers",
        ],
        date_range=date_range,
        limit=args.limit,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="conversions"), desc=True)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# devices — Breakdown por dispositivo
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_devices(args):
    """Breakdown por dispositivo (desktop, mobile, tablet)."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=["deviceCategory"],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "bounceRate",
            "averageSessionDuration",
            "screenPageViews",
            "conversions",
        ],
        date_range=date_range,
        limit=10,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# geo — Breakdown por pais/cidade
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_geo(args):
    """Breakdown por pais/cidade."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    dimensions = ["country", "city"] if not args.country_only else ["country"]

    result = _run_report(
        property_id,
        dimensions=dimensions,
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "bounceRate",
            "conversions",
        ],
        date_range=date_range,
        limit=args.limit,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# daily — Evolucao diaria
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_daily(args):
    """Evolucao diaria de metricas."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    result = _run_report(
        property_id,
        dimensions=["date"],
        metrics=[
            "sessions",
            "totalUsers",
            "newUsers",
            "screenPageViews",
            "bounceRate",
            "averageSessionDuration",
            "conversions",
        ],
        date_range=date_range,
        limit=366,
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"), desc=False)],
    )

    print_json(result)


# ---------------------------------------------------------------------------
# custom — Query custom
# ---------------------------------------------------------------------------

@handle_ga4_error
def cmd_custom(args):
    """Query custom com metricas e dimensoes livres."""
    property_id = resolve_property_id(args.property)
    date_range = build_date_range(args)

    if not args.metrics:
        print_error("--metrics e obrigatorio. Ex: --metrics sessions,totalUsers")
        sys.exit(1)

    metrics = [m.strip() for m in args.metrics.split(",")]
    dimensions = [d.strip() for d in args.dimensions.split(",")] if args.dimensions else []

    order_bys = None
    if args.order_by:
        desc = args.order_by.startswith("-")
        metric_name = args.order_by.lstrip("-")
        order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=metric_name), desc=desc)]

    result = _run_report(
        property_id,
        dimensions=dimensions,
        metrics=metrics,
        date_range=date_range,
        limit=args.limit,
        order_bys=order_bys,
    )

    print_json(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GA4 Ratos - Relatorios")
    sub = parser.add_subparsers(dest="command")

    # overview
    p_overview = sub.add_parser("overview", help="Resumo geral")
    add_property_arg(p_overview)
    add_date_args(p_overview)

    # traffic-sources
    p_traffic = sub.add_parser("traffic-sources", help="Fontes de trafego")
    add_property_arg(p_traffic)
    add_date_args(p_traffic)
    add_limit_arg(p_traffic)

    # landing-pages
    p_landing = sub.add_parser("landing-pages", help="Paginas de destino")
    add_property_arg(p_landing)
    add_date_args(p_landing)
    add_limit_arg(p_landing)

    # campaigns
    p_campaigns = sub.add_parser("campaigns", help="Performance de campanhas UTM")
    add_property_arg(p_campaigns)
    add_date_args(p_campaigns)
    add_limit_arg(p_campaigns)

    # conversions
    p_conversions = sub.add_parser("conversions", help="Eventos de conversao")
    add_property_arg(p_conversions)
    add_date_args(p_conversions)
    add_limit_arg(p_conversions)

    # devices
    p_devices = sub.add_parser("devices", help="Breakdown por dispositivo")
    add_property_arg(p_devices)
    add_date_args(p_devices)

    # geo
    p_geo = sub.add_parser("geo", help="Breakdown por pais/cidade")
    add_property_arg(p_geo)
    add_date_args(p_geo)
    add_limit_arg(p_geo)
    p_geo.add_argument("--country-only", action="store_true", help="Mostrar somente pais (sem cidade)")

    # daily
    p_daily = sub.add_parser("daily", help="Evolucao diaria de metricas")
    add_property_arg(p_daily)
    add_date_args(p_daily)

    # custom
    p_custom = sub.add_parser("custom", help="Query custom")
    add_property_arg(p_custom)
    add_date_args(p_custom)
    add_limit_arg(p_custom, default=50)
    p_custom.add_argument("--dimensions", help="Dimensoes separadas por virgula (ex: date,sessionSource)")
    p_custom.add_argument("--metrics", help="Metricas separadas por virgula (ex: sessions,totalUsers)")
    p_custom.add_argument("--order-by", help="Ordenar por metrica (prefixo - para desc, ex: -sessions)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "overview": cmd_overview,
        "traffic-sources": cmd_traffic_sources,
        "landing-pages": cmd_landing_pages,
        "campaigns": cmd_campaigns,
        "conversions": cmd_conversions,
        "devices": cmd_devices,
        "geo": cmd_geo,
        "daily": cmd_daily,
        "custom": cmd_custom,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
