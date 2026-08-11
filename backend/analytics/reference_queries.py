"""Canonical analytics questions and reference SQL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from backend.data.db import run_query


@dataclass(frozen=True)
class ReferenceQuestion:
    id: str
    question: str
    description: str
    run: Callable[[], list[dict]]


def _q1_last_3_months_kpis() -> list[dict]:
    return run_query(
        """
        WITH bounds AS (
            SELECT MAX(CAST(order_datetime AS DATE)) AS max_date FROM orders
        )
        SELECT
            COUNT(*) AS orders,
            ROUND(SUM(net_revenue), 2) AS total_revenue,
            ROUND(AVG(net_revenue), 2) AS avg_order_value
        FROM orders o
        CROSS JOIN bounds b
        WHERE CAST(o.order_datetime AS DATE) > b.max_date - INTERVAL '3 months'
        """
    )


def _q2_top_bottom_stores() -> list[dict]:
    return run_query(
        """
        WITH store_rev AS (
            SELECT
                store_id,
                store_name,
                city,
                ROUND(SUM(net_revenue), 2) AS revenue
            FROM v_orders_enriched
            GROUP BY store_id, store_name, city
        ),
        top5 AS (
            SELECT 'top' AS rank_type, store_id, store_name, city, revenue
            FROM store_rev
            ORDER BY revenue DESC
            LIMIT 5
        ),
        bottom5 AS (
            SELECT 'bottom' AS rank_type, store_id, store_name, city, revenue
            FROM store_rev
            ORDER BY revenue ASC
            LIMIT 5
        )
        SELECT * FROM top5
        UNION ALL
        SELECT * FROM bottom5
        ORDER BY rank_type DESC, revenue DESC
        """
    )


def _q3_channel_performance() -> list[dict]:
    return run_query(
        """
        SELECT
            channel,
            COUNT(*) AS orders,
            ROUND(SUM(net_revenue), 2) AS revenue,
            ROUND(AVG(net_revenue), 2) AS avg_order_value
        FROM orders
        GROUP BY channel
        ORDER BY revenue DESC
        """
    )


def _q4_top_skus() -> list[dict]:
    return run_query(
        """
        SELECT
            sku_id,
            sku_name,
            category,
            SUM(quantity) AS total_quantity,
            ROUND(SUM(line_net_value), 2) AS total_revenue
        FROM v_order_lines
        GROUP BY sku_id, sku_name, category
        ORDER BY total_quantity DESC, total_revenue DESC
        LIMIT 5
        """
    )


def _q5_cities_revenue_decline() -> list[dict]:
    return run_query(
        """
        WITH bounds AS (
            SELECT MAX(CAST(order_datetime AS DATE)) AS max_date FROM orders
        ),
        city_periods AS (
            SELECT
                city,
                ROUND(CAST(SUM(
                    CASE
                        WHEN CAST(order_datetime AS DATE) > b.max_date - INTERVAL '3 months'
                        THEN net_revenue ELSE 0
                    END
                ) AS NUMERIC), 2) AS recent_revenue,
                ROUND(CAST(SUM(
                    CASE
                        WHEN CAST(order_datetime AS DATE) <= b.max_date - INTERVAL '3 months'
                         AND CAST(order_datetime AS DATE) > b.max_date - INTERVAL '6 months'
                        THEN net_revenue ELSE 0
                    END
                ) AS NUMERIC), 2) AS prior_revenue
            FROM v_orders_enriched
            CROSS JOIN bounds b
            GROUP BY city
        )
        SELECT
            city,
            recent_revenue,
            prior_revenue,
            ROUND(CAST(recent_revenue - prior_revenue AS NUMERIC), 2) AS revenue_change,
            ROUND(CAST(100.0 * (recent_revenue - prior_revenue) / NULLIF(prior_revenue, 0) AS NUMERIC), 2) AS pct_change
        FROM city_periods
        WHERE recent_revenue < prior_revenue
        ORDER BY revenue_change ASC
        """
    )


def _q6_weekend_vs_weekday() -> list[dict]:
    return run_query(
        """
        SELECT
            day_type,
            COUNT(*) AS orders,
            ROUND(SUM(net_revenue), 2) AS revenue,
            ROUND(AVG(net_revenue), 2) AS avg_order_value
        FROM v_orders_enriched
        GROUP BY day_type
        ORDER BY day_type
        """
    )


def _q7_festive_vs_normal() -> list[dict]:
    return run_query(
        """
        SELECT
            CASE WHEN festive_period = 'Normal' THEN 'Normal' ELSE 'Festive' END AS period_type,
            COUNT(*) AS orders,
            ROUND(SUM(net_revenue), 2) AS revenue,
            ROUND(AVG(net_revenue), 2) AS avg_order_value
        FROM v_orders_enriched
        GROUP BY period_type
        ORDER BY period_type
        """
    )


REFERENCE_QUESTIONS: list[ReferenceQuestion] = [
    ReferenceQuestion(
        id="q1",
        question="What were the total revenue, orders, and average order value for the last 3 months?",
        description="Last 3 months KPI summary",
        run=_q1_last_3_months_kpis,
    ),
    ReferenceQuestion(
        id="q2",
        question="Which are the top 5 and bottom 5 stores by revenue?",
        description="Store revenue rankings",
        run=_q2_top_bottom_stores,
    ),
    ReferenceQuestion(
        id="q3",
        question="How does revenue and average order value vary across different channels?",
        description="Channel mix and AOV",
        run=_q3_channel_performance,
    ),
    ReferenceQuestion(
        id="q4",
        question="Which are the top 5 SKUs by quantity sold and revenue?",
        description="SKU ranking",
        run=_q4_top_skus,
    ),
    ReferenceQuestion(
        id="q5",
        question="Which cities have shown a decline in revenue over the last 3 months?",
        description="City-level recent vs prior 3-month decline",
        run=_q5_cities_revenue_decline,
    ),
    ReferenceQuestion(
        id="q6",
        question="How does weekend performance compare with weekdays?",
        description="Weekend vs weekday comparison",
        run=_q6_weekend_vs_weekday,
    ),
    ReferenceQuestion(
        id="q7",
        question="How does festive-period performance compare with normal periods?",
        description="Festive vs normal period comparison",
        run=_q7_festive_vs_normal,
    ),
]


def get_example_questions() -> list[dict[str, str]]:
    return [
        {
            "id": item.id,
            "question": item.question,
            "description": item.description,
        }
        for item in REFERENCE_QUESTIONS
    ]


def get_store_decline_question() -> dict[str, str]:
    return {
        "id": "q8",
        "question": "Which stores have consistently declined in the last 3 months, and what are the key reasons?",
        "description": "Multi-month store decline with channel/order/AOV diagnostics",
    }
