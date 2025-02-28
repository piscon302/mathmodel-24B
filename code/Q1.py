import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# 设置字体为SimHei以支持中文显示
# 设置字体大小
plt.rcParams.update({'font.size': 16})  # 修改整体字体大小，可以根据需要调整
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def calculate_min_sample_size(p, p0=0.1, confidence_level=0.95, error_margin=0.05):
    """
    计算给定总体数量 p 下的最小样本量 m，使得在95%置信水平下能够判断是否拒收。

    参数:
    p (int): 总体数量
    p0 (float): 次品率的估计（标称值，默认为10%）
    confidence_level (float): 置信水平（默认95%）
    error_margin (float): 容忍误差（默认5%）

    返回:
    int: 最小样本量 m
    """
    Z = norm.ppf(confidence_level)  # 单侧检验，正态分布查表得到Z值
    # 使用 Cochran 公式计算样本量
    m = (Z ** 2 * p0 * (1 - p0)) / (error_margin ** 2)

    # 如果总体数量有限，使用有限总体修正公式
    if p < np.inf:
        m_adjusted = m / (1 + (m - 1) / p)
    else:
        m_adjusted = m

    return int(np.ceil(m_adjusted))  # 向上取整以确保足够的样本量


# 1.1 小样本
# 不同总体数量下的样本量计算
p_values = np.arange(1, 502, 20)  # 小样本
m_values = [calculate_min_sample_size(p) for p in p_values]

# 绘制样本量随总体数量变化的图表
plt.figure(figsize=(12, 6))
plt.plot(p_values, m_values, marker='o')
plt.title('不同总体数量 p 下的最小样本量 m 的关系')
plt.xlabel('总体数量 p')
plt.ylabel('最小样本量 m')
plt.grid(True)
# plt.show()
plt.savefig('../image/1_1.png', dpi=300)

# 1.2 大样本
# 不同总体数量下的样本量计算
p_values = np.arange(500, 100001, 2000)  # 大样本：总体数量从50到10000
m_values = [calculate_min_sample_size(p) for p in p_values]

# 绘制样本量随总体数量变化的图表
plt.figure(figsize=(12, 6))
plt.plot(p_values, m_values, marker='o')
plt.title('不同总体数量 p 下的最小样本量 m 的关系')
plt.xlabel('总体数量 p')
plt.ylabel('最小样本量 m')
plt.grid(True)
# plt.show()
plt.savefig('../image/1_2.png', dpi=300)

# 2.1 小样本
# 不同总体数量下的样本量计算
p_values = np.arange(1, 502, 20)  # 小样本
m_values = [calculate_min_sample_size(p, confidence_level=0.9) for p in p_values]

# 绘制样本量随总体数量变化的图表
plt.figure(figsize=(12, 6))
plt.plot(p_values, m_values, marker='o')
plt.title('不同总体数量 p 下的最小样本量 m 的关系')
plt.xlabel('总体数量 p')
plt.ylabel('最小样本量 m')
plt.grid(True)
# plt.show()
plt.savefig('../image/1_3.png', dpi=300)

# 2.2 大样本
# 不同总体数量下的样本量计算
p_values = np.arange(500, 100001, 2000)  # 大样本：总体数量从50到10000
m_values = [calculate_min_sample_size(p, confidence_level=0.9) for p in p_values]

# 绘制样本量随总体数量变化的图表
plt.figure(figsize=(12, 6))
plt.plot(p_values, m_values, marker='o')
plt.title('不同总体数量 p 下的最小样本量 m 的关系')
plt.xlabel('总体数量 p')
plt.ylabel('最小样本量 m')
plt.grid(True)
# plt.show()
plt.savefig('../image/1_4.png', dpi=300)

# 综上所述：
# （1）小样本修正，随总体数增加，样本数增加；大样本就直接用Cochran公式，算出来最大是98
# （2）小样本修正，随总体数增加，样本数增加；大样本就直接用Cochran公式，算出来最大是60
