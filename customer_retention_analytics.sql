-- ============================================================================
-- PROJECT 2: CUSTOMER RETENTION ANALYTICS — PRODUCTION SQL SUITE
-- Dialect: PostgreSQL / T-SQL / SQLite Compatible
-- Dataset: 1,050,000 Customer Transaction Records across 45,000 Accounts
-- ============================================================================

-- 1. Multi-Stage CTE: Transaction Aggregation & RFM Behavioral Scoring
WITH tx_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS tx_frequency,
        ROUND(SUM(tx_amount), 2) AS total_monetary_spend,
        MIN(days_since_tx) AS recency_days,
        SUM(is_failed) AS failed_payments,
        SUM(is_expansion) AS expansion_events
    FROM transactions
    GROUP BY customer_id
),
rfm_percentiles AS (
    SELECT
        c.customer_id,
        c.segment,
        c.contract_type,
        c.cohort_year,
        c.cohort_quarter,
        c.tenure_months,
        c.autopay_enabled,
        c.onboarding_completed,
        c.support_tickets_90d,
        c.nps_score,
        c.feature_adoption_pct,
        c.monthly_recurring_revenue,
        c.is_churned,
        COALESCE(t.tx_frequency, 0) AS tx_frequency,
        COALESCE(t.total_monetary_spend, 0.0) AS total_monetary_spend,
        COALESCE(t.recency_days, 365) AS recency_days,
        COALESCE(t.failed_payments, 0) AS failed_payments,
        COALESCE(t.expansion_events, 0) AS expansion_events,
        NTILE(5) OVER (ORDER BY COALESCE(t.recency_days, 365) DESC) AS r_score,
        NTILE(5) OVER (ORDER BY COALESCE(t.tx_frequency, 0) ASC) AS f_score,
        NTILE(5) OVER (ORDER BY COALESCE(t.total_monetary_spend, 0.0) ASC) AS m_score
    FROM customers c
    LEFT JOIN tx_summary t ON c.customer_id = t.customer_id
),
rfm_segmented AS (
    SELECT
        *,
        CASE
            WHEN is_churned = 1 THEN 'Churned'
            WHEN contract_type = 'Month-to-Month' AND (feature_adoption_pct < 55 OR support_tickets_90d >= 3) THEN 'High-Risk At-Risk'
            WHEN feature_adoption_pct >= 75 AND expansion_events >= 2 THEN 'Champions & Loyalists'
            WHEN feature_adoption_pct >= 60 THEN 'Core Active'
            ELSE 'Needs Nurture'
        END AS rfm_retention_segment
    FROM rfm_percentiles
)
SELECT
    rfm_retention_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(monthly_recurring_revenue), 2) AS avg_mrr,
    ROUND(SUM(monthly_recurring_revenue) * 12.0, 2) AS annualized_arr,
    ROUND(AVG(feature_adoption_pct), 1) AS avg_adoption_pct,
    ROUND(AVG(support_tickets_90d), 2) AS avg_tickets_90d,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(total_monetary_spend), 2) AS avg_lifetime_spend
FROM rfm_segmented
GROUP BY rfm_retention_segment
ORDER BY annualized_arr DESC;

-- 2. Churn Driver Attribution by Contract Structure, Onboarding & Support Friction
SELECT
    contract_type,
    CASE WHEN onboarding_completed = 1 THEN 'Completed' ELSE 'Incomplete' END AS onboarding_status,
    CASE WHEN support_tickets_90d >= 3 THEN '3+ Tickets (High Friction)' ELSE '0-2 Tickets (Normal)' END AS support_tier,
    COUNT(*) AS total_accounts,
    SUM(is_churned) AS churned_accounts,
    ROUND(AVG(is_churned) * 100.0, 2) AS churn_rate_pct,
    ROUND(SUM(monthly_recurring_revenue * 12.0), 2) AS total_segment_arr,
    ROUND(SUM(CASE WHEN is_churned = 1 THEN monthly_recurring_revenue * 12.0 ELSE 0 END), 2) AS churned_arr_loss
FROM customers
GROUP BY contract_type, onboarding_status, support_tier
ORDER BY churn_rate_pct DESC;

-- 3. Cohort Survival & Tenure Retention Curve Analysis
SELECT
    cohort_year,
    cohort_quarter,
    COUNT(*) AS cohort_size,
    ROUND(AVG(CASE WHEN tenure_months >= 3 OR is_churned = 0 THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS m3_retention_pct,
    ROUND(AVG(CASE WHEN tenure_months >= 6 OR is_churned = 0 THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS m6_retention_pct,
    ROUND(AVG(CASE WHEN tenure_months >= 12 OR is_churned = 0 THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS m12_retention_pct,
    ROUND(AVG(1.0 - is_churned) * 100.0, 2) AS net_logo_retention_pct
FROM customers
GROUP BY cohort_year, cohort_quarter
ORDER BY cohort_year, cohort_quarter;
