#!/usr/bin/env python3
"""
Build End-to-End Analytics Portfolio Projects for Dolma Sherpa:
1. Financial Forecasting & Revenue Analysis (Python, Power BI)
2. Customer Retention Analytics (SQL, Python, Power BI)
3. Statistical Analysis & Predictive Modeling (Python, SQL, R)

Executes real data generation, SQLite query pipelines, statistical & predictive models,
exports production scripts, cleaned CSV datasets, DAX/Power BI specs, and generates
publication-grade charts & Power BI dashboard mockups.
"""

import os
import json
import sqlite3
import zipfile
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker

# Set global random seed for 100% reproducibility
np.random.seed(42)

BASE_DIR = "/working_dir/c_b3c497e8c8f7cde4"
INTERMEDIATE_DIR = os.path.join(BASE_DIR, "artifacts/file_generation/ttl=63d/intermediate")
OUTPUT_DIR = os.path.join(BASE_DIR, "artifacts/file_generation/ttl=63d/output")
PORTFOLIO_ROOT = os.path.join(INTERMEDIATE_DIR, "Dolma_Sherpa_Analytics_Portfolio")

os.makedirs(INTERMEDIATE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PORTFOLIO_ROOT, exist_ok=True)

# Clean styling for matplotlib
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

metrics_summary = {}

print("=================================================================")
print("PROJECT 1: FINANCIAL FORECASTING & REVENUE ANALYSIS (Python, Power BI)")
print("=================================================================")

p1_dir = os.path.join(PORTFOLIO_ROOT, "01_Financial_Forecasting_Revenue_Analysis")
os.makedirs(p1_dir, exist_ok=True)

# 1. Generate 7 years of monthly financial data (Jan 2019 - Dec 2025: 84 months)
# Across 4 business segments (Enterprise SaaS, Mid-Market, SMB, Commercial Services)
# and 3 Regions (West, Central, East) -> 84 * 4 * 3 = 1,008 monthly segment records
dates = pd.date_range(start="2019-01-01", end="2025-12-01", freq="MS")
segments = [
    ("Enterprise", 0.45, 0.78, 0.012),
    ("Mid-Market", 0.30, 0.72, 0.010),
    ("SMB", 0.15, 0.65, 0.007),
    ("Commercial Services", 0.10, 0.58, 0.008)
]
regions = [("West", 0.42), ("East", 0.35), ("Central", 0.23)]

rows_p1 = []
for t_idx, d in enumerate(dates):
    month = d.month
    year = d.year
    # Seasonal factor: Q4 peak (Nov/Dec), Q1 dip (Jan/Feb), Q2/Q3 steady
    seasonal = 1.0 + 0.14 * np.sin(2 * np.pi * (month - 3) / 12.0) + (0.11 if month == 12 else (-0.06 if month == 1 else 0.0))
    # Macro indicator (e.g., PMI / Business Confidence Index)
    macro_index = 100 + 4.5 * np.sin(2 * np.pi * t_idx / 36.0) - (8.0 if (year == 2020 and month in [3,4,5]) else 0.0)
    
    for seg_name, seg_share, base_gm, growth_rate in segments:
        for reg_name, reg_share in regions:
            base_rev = 2850000 * seg_share * reg_share
            trend = (1.0 + growth_rate) ** t_idx
            macro_effect = (macro_index / 100.0) ** 0.65
            noise = np.random.normal(1.0, 0.028)
            
            actual_rev = base_rev * trend * seasonal * macro_effect * noise
            # Budget was set at prior year end with simpler linear growth + average seasonality
            budget_seasonal = 1.0 + 0.10 * np.sin(2 * np.pi * (month - 3) / 12.0)
            budget_rev = base_rev * ((1.0 + growth_rate * 0.95) ** t_idx) * budget_seasonal
            
            cogs = actual_rev * (1.0 - base_gm + np.random.normal(0, 0.008))
            gross_profit = actual_rev - cogs
            opex_rd = actual_rev * (0.14 - 0.0003 * t_idx + np.random.normal(0, 0.004))
            opex_sm = actual_rev * (0.22 - 0.0004 * t_idx + np.random.normal(0, 0.006))
            opex_ga = actual_rev * (0.09 - 0.0002 * t_idx + np.random.normal(0, 0.003))
            total_opex = opex_rd + opex_sm + opex_ga
            ebitda = gross_profit - total_opex
            net_income = ebitda * 0.76
            
            active_customers = int((actual_rev / (4200 if seg_name == "Enterprise" else (1450 if seg_name == "Mid-Market" else 480))) * np.random.normal(1.0, 0.015))
            headcount_fte = max(5, int((actual_rev / 26500) * (1.0 - 0.001 * t_idx)))
            dso_days = round(38.0 + (4.5 if seg_name == "Enterprise" else -3.0) - 0.04 * t_idx + np.random.normal(0, 1.1), 1)
            working_capital = actual_rev * 0.18
            operating_cash_flow = ebitda * 0.88 - (actual_rev - budget_rev) * 0.05
            
            rows_p1.append({
                "Date": d.strftime("%Y-%m-%d"),
                "Year": year,
                "Month": month,
                "Quarter": f"Q{(month-1)//3 + 1}",
                "Segment": seg_name,
                "Region": reg_name,
                "Macro_Confidence_Index": round(macro_index, 2),
                "Actual_Revenue": round(actual_rev, 2),
                "Budget_Revenue": round(budget_rev, 2),
                "Revenue_Variance": round(actual_rev - budget_rev, 2),
                "Revenue_Variance_Pct": round((actual_rev - budget_rev) / budget_rev * 100, 2),
                "COGS": round(cogs, 2),
                "Gross_Profit": round(gross_profit, 2),
                "Gross_Margin_Pct": round(gross_profit / actual_rev * 100, 2),
                "OpEx_RD": round(opex_rd, 2),
                "OpEx_Sales_Marketing": round(opex_sm, 2),
                "OpEx_GA": round(opex_ga, 2),
                "Total_OpEx": round(total_opex, 2),
                "EBITDA": round(ebitda, 2),
                "EBITDA_Margin_Pct": round(ebitda / actual_rev * 100, 2),
                "Net_Income": round(net_income, 2),
                "Net_Margin_Pct": round(net_income / actual_rev * 100, 2),
                "Operating_Cash_Flow": round(operating_cash_flow, 2),
                "Working_Capital": round(working_capital, 2),
                "Active_Customers": active_customers,
                "ARPU": round(actual_rev / max(1, active_customers), 2),
                "Headcount_FTE": headcount_fte,
                "Revenue_Per_Employee": round(actual_rev / max(1, headcount_fte), 2),
                "DSO_Days": dso_days
            })

df_p1 = pd.DataFrame(rows_p1)
df_p1.to_csv(os.path.join(p1_dir, "financial_revenue_7yr_historical.csv"), index=False)

# Aggregate monthly total revenue for time-series forecasting (84 months: 66 train, 18 test)
monthly_p1 = df_p1.groupby("Date").agg({
    "Actual_Revenue": "sum",
    "Budget_Revenue": "sum",
    "Gross_Profit": "sum",
    "Total_OpEx": "sum",
    "EBITDA": "sum",
    "Net_Income": "sum",
    "Operating_Cash_Flow": "sum",
    "Active_Customers": "sum",
    "Headcount_FTE": "sum",
    "Macro_Confidence_Index": "mean",
    "DSO_Days": "mean"
}).reset_index()
monthly_p1["Date"] = pd.to_datetime(monthly_p1["Date"])
monthly_p1["t"] = np.arange(len(monthly_p1))
monthly_p1["Month"] = monthly_p1["Date"].dt.month

# Split Train (Jan 2019 - Jun 2024: 66 months) and Holdout Test (Jul 2024 - Dec 2025: 18 months)
train_len = 66
y = monthly_p1["Actual_Revenue"].values
y_train = y[:train_len]
y_test = y[train_len:]

# Model 1: Baseline 3-Month Trailing Moving Average
pred_baseline = []
for i in range(train_len, len(y)):
    # 3-month rolling average without seasonal adjustment (standard naive management baseline)
    pred_baseline.append(np.mean(y[i-3:i]))
pred_baseline = np.array(pred_baseline)

# Model 2: Seasonal Naive (prior year same month + average drift)
drift = (y_train[-1] - y_train[0]) / (train_len - 1)
pred_snaive = np.array([y[i - 12] + 12 * drift for i in range(train_len, len(y))])

# Model 3: Holt-Winters Multiplicative Triple Exponential Smoothing (optimized via SciPy L-BFGS-B)
def holt_winters_mul(series, slen=12, alpha=0.3, beta=0.1, gamma=0.2, n_preds=18):
    seasonals = {}
    n_seasons = len(series) // slen
    season_averages = [sum(series[slen*j:slen*j+slen])/float(slen) for j in range(n_seasons)]
    for i in range(slen):
        sum_of_vals_over_avg = 0.0
        for j in range(n_seasons):
            sum_of_vals_over_avg += series[slen*j+i] / season_averages[j]
        seasonals[i] = sum_of_vals_over_avg / n_seasons
    
    result = []
    smooth = series[0]
    trend_val = sum([(series[i+slen] - series[i]) / float(slen) for i in range(slen)]) / slen
    for i in range(len(series) + n_preds):
        if i == 0:
            result.append(series[0])
            continue
        if i >= len(series):
            m = i - len(series) + 1
            result.append((smooth + m * trend_val) * seasonals[i % slen])
        else:
            val = series[i]
            last_smooth, smooth = smooth, alpha*(val/seasonals[i%slen]) + (1-alpha)*(smooth+trend_val)
            trend_val = beta * (smooth-last_smooth) + (1-beta)*trend_val
            seasonals[i%slen] = gamma*(val/smooth) + (1-gamma)*seasonals[i%slen]
            result.append((smooth+trend_val)*seasonals[i%slen])
    return np.array(result[:len(series)]), np.array(result[len(series):])

def hw_loss(params):
    a, b, g = params
    fitted, _ = holt_winters_mul(y_train, 12, a, b, g, n_preds=1)
    return np.mean(np.abs((y_train[12:] - fitted[12:]) / y_train[12:]))

res_hw = minimize(hw_loss, [0.35, 0.08, 0.25], bounds=[(0.05, 0.95), (0.01, 0.5), (0.05, 0.95)])
best_a, best_b, best_g = res_hw.x
hw_fitted, pred_hw = holt_winters_mul(y_train, 12, best_a, best_b, best_g, n_preds=len(y_test))

# Model 4: Dynamic Harmonic Regression with Exogenous Macro Indicator & Month Indicators (OLS / Ridge)
def build_features(df_sub):
    t = df_sub["t"].values
    m = df_sub["Month"].values
    macro = df_sub["Macro_Confidence_Index"].values
    X_cols = [
        np.ones(len(t)),
        t,
        t**2 / 1000.0,
        np.sin(2 * np.pi * (m - 3) / 12.0),
        np.cos(2 * np.pi * (m - 3) / 12.0),
        np.sin(4 * np.pi * (m - 3) / 12.0),
        np.cos(4 * np.pi * (m - 3) / 12.0),
        (m == 12).astype(float),
        (m == 1).astype(float),
        macro / 100.0
    ]
    return np.column_stack(X_cols)

X_all = build_features(monthly_p1)
X_tr, X_te = X_all[:train_len], X_all[train_len:]
# Fit log-linear Ridge regression for multiplicative stability
l2_reg = 1e-3 * np.eye(X_tr.shape[1])
l2_reg[0, 0] = 0
beta_dhr = np.linalg.solve(X_tr.T @ X_tr + l2_reg, X_tr.T @ np.log(y_train))
pred_dhr = np.exp(X_te @ beta_dhr)
fitted_dhr = np.exp(X_tr @ beta_dhr)

# Ensemble Model (60% Dynamic Harmonic Regression + 40% Holt-Winters)
pred_ensemble = 0.60 * pred_dhr + 0.40 * pred_hw

def calc_ts_metrics(actual, pred):
    mape = np.mean(np.abs((actual - pred) / actual)) * 100.0
    rmse = np.sqrt(np.mean((actual - pred) ** 2))
    mae = np.mean(np.abs(actual - pred))
    r2 = 1.0 - np.sum((actual - pred) ** 2) / np.sum((actual - np.mean(actual)) ** 2)
    return {"MAPE": round(float(mape), 2), "RMSE": round(float(rmse), 0), "MAE": round(float(mae), 0), "R2": round(float(r2), 4)}

m_base = calc_ts_metrics(y_test, pred_baseline)
m_snaive = calc_ts_metrics(y_test, pred_snaive)
m_hw = calc_ts_metrics(y_test, pred_hw)
m_dhr = calc_ts_metrics(y_test, pred_dhr)
m_ens = calc_ts_metrics(y_test, pred_ensemble)

mape_reduction_pct = round((m_base["MAPE"] - m_ens["MAPE"]) / m_base["MAPE"] * 100.0, 1)
mape_pp_improvement = round(m_base["MAPE"] - m_ens["MAPE"], 2)

# Generate 2026 Forecast Scenarios (12 months ahead: Base, Upside/Bull +8% macro/promo, Downside/Bear -7% macro contraction)
future_dates = pd.date_range(start="2026-01-01", end="2026-12-01", freq="MS")
df_future = pd.DataFrame({
    "Date": future_dates,
    "t": np.arange(len(monthly_p1), len(monthly_p1) + 12),
    "Month": future_dates.month,
    "Macro_Confidence_Index": [101.5 + 0.3 * i for i in range(12)]
})
X_fut_base = build_features(df_future)
# Re-fit on full 84 months for 2026 production forecast
beta_full = np.linalg.solve(X_all.T @ X_all + l2_reg, X_all.T @ np.log(y))
_, hw_fut = holt_winters_mul(y, 12, best_a, best_b, best_g, n_preds=12)
dhr_fut_base = np.exp(X_fut_base @ beta_full)
fut_base = 0.60 * dhr_fut_base + 0.40 * hw_fut

# Residual std for 95% confidence interval
resid_std = np.std((y_test - pred_ensemble) / y_test)
fut_bull = fut_base * 1.078
fut_bear = fut_base * 0.925
fut_ci_upper = fut_base * (1.0 + 1.96 * resid_std)
fut_ci_lower = fut_base * (1.0 - 1.96 * resid_std)

df_future["Base_Case_Forecast"] = np.round(fut_base, 2)
df_future["Bull_Case_Forecast"] = np.round(fut_bull, 2)
df_future["Bear_Case_Forecast"] = np.round(fut_bear, 2)
df_future["CI_95_Lower"] = np.round(fut_ci_lower, 2)
df_future["CI_95_Upper"] = np.round(fut_ci_upper, 2)
df_future.to_csv(os.path.join(p1_dir, "forecast_2026_scenarios.csv"), index=False)

# Save holdout comparison table
df_holdout = pd.DataFrame({
    "Date": monthly_p1["Date"].iloc[train_len:].dt.strftime("%Y-%m-%d"),
    "Actual_Revenue": np.round(y_test, 2),
    "Baseline_MA3": np.round(pred_baseline, 2),
    "Seasonal_Naive": np.round(pred_snaive, 2),
    "Holt_Winters": np.round(pred_hw, 2),
    "Dynamic_Harmonic_Reg": np.round(pred_dhr, 2),
    "Ensemble_Forecast": np.round(pred_ensemble, 2)
})
df_holdout.to_csv(os.path.join(p1_dir, "holdout_model_evaluation.csv"), index=False)

total_7yr_rev = float(df_p1["Actual_Revenue"].sum())
fy2025_rev = float(monthly_p1[monthly_p1["Date"].dt.year == 2025]["Actual_Revenue"].sum())
fy2024_rev = float(monthly_p1[monthly_p1["Date"].dt.year == 2024]["Actual_Revenue"].sum())
fy2019_rev = float(monthly_p1[monthly_p1["Date"].dt.year == 2019]["Actual_Revenue"].sum())
cagr_7yr = ((fy2025_rev / fy2019_rev) ** (1/6.0) - 1.0) * 100.0
fy2026_base_total = float(df_future["Base_Case_Forecast"].sum())
fy2026_bull_total = float(df_future["Bull_Case_Forecast"].sum())
fy2026_bear_total = float(df_future["Bear_Case_Forecast"].sum())

metrics_summary["project1"] = {
    "total_records": len(df_p1),
    "months": 84,
    "years": "2019-2025 (7 Years)",
    "total_7yr_revenue": round(total_7yr_rev, 2),
    "fy2019_revenue": round(fy2019_rev, 2),
    "fy2024_revenue": round(fy2024_rev, 2),
    "fy2025_revenue": round(fy2025_rev, 2),
    "yoy_2025_growth_pct": round((fy2025_rev - fy2024_rev) / fy2024_rev * 100, 2),
    "cagr_7yr_pct": round(cagr_7yr, 2),
    "fy2025_gross_margin_pct": round(float(df_p1[df_p1["Year"]==2025]["Gross_Profit"].sum() / fy2025_rev * 100), 2),
    "fy2025_ebitda_margin_pct": round(float(df_p1[df_p1["Year"]==2025]["EBITDA"].sum() / fy2025_rev * 100), 2),
    "fy2025_net_margin_pct": round(float(df_p1[df_p1["Year"]==2025]["Net_Income"].sum() / fy2025_rev * 100), 2),
    "models": {
        "Baseline_MA3": m_base,
        "Seasonal_Naive": m_snaive,
        "Holt_Winters": m_hw,
        "Dynamic_Harmonic_Reg": m_dhr,
        "Hybrid_Ensemble": m_ens
    },
    "mape_reduction_relative_pct": mape_reduction_pct,
    "mape_pp_improvement": mape_pp_improvement,
    "fy2026_scenarios": {
        "Base": round(fy2026_base_total, 2),
        "Bull": round(fy2026_bull_total, 2),
        "Bear": round(fy2026_bear_total, 2)
    }
}
print("Project 1 Metrics:", json.dumps(metrics_summary["project1"], indent=2))
