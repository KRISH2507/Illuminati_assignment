"""Schema metadata for LLM context and agent tools."""

from __future__ import annotations

TABLES: dict[str, str] = {
    "store_master": "Store locations, cities, regions, and performance attributes.",
    "product_master": "Menu SKUs, categories, and base pricing.",
    "customer_master": "Customer segments and home cities.",
    "promotions": "Promotion definitions, discount rules, and validity.",
    "calendar": "Date dimension with weekday/weekend and festive period flags.",
    "orders": "Order header facts: revenue, channel, store, customer, promo.",
    "order_details": "Order line items with SKU quantities and line values.",
    "glossary": "Column descriptions and table relationships.",
    "v_orders_enriched": "Orders joined with store and calendar attributes.",
    "v_order_lines": "Order lines joined with product, order, and store context.",
}

RELATIONSHIPS: list[str] = [
    "orders.store_id → store_master.store_id",
    "orders.customer_id → customer_master.customer_id",
    "orders.promo_id → promotions.promo_id",
    "order_details.order_id → orders.order_id",
    "order_details.sku_id → product_master.sku_id",
    "CAST(orders.order_datetime AS DATE) → calendar.date",
]

METRICS: dict[str, str] = {
    "revenue": "SUM(net_revenue) from orders (final billed value including tax).",
    "orders": "COUNT(DISTINCT order_id) from orders.",
    "average_order_value": "AVG(net_revenue) or SUM(net_revenue) / COUNT(DISTINCT order_id).",
    "quantity_sold": "SUM(quantity) from order_details.",
    "line_revenue": "SUM(line_net_value) from order_details.",
    "last_3_months": "Filter where order_datetime >= (max order date - 3 months).",
    "weekend": "calendar.day_type = 'Weekend'.",
    "weekday": "calendar.day_type = 'Weekday'.",
    "festive_period": "calendar.festive_period != 'Normal' (Pujo, Diwali, New Year).",
    "normal_period": "calendar.festive_period = 'Normal'.",
}

VIEW_SQL_HINTS: dict[str, str] = {
    "v_orders_enriched": (
        "Use for store/city/channel/calendar questions. "
        "Columns include net_revenue, channel, city, region, day_type, festive_period."
    ),
    "v_order_lines": (
        "Use for SKU/category quantity and line revenue questions. "
        "Columns include sku_name, category, quantity, line_net_value, city, channel."
    ),
}


def get_schema_text() -> str:
    """Return schema documentation as plain text for LLM prompts."""
    lines = ["# QuickBite QSR Database Schema", ""]

    lines.append("## Tables and views")
    for name, description in TABLES.items():
        lines.append(f"- **{name}**: {description}")

    lines.append("")
    lines.append("## Relationships")
    for rel in RELATIONSHIPS:
        lines.append(f"- {rel}")

    lines.append("")
    lines.append("## Metric definitions")
    for name, definition in METRICS.items():
        lines.append(f"- **{name}**: {definition}")

    lines.append("")
    lines.append("## View usage hints")
    for name, hint in VIEW_SQL_HINTS.items():
        lines.append(f"- **{name}**: {hint}")

    lines.append("")
    lines.append("## Key columns")
    lines.extend(
        [
            "- orders.net_revenue — primary revenue metric",
            "- orders.channel — Dine-in, Takeaway, Swiggy, Zomato",
            "- calendar.day_type — Weekday or Weekend",
            "- calendar.festive_period — Normal, Pujo, Diwali, New Year",
            "- store_master.city — city for store-level and city-level analysis",
        ]
    )

    return "\n".join(lines)
