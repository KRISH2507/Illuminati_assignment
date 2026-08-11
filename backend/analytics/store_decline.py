"""Store decline diagnostics for Q8."""

from __future__ import annotations

import json

from backend.data.db import run_query


def analyze_declining_stores() -> list[dict]:
    """
    Identify stores with consistent month-over-month revenue decline
    in the last 3 months and attach likely drivers.
    """
    declining = run_query(
        """
        WITH bounds AS (
            SELECT MAX(CAST(order_datetime AS DATE)) AS max_date FROM orders
        ),
        monthly AS (
            SELECT
                o.store_id,
                o.store_name,
                o.city,
                DATE_TRUNC('month', CAST(o.order_datetime AS TIMESTAMP)) AS month,
                ROUND(SUM(o.net_revenue), 2) AS revenue,
                COUNT(*) AS orders,
                ROUND(AVG(o.net_revenue), 2) AS avg_order_value
            FROM v_orders_enriched o
            CROSS JOIN bounds b
            WHERE CAST(o.order_datetime AS DATE) > b.max_date - INTERVAL '3 months'
            GROUP BY
                o.store_id,
                o.store_name,
                o.city,
                DATE_TRUNC('month', CAST(o.order_datetime AS TIMESTAMP))
        ),
        flagged AS (
            SELECT
                *,
                LAG(revenue) OVER (PARTITION BY store_id ORDER BY month) AS prev_revenue
            FROM monthly
        ),
        store_summary AS (
            SELECT
                store_id,
                store_name,
                city,
                COUNT(*) AS months_in_window,
                SUM(CASE WHEN prev_revenue IS NOT NULL AND revenue < prev_revenue THEN 1 ELSE 0 END) AS declining_months,
                MIN(revenue) AS min_monthly_revenue,
                MAX(revenue) AS max_monthly_revenue,
                ROUND(SUM(revenue), 2) AS total_revenue,
                SUM(orders) AS total_orders,
                ROUND(AVG(avg_order_value), 2) AS avg_order_value
            FROM flagged
            GROUP BY store_id, store_name, city
        )
        SELECT *
        FROM store_summary
        WHERE declining_months >= 2
        ORDER BY declining_months DESC, total_revenue ASC
        """
    )

    if not declining:
        return []

    store_ids = ", ".join(f"'{row['store_id']}'" for row in declining)

    channel_shift = run_query(
        f"""
        WITH bounds AS (
            SELECT MAX(CAST(order_datetime AS DATE)) AS max_date FROM orders
        ),
        windowed AS (
            SELECT
                o.store_id,
                o.channel,
                CASE
                    WHEN CAST(o.order_datetime AS DATE) > b.max_date - INTERVAL '3 months'
                    THEN 'recent'
                    ELSE 'earlier'
                END AS period,
                SUM(o.net_revenue) AS revenue,
                COUNT(*) AS orders
            FROM v_orders_enriched o
            CROSS JOIN bounds b
            WHERE o.store_id IN ({store_ids})
              AND CAST(o.order_datetime AS DATE) > b.max_date - INTERVAL '6 months'
            GROUP BY o.store_id, o.channel, period
        )
        SELECT * FROM windowed
        ORDER BY store_id, period, revenue DESC
        """
    )

    promo_usage = run_query(
        f"""
        WITH bounds AS (
            SELECT MAX(CAST(order_datetime AS DATE)) AS max_date FROM orders
        )
        SELECT
            o.store_id,
            COUNT(*) AS orders,
            SUM(CASE WHEN o.promo_id IS NOT NULL AND o.promo_id != '' THEN 1 ELSE 0 END) AS promo_orders,
            ROUND(
                100.0 * SUM(CASE WHEN o.promo_id IS NOT NULL AND o.promo_id != '' THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) AS promo_order_pct,
            ROUND(AVG(o.discount_amount), 2) AS avg_discount
        FROM v_orders_enriched o
        CROSS JOIN bounds b
        WHERE o.store_id IN ({store_ids})
          AND CAST(o.order_datetime AS DATE) > b.max_date - INTERVAL '3 months'
        GROUP BY o.store_id
        """
    )

    performance = run_query(
        f"""
        SELECT store_id, performance_factor, store_format, city_price_index
        FROM store_master
        WHERE store_id IN ({store_ids})
        """
    )

    channel_by_store: dict[str, list[dict]] = {}
    for row in channel_shift:
        channel_by_store.setdefault(row["store_id"], []).append(row)

    promo_by_store = {row["store_id"]: row for row in promo_usage}
    perf_by_store = {row["store_id"]: row for row in performance}

    enriched: list[dict] = []
    for store in declining:
        store_id = store["store_id"]
        channels = channel_by_store.get(store_id, [])
        promo = promo_by_store.get(store_id, {})
        perf = perf_by_store.get(store_id, {})

        recent_channels = [c for c in channels if c["period"] == "recent"]
        earlier_channels = [c for c in channels if c["period"] == "earlier"]
        top_recent = recent_channels[0]["channel"] if recent_channels else None
        top_earlier = earlier_channels[0]["channel"] if earlier_channels else None

        reasons = []
        if store["declining_months"] >= 2:
            reasons.append(f"Revenue fell in {store['declining_months']} of the last 3 months.")
        if top_recent and top_earlier and top_recent != top_earlier:
            reasons.append(
                f"Leading channel shifted from {top_earlier} to {top_recent} in the recent window."
            )
        if promo.get("promo_order_pct", 0) < 15:
            reasons.append("Low promo usage may indicate weaker demand or fewer deal-driven orders.")
        if perf.get("performance_factor", 1) < 1:
            reasons.append(
                f"Store has a below-baseline performance factor ({perf.get('performance_factor')})."
            )
        if store["avg_order_value"] and store["total_orders"]:
            reasons.append(
                f"Recent AOV is INR {store['avg_order_value']} across {store['total_orders']} orders."
            )

        enriched.append(
            {
                **store,
                "top_recent_channel": top_recent,
                "top_earlier_channel": top_earlier,
                "promo_order_pct": promo.get("promo_order_pct"),
                "avg_discount": promo.get("avg_discount"),
                "performance_factor": perf.get("performance_factor"),
                "store_format": perf.get("store_format"),
                "key_reasons": reasons,
                "channel_detail": channels,
            }
        )

    return enriched


def analyze_declining_stores_json() -> str:
    return json.dumps(analyze_declining_stores(), default=str, indent=2)
