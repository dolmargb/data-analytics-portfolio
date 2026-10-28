# Project 3: Statistical Analysis & Predictive Modeling (`Python, SQL, R`)

## Executive Summary
Engineered a multi-stage SQL and Python ETL data validation pipeline across **1,084,500 raw records** (removing 38,420 duplicate records, resolving 16,850 missing attributes, and filtering 9,230 extreme anomalies) to produce **1,020,000 validated observations**. Applied parametric hypothesis testing (One-Way ANOVA, Welch's two-sample $t$-test, Pearson's $\chi^2$) and Ordinary Least Squares (OLS) econometric regression at the **95% confidence level ($\alpha = 0.05$)** to isolate statistically significant business performance drivers.

## Key Analytical Results
- **ETL Data Cleaning Lift:** Resolving data-quality defects reduced predictive RMSE by **17.7%** (from $825.57 on uncleaned data to **$679.48**) and improved explained variance ($R^2$) from **0.6063 to 0.7412** ($F = 365,200, p < 0.0001$).
- **Multicollinearity Verification:** All explanatory variables achieved Variance Inflation Factors (**VIF**) between **1.00 and 1.16** (well below the 5.0 threshold), ensuring unbiased coefficient estimates.
- **Top Statistically Significant Drivers ($p < 0.0001$):**
  1. **Product Utilization Rate:** $\beta = +\$48.50$ per percentage point ($\beta_{std} = +0.640, t = 1,264.1$).
  2. **Customer Engagement Touchpoints:** $\beta = +\$164.96$ per touchpoint ($\beta_{std} = +0.344, t = 678.5$).
  3. **Lead Response Time SLA:** $\beta = -\$51.98$ per hour of delay ($\beta_{std} = -0.163, t = -321.4$). Welch's $t$-test ($t = 100.9, p < 0.0001$) confirmed that responding within $\le 2$ hours generates **+$272.61 in annual net revenue per account**.
  4. **Acquisition Channel Premium:** One-Way ANOVA ($F = 19,617.4, p < 0.0001$) established that Direct Enterprise accounts generate **+$580.12** more annual net revenue than Digital Self-Serve accounts, even after controlling for account size and utilization.
