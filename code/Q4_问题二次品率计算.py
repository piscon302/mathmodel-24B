import numpy as np
import pandas as pd
from scipy.stats import norm


# 问题二次品率处理
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


# 表格数据
data = {
    '情况': [1, 2, 3, 4, 5, 6],
    '零配件 1 次品率': [0.1, 0.2, 0.1, 0.2, 0.1, 0.05],
    '零配件 2 次品率': [0.1, 0.2, 0.1, 0.2, 0.2, 0.05],
    '成品次品率': [0.1, 0.2, 0.1, 0.2, 0.1, 0.05]
}
df = pd.DataFrame(data)
# 设定总体数量
p_total = 10000


# 计算修正后的次品率
def calculate_adjusted_defect_rate(df, p_total):
    adjusted_rates = []
    for _, row in df.iterrows():
        # 计算修正后的次品率
        adjusted_rate_1 = adjust_defect_rate(row['零配件 1 次品率'], p_total)
        adjusted_rate_2 = adjust_defect_rate(row['零配件 2 次品率'], p_total)
        adjusted_rate_finished = adjust_defect_rate(row['成品次品率'], p_total)

        adjusted_rates.append({
            '情况': row['情况'],
            '零配件 1 次品率': round(adjusted_rate_1, 4),  # 保留四位小数
            '零配件 2 次品率': round(adjusted_rate_2, 4),  # 保留四位小数
            '成品次品率': round(adjusted_rate_finished, 4)  # 保留四位小数
        })
    return pd.DataFrame(adjusted_rates)


# 计算调整后的次品率
adjusted_df = calculate_adjusted_defect_rate(df, p_total)
print(adjusted_df)

# 问题二新数据展示
new_data = {
    '情况': [1, 2, 3, 4, 5, 6],
    '零配件 1 次品率': [0.15, 0.27, 0.15, 0.27, 0.15, 0.09],
    '零配件 2 次品率': [0.15, 0.27, 0.15, 0.27, 0.27, 0.09],
    '零配件 1 购买单价': [4, 4, 4, 4, 4, 4],
    '零配件 1 检测成本': [2, 2, 2, 1, 8, 2],
    '零配件 2 购买单价': [18, 18, 18, 18, 18, 18],
    '零配件 2 检测成本': [3, 3, 3, 1, 1, 3],
    '成品次品率': [0.15, 0.27, 0.15, 0.27, 0.15, 0.09],
    '装配成本': [6, 6, 6, 6, 6, 6],
    '市场售价': [56, 56, 56, 56, 56, 56],
    '调换损失': [6, 6, 30, 30, 10, 10],
    '拆解费用': [5, 5, 5, 5, 5, 40]
}
