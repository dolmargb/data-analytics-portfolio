# ==============================================================================
# PROJECT 3: ECONOMETRIC & HYPOTHESIS TESTING SUITE IN R
# Dataset: 1,020,000 Validated Operational & Commercial Account Observations
# Confidence Level: 95% (alpha = 0.05)
# ==============================================================================

library(tidyverse)
library(car)       # For Variance Inflation Factor (VIF)
library(lmtest)    # For Breusch-Pagan heteroskedasticity & White robust SEs
library(sandwich)  # For HC3 heteroskedasticity-consistent covariance matrix

# 1. Load Cleaned Dataset
df <- read_csv("cleaned_modeling_dataset_sample.csv")
cat("Loaded validated modeling dataset:", nrow(df), "observations\n")

# 2. Hypothesis Test 1: One-Way ANOVA across Acquisition Channels
df$channel <- factor(df$channel, levels = c("Digital_Self_Serve", "Partner_Referral", "Direct_Enterprise"))
anova_model <- aov(annual_net_revenue ~ channel, data = df)
cat("\n--- One-Way ANOVA Summary (Acquisition Channel) ---\n")
print(summary(anova_model))
print(TukeyHSD(anova_model, conf.level = 0.95))

# 3. Hypothesis Test 2: Welch's Two-Sample t-Test (Lead Response SLA <= 2h vs > 2h)
df$fast_sla <- ifelse(df$lead_response_time_hrs <= 2.0, "Fast_SLA_Under_2h", "Slow_SLA_Over_2h")
welch_res <- t.test(annual_net_revenue ~ fast_sla, data = df, var.equal = FALSE, conf.level = 0.95)
cat("\n--- Welch's Two-Sample t-Test (SLA Response Time) ---\n")
print(welch_res)

# 4. Hypothesis Test 3: Pearson's Chi-Square Test of Independence
df$high_utilization <- ifelse(df$product_utilization_pct >= 65.0, "High_Util", "Low_Util")
df$top_revenue_tier <- ifelse(df$annual_net_revenue >= median(df$annual_net_revenue), "Top_Half", "Bottom_Half")
chi_tbl <- table(df$high_utilization, df$top_revenue_tier)
chi_res <- chisq.test(chi_tbl)
cat("\n--- Pearson Chi-Square Independence Test ---\n")
print(chi_res)

# 5. Multiple Linear Regression (OLS) & Multicollinearity Audit (VIF)
ols_fit <- lm(
  annual_net_revenue ~ product_utilization_pct + engagement_touchpoints +
    lead_response_time_hrs + promo_discount_pct + account_size_log +
    onboarding_cycle_days + channel,
  data = df
)
cat("\n--- OLS Multiple Regression Summary ---\n")
print(summary(ols_fit))

cat("\n--- 95% Confidence Intervals for Regression Parameters ---\n")
print(confint(ols_fit, level = 0.95))

cat("\n--- Variance Inflation Factors (VIF < 5.0 Threshold) ---\n")
print(vif(ols_fit))

cat("\n--- Robust HC3 Standard Errors ---\n")
print(coeftest(ols_fit, vcov = vcovHC(ols_fit, type = "HC3")))
