import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置字体大小
plt.rcParams.update({'font.size': 14})  # 修改整体字体大小，可以根据需要调整
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
import itertools

# 输入表格数据
data = {
    "情况": [1, 2, 3, 4, 5, 6],
    "零配件1_次品率": [10, 20, 10, 20, 10, 5],
    "零配件1_购买单价": [4, 4, 4, 4, 4, 4],
    "零配件1_检测成本": [2, 2, 2, 1, 8, 2],
    "零配件2_次品率": [10, 20, 10, 20, 20, 5],
    "零配件2_购买单价": [18, 18, 18, 18, 18, 18],
    "零配件2_检测成本": [3, 3, 3, 1, 1, 3],
    "成品_次品率": [10, 20, 10, 20, 10, 5],
    "成品_装配成本": [6, 6, 6, 6, 6, 6],
    "成品_检测成本": [3, 3, 3, 2, 2, 3],
    "市场售价": [56, 56, 56, 56, 56, 56],
    "调换损失": [6, 6, 30, 30, 10, 10],
    "拆解费用": [0, 0, 0, 0, 0, 40]
}

df = pd.DataFrame(data)

# 记录前一次企业生产的成品数量
previous_n = 100


# 计算利润函数
def count_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2, assembly_cost,
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
    print(f'当前赚的利润为：{is_earned}，上一次拆解的零件数：{previous_n}，这一次拆解的零件数：{reject_n}')
    # 如果拆解的零件数比上一次少，说明才有拆解的必要，否则拆解后再组装还是次品，卖不出去
    if is_earned > 0 and previous_n - 1 > reject_n:
        previous_n = reject_n
        additional_profit = f_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2,
                                         assembly_cost, p_check_cost, replace_cost, rework_cost, reject_n, reject_n)
    else:
        additional_profit = 0

    # 总利润
    total_profit = total_revenue - total_cost + additional_profit
    print(f'共{ideal_n}件，卖了{total_revenue}元，重加工{additional_profit}元，成本为{total_cost}元')
    print(f'成品回溯，总利润共{total_profit}元')

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
    return count_profit(opt1, opt2, opt_check, opt_rework, p1_new, p2_new, p3_new, p_check_cost1, p_check_cost2,
                        assembly_cost, p_check_cost, replace_cost, rework_cost, n1, n2)


# 定义所有可能的决策组合（16种策略）
decisions = list(itertools.product([0, 1], repeat=4))

# 初始化存储结果的列表
results = []

# 遍历每种情况和每种决策组合
for index, row in df.iterrows():
    for decision in decisions:
        # 记录前一次企业生产的成品数量
        previous_n = 100
        # 拿到4个决策参数
        opt1, opt2, opt_check, opt_rework = decision
        # 从 row 中提取参数
        p1 = row['零配件1_次品率'] / 100
        p2 = row['零配件2_次品率'] / 100
        p3 = row['成品_次品率'] / 100
        assembly_cost = row['成品_装配成本']
        p_check_cost = row['成品_检测成本']
        replace_cost = row['调换损失']
        rework_cost = row['拆解费用']
        p_check_cost1 = row['零配件1_检测成本']
        p_check_cost2 = row['零配件2_检测成本']
        n1 = 100  # 零件1数量，这里可以是一个固定值或从其他地方读取
        n2 = 100  # 零件2数量
        # 计算该种决策下的利润
        profit = count_profit(opt1, opt2, opt_check, opt_rework, p1, p2, p3, p_check_cost1, p_check_cost2,
                              assembly_cost, p_check_cost, replace_cost, rework_cost, n1, n2)
        results.append({
            "情况": row["情况"],
            "零件1检测": decision[0],
            "零件2检测": decision[1],
            "成品检测": decision[2],
            "不合格成品拆解": decision[3],
            "利润": profit - (4 + 18) * 100
        })
# 转换为DataFrame输出结果
results_df = pd.DataFrame(results)
# 输出结果
results_df.to_excel('../data/Q2_6种情况在不同策略下的总利润.xlsx', index=False)

# 按利润最大化排序，获取每种情况的最佳决策
best_decisions = results_df.loc[results_df.groupby("情况")["利润"].idxmax()]

print("\n最佳决策方案：", best_decisions)

# 按利润最大化排序，获取每种情况的最佳决策
best_decisions = results_df.loc[results_df.groupby("情况")["利润"].idxmax()]

# 获取所有的决策组合
unique_decisions = results_df[['零件1检测', '零件2检测', '成品检测', '不合格成品拆解']].drop_duplicates()

# 16条策略折线图，横坐标6种情况，纵坐标总利润
# 为每种策略绘制折线图
plt.figure(figsize=(12, 6))

for index, decision in unique_decisions.iterrows():
    # 获取当前策略的所有行
    strategy_rows = results_df[
        (results_df['零件1检测'] == decision['零件1检测']) &
        (results_df['零件2检测'] == decision['零件2检测']) &
        (results_df['成品检测'] == decision['成品检测']) &
        (results_df['不合格成品拆解'] == decision['不合格成品拆解'])
        ]

    # 绘制当前策略的折线图
    plt.plot(strategy_rows['情况'], strategy_rows['利润'], marker='o', label=f"策略: {decision.values}")

# 可视化图表
# 表1 6种情况在不同策略下的总利润变化
plt.title('6种情况在不同策略下的总利润变化')
plt.xlabel('情况')
plt.ylabel('总利润')
plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.02), title="策略组合")
plt.tight_layout()
plt.savefig('../image/6种情况在不同策略下的总利润变化.png', dpi=500)

# 复制数据并更新列名为中文
best_decision_df = best_decisions.copy()
best_decision_df.columns = ['情况', '零件1检测', '零件2检测', '成品检测', '不合格成品拆解', '利润']

# 替换检测和拆解的值
best_decision_df['零件1检测'] = best_decision_df['零件1检测'].map({1: '检测', 0: '不检测'})
best_decision_df['零件2检测'] = best_decision_df['零件2检测'].map({1: '检测', 0: '不检测'})
best_decision_df['成品检测'] = best_decision_df['成品检测'].map({1: '检测', 0: '不检测'})
best_decision_df['不合格成品拆解'] = best_decision_df['不合格成品拆解'].map({1: '拆解', 0: '不拆解'})

# 保留利润小数点后两位
best_decision_df['利润'] = best_decision_df['利润'].apply(lambda x: f"{x:.2f}")

# 将情况前缀更新为"情况1-6"
best_decision_df['情况'] = best_decision_df['情况'].apply(lambda x: f'情况{x}')

# 输出到 Excel 文件
best_decision_df.to_excel('../data/Q2_每个情况的最佳方案.xlsx', index=False)

# 绘制表格
fig, ax = plt.subplots(figsize=(12, 4))

# 移除坐标轴
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_frame_on(False)

# 创建表格
table = plt.table(cellText=best_decision_df.values,
                  colLabels=best_decision_df.columns,
                  cellLoc='center',
                  loc='center',
                  bbox=[0, 0, 1, 1])

# 设置表格样式
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.2)  # 调整表格大小

plt.title('每个情况的最佳方案', fontsize=16)
plt.tight_layout()
# plt.savefig('每个情况的最佳方案.png', dpi=500)
plt.show()


# 创建数据
data = {
    '情况': ['情况1', '情况2', '情况3', '情况4', '情况5', '情况6'],
    '利润': [1242.00, 308.00, 1119.77, 544.00, 783.46, 1858.68]
}

# 转换为 DataFrame
df = pd.DataFrame(data)

# 设置seaborn主题
sns.set(style="whitegrid")

# 设置字体大小
plt.rcParams.update({'font.size': 14})  # 修改整体字体大小，可以根据需要调整
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 绘制柱状图
plt.figure(figsize=(10, 6))
barplot = sns.barplot(x='情况', y='利润', data=df, palette="viridis")

# 添加数据标签
for index, row in df.iterrows():
    barplot.text(index, row['利润'] + 10, round(row['利润'], 2), color='black', ha="center")

# 设置标题和标签
plt.title('各情况下的最佳决策利润', fontsize=16)
plt.xlabel('情况', fontsize=14)
plt.ylabel('利润', fontsize=14)

# 显示图表
# plt.show()
plt.savefig('../image/2_col.png', dpi=300)
