import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import os

# 设置字体大小
plt.rcParams.update({'font.size': 16})  # 修改整体字体大小，可以根据需要调整
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 输入表格数据
data = {
    "情况": [1, 2, 3, 4, 5, 6],
    "零配件1次品率": [10, 20, 10, 20, 10, 5],
    "零配件1购买单价": [4, 4, 4, 4, 4, 4],
    "零配件1检测成本": [2, 2, 2, 1, 8, 2],
    "零配件2次品率": [10, 20, 10, 20, 20, 5],
    "零配件2购买单价": [18, 18, 18, 18, 18, 18],
    "零配件2检测成本": [3, 3, 3, 1, 1, 3],
    "成品次品率": [10, 20, 10, 20, 10, 5],
    "成品装配成本": [6, 6, 6, 6, 6, 6],
    "成品检测成本": [3, 3, 3, 2, 2, 3],
    "市场售价": [56, 56, 56, 56, 56, 56],
    "调换损失": [6, 6, 30, 30, 10, 10],
    "拆解费用": [5, 5, 5, 5, 5, 40]
}

df = pd.DataFrame(data)
# 记录前一次企业生产的成品数量
previous_n = 100

# 计算利润函数
def calculate_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2, assembly_cost,
                     p_check_cost, replace_cost, rework_cost, n1, n2):
    """
    计算不同决策组合下的总成本，包括零配件检测成本、装配成本、成品检测成本、返工成本等。

    参数:
    opt1, opt2: 零件1和零件2是否检测的决策变量
    opt_check: 成品是否检测的决策变量
    opt_rework: 是否进行返工的决策变量
    p1, p2, p3: 零件1、零件2、装配为成品过程 的 次品率
    p_check_cost1, p_check_cost2: 零件1和零件2的检测成本
    assembly_cost: 装配成本
    p_check_cost: 成品检测成本
    replace_cost: 成品调换损失
    rework_cost: 拆解费用
    n1, n2: 零件1和零件2的数量

    计算得出中间量
    product_n: 生产成品数量

    返回:
    total_profit: 总利润
    """

    # 递归退出条件
    if n1 < 1 or n2 < 1:
        return 0  # 没赚钱也没亏钱

    # 考虑策略1、2

    p_assembly = 1 - max(opt1 * p1, opt2 * p2)

    # 生产的成品数量
    product_n = n1 * p_assembly

    # 理想状态下，完全没有次品的成品个数
    ideal_n = 0

    if opt1 == 1 and opt2 == 1:
        ideal_n = n1 * (1 - max(p1, p2)) * (1 - p3)
    else:
        ideal_n = n1 * (1 - p1) * (1 - p2) * (1 - p3)

    # 根据策略3，得到实际成品数量
    real_n = ideal_n if opt_check == 1 else product_n

    # 如果不选择检测，仍有次品，需要计算次品率
    if real_n != 0:
        p_hidden = 1 - ideal_n / real_n
    else:
        p_hidden = 0  # 或者其他适当的处理方式

    # 零件检测成本
    cost_parts = opt1 * p_check_cost1 * n1 + opt2 * p_check_cost2 * n2

    # 装配成本
    cost_assembly = assembly_cost * product_n

    # 成品检测成本
    cost_product = opt_check * p_check_cost * product_n

    # 拆解和调换成本
    cost_rework = opt_rework * rework_cost * (product_n - ideal_n)
    cost_replace = replace_cost * p_hidden * real_n

    # 如果选择拆解，那还要重新得到零件数去递归
    reject_n = opt_rework * (product_n - ideal_n)

    # 总成本
    total_cost = cost_parts + cost_assembly + cost_product + cost_rework + cost_replace
    # 总售额：理想的成品数量
    total_revenue = ideal_n * 56
    # 当前赚的利润
    is_earned = ideal_n * 34 - total_cost

    global previous_n
    # 如果拆解的零件数比上一次少，说明才有拆解的必要，否则拆解后再组装还是次品，卖不出去
    if is_earned > 0 and previous_n - 1 > reject_n:
        previous_n = reject_n
        additional_profit = f_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2,
                                         assembly_cost, p_check_cost, replace_cost, rework_cost, reject_n, reject_n)
    else:
        additional_profit = 0

    # 总利润
    total_profit = total_revenue - total_cost + additional_profit
    return total_profit

# 递归，要先做次品率的概率修正
def f_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2, assembly_cost, p_check_cost,
             replace_cost, rework_cost, n1, n2):
    # print('before', p1, p2, p3)
    if opt1 == 0 and opt2 == 0:
        p1_new = p1 / (1 - (1 - p1) * (1 - p2) * (1 - p3))
        p2_new = p2 / (1 - (1 - p1) * (1 - p2) * (1 - p3))
        p3_new = p3 / (1 - (1 - p1) * (1 - p2) * (1 - p3))
    elif opt1 == 1 and opt2 == 0:
        p1_new = 0
        p2_new = p2 / (1 - (1 - p2) * (1 - p3))
        p3_new = p3 / (1 - (1 - p2) * (1 - p3))
    elif opt1 == 0 and opt2 == 1:
        p1_new = p1 / (1 - (1 - p1) * (1 - p3))
        p2_new = 0
        p3_new = p3 / (1 - (1 - p1) * (1 - p3))
    else:
        p1_new = 0
        p2_new = 0
        p3_new = 1
    return calculate_profit(opt1, opt2, opt_check, opt_rework, p1_new, p2_new, p3_new, p_check_cost1, p_check_cost2,
                        assembly_cost, p_check_cost, replace_cost, rework_cost, n1, n2)



def compute_profit_for_decisions(df, decisions):
    results = []
    for index, row in df.iterrows():
        for decision in decisions:
            # 记录前一次企业生产的成品数量
            previous_n = 100
            # 拿到4个决策参数
            opt1, opt2, opt_check, opt_rework = decision
            # 从 row 中提取参数
            p1 = row['零配件1次品率'] / 100
            p2 = row['零配件2次品率'] / 100
            p3 = row['成品次品率'] / 100
            assembly_cost = row['成品装配成本']
            p_check_cost = row['成品检测成本']
            replace_cost = row['调换损失']
            rework_cost = row['拆解费用']
            p_check_cost1 = row['零配件1检测成本']
            p_check_cost2 = row['零配件2检测成本']
            n1 = 100  # 零件1数量，这里可以是一个固定值或从其他地方读取
            n2 = 100  # 零件2数量
            # 计算该种决策下的利润
            profit = calculate_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2,
                                  assembly_cost, p_check_cost, replace_cost, rework_cost, n1, n2)
            results.append({
                "情况": row["情况"],
                "零件1检测": decision[0],
                "零件2检测": decision[1],
                "成品检测": decision[2],
                "不合格成品拆解": decision[3],
                "利润": profit - (4 + 18) * 100
            })

    return pd.DataFrame(results)


# 定义所有可能的决策组合（16种策略）
decisions = list(itertools.product([0, 1], repeat=4))

# 计算所有决策组合下的利润
results_df = compute_profit_for_decisions(df, decisions)

# 按利润最大化排序，获取每种情况的最佳决策
best_decisions = results_df.loc[results_df.groupby("情况")["利润"].idxmax()]

# 创建“敏感性分析”目录
os.makedirs("../敏感性分析", exist_ok=True)


# 敏感性分析结果展示
def sensitivity_analysis(parameter, values):
    plt.figure(figsize=(12, 8))
    tables = []
    for value in values:
        temp_df = df.copy()
        temp_df[parameter] = value
        temp_results = compute_profit_for_decisions(temp_df, decisions)
        best_temp_decisions = temp_results.loc[temp_results.groupby("情况")["利润"].idxmax()]

        # 以参数值为x轴，最大利润为y轴绘制
        plt.plot(best_temp_decisions["情况"], best_temp_decisions["利润"], marker='o', linestyle='-',
                 label=f'{parameter} = {value}')

        # 准备表格数据
        best_decision_table = best_temp_decisions.copy()
        best_decision_table[parameter] = f'{value}'
        best_decision_table["零件1检测"] = best_decision_table["零件1检测"].apply(
            lambda x: '检测' if x == 1 else '不检测')
        best_decision_table["零件2检测"] = best_decision_table["零件2检测"].apply(
            lambda x: '检测' if x == 1 else '不检测')
        best_decision_table["成品检测"] = best_decision_table["成品检测"].apply(
            lambda x: '检测' if x == 1 else '不检测')
        best_decision_table["不合格成品拆解"] = best_decision_table["不合格成品拆解"].apply(
            lambda x: '拆解' if x == 1 else '不拆解')

        # 添加表格到列表
        tables.append(best_decision_table)

    plt.xlabel('情况')
    plt.ylabel('最大利润')
    plt.title(f'{parameter}的敏感性分析')
    plt.legend()
    plt.grid(True)

    # 保存敏感性分析图像
    plt.savefig(f'../敏感性分析/{parameter}的敏感性分析图像.png', dpi=500)
    plt.close()

    # 保存表格为PNG图片
    for i, table in enumerate(tables):
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_frame_on(False)

        # 创建表格
        table_fig = plt.table(cellText=table.values,
                              colLabels=table.columns,
                              cellLoc='center',
                              loc='center',
                              bbox=[0, 0, 1, 1])

        # 设置表格样式
        table_fig.auto_set_font_size(False)
        table_fig.set_fontsize(12)
        table_fig.scale(1.2, 1.2)  # 调整表格大小

        plt.title(f'{parameter}={values[i]}下的最佳方案', fontsize=16)
        plt.tight_layout()

        # 保存表格图像
        plt.savefig(f'../敏感性分析/在{parameter}={values[i]}下的最佳方案.png', dpi=500)
        plt.close()


# 进行敏感性分析
parameters = [
    ('零配件1次品率', [5, 10, 15, 20]),
    ('零配件2次品率', [5, 10, 15, 20]),
    ('成品次品率', [5, 10, 15, 20]),
    ('零配件1检测成本', [0, 2, 5, 10]),
    ('零配件2检测成本', [0, 2, 5, 10]),
    ('成品检测成本', [0, 2, 5, 10]),
    ('调换损失', [0, 5, 10, 15, 20])
]

for param, vals in parameters:
    sensitivity_analysis(param, vals)
