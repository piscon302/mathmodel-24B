import numpy as np
import pandas as pd
from scipy.stats import norm


# 计算 Cochran 公式中的样本量
def calculate_min_sample_size(p_total, p0=0.1, confidence_level=0.95, error_margin=0.05):
    Z = norm.ppf(confidence_level)  # 单侧检验，查表得到Z值
    # 使用 Cochran 公式计算样本量
    m = (Z ** 2 * p0 * (1 - p0)) / (error_margin ** 2)
    # 如果总体数量有限，使用有限总体修正公式
    m_adjusted = m / (1 + (m - 1) / p_total)
    return int(np.ceil(m_adjusted))  # 向上取整以确保足够的样本量


# 计算修正后的次品率
def adjust_defect_rate(original_rate, p_total, p0=0.1, confidence_level=0.95, error_margin=0.05):
    # 计算样本量
    sample_size = calculate_min_sample_size(p_total, p0, confidence_level, error_margin)
    # 计算 Cochran 公式中的置信区间边界
    Z = norm.ppf(confidence_level)
    margin_of_error = Z * np.sqrt((original_rate * (1 - original_rate)) / sample_size)
    # 修正次品率为原始次品率加上边界
    adjusted_rate = original_rate + margin_of_error
    # 确保修正后的次品率不超过 1
    adjusted_rate = min(adjusted_rate, 1)
    return adjusted_rate


# 问题三的新数据
data_problem_3 = {
    '零配件': ['1', '2', '3', '4', '5', '6', '7', '8'],
    '次品率': [0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
    '购买单价': [2, 8, 12, 2, 8, 12, 8, 12],
    '检测成本': [1, 1, 2, 1, 1, 2, 1, 2],
    '半成品': ['1', '2', '3', '', '', '', '成品', '']
}

df_problem_3 = pd.DataFrame(data_problem_3)


# 计算每个零配件的修正次品率
def calculate_adjusted_defect_rates(df, p_total):
    adjusted_rates = []
    for _, row in df.iterrows():
        adjusted_rate = adjust_defect_rate(row['次品率'], p_total)
        adjusted_rates.append({
            '零配件': row['零配件'],
            '修正次品率': round(adjusted_rate, 4),  # 保留四位小数
            '购买单价': row['购买单价'],
            '检测成本': row['检测成本']
        })
    return pd.DataFrame(adjusted_rates)


# 设定总体数量
p_total = 10000

# 计算修正后的次品率
adjusted_df_problem_3 = calculate_adjusted_defect_rates(df_problem_3, p_total)
print(adjusted_df_problem_3)


# 计算生产过程中的决策方案
def calculate_decision_scheme(df):
    # 假设的市场售价和调换损失
    market_price = 200
    exchange_loss = 40

    # 决策依据
    decision_results = []
    for _, row in df.iterrows():
        purchase_price = row['购买单价']
        detection_cost = row['检测成本']
        adjusted_defect_rate = row['修正次品率']

        # 计算装配成本
        assembly_cost = 8  # 假设的装配成本

        # 计算总成本
        total_cost = purchase_price + detection_cost + assembly_cost

        # 计算每件产品的净利润
        profit = market_price - total_cost

        # 决策
        decision = '检测' if adjusted_defect_rate > 0.1 else '不检测'
        decision_results.append({
            '零配件': row['零配件'],
            '修正次品率': round(adjusted_defect_rate, 4)
        })

    return pd.DataFrame(decision_results)


# 计算生产过程中的决策方案
decision_df = calculate_decision_scheme(adjusted_df_problem_3)
print(decision_df)
