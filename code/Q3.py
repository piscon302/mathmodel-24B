import pandas as pd
import itertools
import matplotlib.pyplot as plt

# 设置字体大小
plt.rcParams.update({'font.size': 16})  # 修改整体字体大小，可以根据需要调整
# 防止中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 构造DataFrame
data = {
    '零配件': [1, 2, 3, 4, 5, 6, 7, 8],
    '次品率': ['10%', '10%', '10%', '10%', '10%', '10%', '10%', '10%'],
    '购买单价': [2, 8, 12, 2, 8, 12, 8, 12],
    '检测成本': [1, 1, 2, 1, 1, 2, 1, 2],
}

df = pd.DataFrame(data)

# 利润最大化    总利润 = 总收入 - 总成本

# 题目给的，都一样的常量
p_check_cost1 = p_check_cost2 = 1  # 零件1、零件2的检测成本
p_check_cost3 = 2  # 零件3的检测成本
assembly_cost = 8  # 装配成本
replace_cost = 40  # 成品调换损失
mid_check_cost = 4  # 半成品检测成本
p_check_cost = 6  # 成品检测成本
mid_rework_cost = 6  # 半成品拆解费用
p_rework_cost = 10  # 成品拆解费用

p_part = 0.1  # 刚开始零件的次品率
p_mid = 0.1  # 刚开始半成品的次品率

previous_mid_n = 100  # 记录前一次企业生产的半成品数量
previous_f_n = 100  # 记录前一次企业生产的成品数量


# 零件 - 成品 全流程函数
def count_profit(opt1, opt2, opt3, opt4, opt5, n, p_part, p_mid):
    '''
    参数：
    opt1：零件的检测策略
    opt2：半成品的检测策略
    opt3：成品的检测策略
    opt4：半成品是否拆解
    opt5：成品是否拆解
    n：理想成品个数，假设理想值（不考虑次品）算出能生产出100个成品
    p_part：零件的次品率
    p_mid：半成品的次品率

    中间量：
    product_mid_n：半成品的实际生产数量
    p_mid_hidden：如果不对半成品进行检测，其中隐藏的次品率（检测的话就是次品率为0）
    product_f_n：成品的实际生产数量
    p_f_hidden：如果不对成品进行检测，其中隐藏的次品率（检测的话就是次品率为0）
    reject_mid_n：如果拆解半成品，拆解的数量
    reject_f_n：如果拆解成品，拆解的数量

    结果：
    total_profit：总利润
    '''

    # 递归退出条件
    if n < 1:
        return 0  # 没赚钱也没亏钱

    # -------------------- 零件 - 半成品 --------------------

    # 企业实际生产的半成品数量
    p_to_mid = 1 - opt1 * p_part
    product_mid_n = p_to_mid * n

    # 理想状态下，完全没有次品的半成品个数
    if opt1 == 1:
        ideal_mid_n = n * (1 - p_part) * 0.9  # 组装
    else:
        ideal_mid_n = n * (1 - p_part) ** 3 * 0.9  # 3种零件 + 组装

    # 根据策略opt2，得到实际半成品数量
    real_mid_n = ideal_mid_n if opt2 == 1 else product_mid_n

    # 如果不选择检测，仍有次品，需要计算次品率
    p_mid_hidden = 1 - ideal_mid_n / real_mid_n

    # 零件检测成本
    cost_parts = 6 * n * opt1 * p_check_cost1 + 2 * n * opt1 * p_check_cost3
    # 装配成半成品的成本
    cost_mid_assembly = assembly_cost * 3 * product_mid_n
    # 半成品检测成本
    cost_mid_check = opt2 * mid_check_cost * 3 * product_mid_n
    # 半成品拆解成本
    cost_mid_rework = opt4 * mid_rework_cost * 3 * (product_mid_n - ideal_mid_n)

    # 根据opt4，选择是否对半成品进行拆解，如果拆解要进递归
    reject_mid_n = opt4 * (product_mid_n - ideal_mid_n)

    additional_profit1 = 0

    global previous_mid_n  # 上一次拆解后的半成品数
    # 如果拆解的零件数比上一次少，说明才有拆解的必要，因为这样说明上一次拆解过后能至少卖出去一个，否则拆解后再组装全都还是次品，卖不出去
    if previous_mid_n - 1 > reject_mid_n and reject_mid_n > 1:
        previous_mid_n = reject_mid_n
        print('reject_mid_n: ', reject_mid_n)
        p_part = p_part / (1 - (1 - p_part) ** 3)
        # 递归，拿到剩下reject_mid_n套配件数，组装-生产-销售全流程，产生的利润
        additional_profit1 = count_profit(opt1, opt2, opt3, opt4, opt5, reject_mid_n, p_part, p_mid)
    else:
        additional_profit1 = 0

    # -------------------- 零件 - 成品 --------------------

    # 企业实际生产的成品数量（根据是否检测半成品来考虑）
    p_to_f = 1 - opt2 * p_mid
    product_f_n = p_to_f * product_mid_n

    # 理想状态下，完全没有次品的成品个数
    # global ideal_f_n
    ideal_f_n = 0
    if opt2 == 1:
        ideal_f_n = product_mid_n * (1 - p_mid) * 0.9  # 3个半成品能正确组装配对
    else:
        ideal_f_n = product_mid_n * (1 - p_mid) ** 3 * 0.9  # 3个半成品无法正确组装配对

    # 根据策略opt3，得到实际成品数量
    real_f_n = ideal_f_n if opt3 == 1 else product_f_n

    # 如果不选择检测，仍有次品，需要计算次品率
    p_f_hidden = 1 - ideal_f_n / real_f_n

    # 装配为成品的成本
    cost_f_assembly = assembly_cost * product_f_n
    # 成品检测成本
    cost_f_product = opt3 * p_check_cost * product_f_n
    # 成品拆解成本
    cost_f_rework = opt5 * p_rework_cost * (product_f_n - ideal_f_n)
    # 调换成本
    cost_replace = replace_cost * p_f_hidden * real_f_n

    # 如果选择对成品进行拆解，那还要重新得到半成品数去递归
    reject_f_n = opt5 * (product_f_n - ideal_f_n)

    # 半成品 - 成品
    global previous_f_n
    print(f'上一次半成品的数量：{previous_f_n}, 这一次半成品的数量：{reject_f_n}')
    if previous_f_n - 1 > reject_f_n or reject_f_n > 1:  # 得先确定有拆解的必要，不然拆完卖不出去浪费钱
        previous_f_n = reject_f_n
        if opt4 == 1 and opt5 == 1:
            # 都拆回零件，那么就计算最终拆成的零件总数，并作次品率p_mid修正，然后去递归
            p_part = p_part / (1 - (1 - p_part) ** 3)
            print('opt4=1, opt5=1')
            additional_profit2 = count_profit(opt1, opt2, opt3, opt4, opt5, reject_f_n, p_part, p_mid)
        elif opt4 == 0 and opt5 == 1:
            # 半成品不拆回零件，那么就计算最终拆成的零件总数，并作次品率修正，然后去递归
            p_mid = p_mid / (1 - (1 - p_mid) ** 3)
            print('opt4=0, opt5=1')
            additional_profit2 = count_middle_to_final_profit(opt2, opt3, reject_f_n, p_mid)
        else:
            # 成品不进行拆解，那不考虑了
            additional_profit2 = 0
    else:
        additional_profit2 = 0

    # 总成本
    total_cost = cost_parts + cost_mid_assembly + cost_mid_check + cost_mid_rework + cost_f_assembly + cost_f_product + cost_f_rework + cost_replace
    # 总收入
    total_revenue = ideal_f_n * 200
    # 总利润
    total_profit = total_revenue - total_cost + additional_profit1 + additional_profit2
    print(
        f'共{ideal_f_n}件，卖了{total_revenue}元，半成品重加工{additional_profit1}元，成品重加工{additional_profit2}元，成本为{total_cost}元')
    print(f'成品回溯，总利润共{total_profit}元')

    return total_profit


# 半成品 - 成品
# 当半成品不进行拆解，成品进行拆解时 (opt4=0, opt5=1)，来到这一步骤
# 如果都拆解，那其实本质上都是求 零件 - 成品 全过程带来的收益，和上面的函数一样


# 半成品 - 成品带来的利润
def count_middle_to_final_profit(opt2, opt3, mid_n, p_mid):
    '''
    说明：
    已知半成品的数量mid_n，次品率p_mid，（不拆解为零件）求他们能带来的利润收益
    参数：
    opt1-3：不在本函数考虑范围之内
    opt4：半成品的检测策略
    opt5：成品的检测策略
    opt6=0：半成品是否拆解  不拆解
    opt7=0：成品是否拆解    拆解
    mid_n：理想成品个数
    p_mid：半成品的次品率

    中间量：
    product_half1、product_half2、product_half3：半成品的实际生产数量
    p_half1_hidden、p_half1_hidden、p_half1_hidden：如果不对半成品进行检测，其中隐藏的次品率（检测的话就是次品率为0）

    结果：
    total_profit：总利润
    '''

    # 递归退出条件
    if mid_n < 1:
        return 0  # 没赚钱也没亏钱

    # 企业生产的成品数
    p_to_f = 1 - opt2 * p_mid
    product_n = p_to_f * mid_n

    # 理想状态下，完全没有次品的成品个数
    if opt2 == 1:
        ideal_f_n = mid_n * (1 - p_mid) * 0.9
    else:
        ideal_f_n = mid_n * (1 - p_mid) ** 3 * 0.9

    # 根据策略opt3，得到实际成品数量
    real_f_n = ideal_f_n if opt3 == 1 else product_n

    # 如果不选择检测，仍有次品，需要计算次品率
    p_f_hidden = 1 - ideal_f_n / real_f_n

    # 半成品检测成本
    cost_mid_check = opt2 * mid_check_cost * 3 * mid_n
    # 装配为成品的成本
    cost_f_assembly = assembly_cost * product_n
    # 成品检测成本
    cost_f_product = opt3 * p_check_cost * product_n
    # 成品拆解成本
    cost_f_rework = opt5 * p_rework_cost * (product_n - ideal_f_n)
    # 调换成本
    cost_replace = replace_cost * p_f_hidden * real_f_n

    # 此时必对成品进行拆解，重新得到半成品数去继续递归该 “半成品 - 成品” 函数，去继续计算收益
    reject_f_n = product_n - ideal_f_n

    global previous_f_n
    if previous_f_n - 1 > reject_f_n and reject_f_n > 1:
        # 半成品不拆回零件，那么就计算最终拆成的零件总数，并作次品率修正，然后去递归
        previous_f_n = reject_f_n
        p_mid = p_mid / (1 - (1 - p_mid) ** 3)
        additional_profit2 = count_middle_to_final_profit(opt2, opt3, reject_f_n, p_mid)
    else:
        # 成品不进行拆解，那不考虑了
        additional_profit2 = 0

    # 总成本
    total_cost = cost_mid_check + cost_f_assembly + cost_f_product + cost_f_rework + cost_replace
    # 总收入
    total_revenue = ideal_f_n * 200
    # 总利润
    total_profit = total_revenue - total_cost + additional_profit2
    # 回溯打印
    print(
        f'半成品-成品回溯：共{ideal_f_n}件，卖了{total_revenue}元，成品重加工{additional_profit2}元，成本为{total_cost}元')
    print(f'半成品-成品回溯，总利润共{total_profit}元')

    return total_profit


# 定义所有可能的决策组合，后面遍历32种情况
decisions = list(itertools.product([0, 1], repeat=5))

# 初始化存储结果的列表
results = []

# 遍历每种情况和每种决策组合
for decision in decisions:
    # 拿到5个决策参数
    opt1, opt2, opt3, opt4, opt5 = decision
    # 从 row 中提取参数
    p_check_cost1 = p_check_cost2 = 1  # 零件1、零件2的检测成本
    p_check_cost3 = 2  # 零件3的检测成本
    assembly_cost = 8  # 装配成本
    replace_cost = 40  # 成品调换损失
    mid_check_cost = 4  # 半成品检测成本
    p_check_cost = 6  # 成品检测成本
    mid_rework_cost = 6  # 半成品拆解费用
    p_rework_cost = 10  # 成品拆解费用
    n = 100  # 零件数量（1-8各100个，理想情况组成100个成品）

    p_part = 0.1  # 刚开始零件的次品率
    p_mid = 0.1  # 刚开始半成品的次品率

    previous_mid_n = 100  # 记录前一次企业生产的半成品数量
    previous_f_n = 100  # 记录前一次企业生产的成品数量

    # 计算该种决策下的利润
    profit = count_profit(opt1, opt2, opt3, opt4, opt5, n, p_part, p_mid)
    results.append({
        "零件检测": decision[0],
        "半成品检测": decision[1],
        "成品检测": decision[2],
        "不合格半成品拆解": decision[3],
        "不合格成品拆解": decision[4],
        "利润": profit - 64 * 100
    })

# 转换为DataFrame输出结果
results_df = pd.DataFrame(results)

results_df.to_excel('../data/Q3_所有策略对应的利润.xlsx', index=False)

# 可视化比较结果
# 从 Excel 文件中读取数据：
df = pd.read_excel('../data/Q3_所有策略对应的利润.xlsx')

# 绘制图表
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['利润'], marker='o', linestyle='-', color='b', label='利润')

# 设置标题和标签
plt.title('32种不同策略的比较', fontsize=16)
plt.xlabel('策略编号', fontsize=14)
plt.ylabel('利润', fontsize=14)

# 添加网格
plt.grid(True)

# 添加图例
plt.legend()

# 显示图表
# plt.show()
plt.savefig('../image/3_res.png', dpi=500)
