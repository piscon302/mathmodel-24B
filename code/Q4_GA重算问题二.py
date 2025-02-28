import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据定义
data = {
    '情况': [1, 2, 3, 4, 5, 6],
    '零配件 1 次品率': [0.15, 0.27, 0.15, 0.27, 0.15, 0.09],
    '零配件 2 次品率': [0.15, 0.27, 0.15, 0.27, 0.27, 0.09],
    '零配件 1 购买单价': [4, 4, 4, 4, 4, 4],
    '零配件 1 检测成本': [2, 2, 2, 1, 8, 2],
    '零配件 2 购买单价': [18, 18, 18, 18, 18, 18],
    '零配件 2 检测成本': [3, 3, 3, 1, 1, 3],
    '成品次品率': [0.10, 0.20, 0.10, 0.20, 0.10, 0.05],
    '装配成本': [6, 6, 6, 6, 6, 6],
    '市场售价': [56, 56, 56, 56, 56, 56],
    '调换损失': [6, 6, 30, 30, 10, 10],
    '拆解费用': [5, 5, 5, 5, 5, 40]
}

# 遗传算法参数
population_size = 50
num_generations = 100
mutation_rate = 0.1
tournament_size = 5
elite_size = 5

# 初始化种群
def initialize_population(pop_size, num_genes):
    return np.random.randint(2, size=(pop_size, num_genes))

# 计算适应度
def calculate_fitness(individual, data):
    total_cost = 0
    total_revenue = 0

    for i in range(len(data['情况'])):
        part1_inspect = individual[i * 4]  # 零配件 1 检测
        part2_inspect = individual[i * 4 + 1]  # 零配件 2 检测
        product_inspect = individual[i * 4 + 2]  # 成品检测
        discard_defective = individual[i * 4 + 3]  # 不合格成品拆解

        if discard_defective == 1:
            total_cost += data['拆解费用'][i]
            if part1_inspect == 1:
                total_cost += data['零配件 1 次品率'][i] * data['零配件 1 购买单价'][i] + data['零配件 1 检测成本'][i]
                total_revenue += data['市场售价'][i] - data['调换损失'][i]

            if part2_inspect == 1:
                total_cost += data['零配件 2 次品率'][i] * data['零配件 2 购买单价'][i] + data['零配件 2 检测成本'][i]
                total_revenue += data['市场售价'][i] - data['调换损失'][i]

        else:  # 不拆解的情况
            if part1_inspect == 1:
                total_cost += data['零配件 1 次品率'][i] * data['零配件 1 购买单价'][i] + data['零配件 1 检测成本'][i]
            if part2_inspect == 1:
                total_cost += data['零配件 2 次品率'][i] * data['零配件 2 购买单价'][i] + data['零配件 2 检测成本'][i]
            if product_inspect == 1:
                total_cost += data['成品次品率'][i] * data['装配成本'][i]
                total_revenue += data['市场售价'][i] - data['调换损失'][i]

    return total_revenue - total_cost

# 选择操作 - 锦标赛选择
def select(population, fitness):
    selected_indices = np.argsort(fitness)[-tournament_size:]
    return population[selected_indices]

# 交叉操作 - 单点交叉
def crossover(parent1, parent2):
    point = np.random.randint(1, len(parent1))
    child1 = np.concatenate((parent1[:point], parent2[point:]))
    child2 = np.concatenate((parent2[:point], parent1[point:]))
    return child1, child2

# 变异操作
def mutate(individual, mutation_rate):
    mutation_mask = np.random.rand(len(individual)) < mutation_rate
    individual[mutation_mask] = 1 - individual[mutation_mask]
    return individual

# 局部搜索 - 使用邻域搜索
def local_search(individual):
    best = individual.copy()
    best_fitness = calculate_fitness(best, data)
    for i in range(len(best)):
        new_individual = best.copy()
        new_individual[i] = 1 - new_individual[i]
        new_fitness = calculate_fitness(new_individual, data)
        if new_fitness > best_fitness:
            best, best_fitness = new_individual, new_fitness
    return best

# 遗传算法主程序
def genetic_algorithm(data):
    num_genes = len(data['情况']) * 4
    population = initialize_population(population_size, num_genes)

    fitness_history = []

    for generation in range(num_generations):
        fitness = np.array([calculate_fitness(ind, data) for ind in population])
        selected = select(population, fitness)

        new_population = []
        while len(new_population) < population_size - elite_size:
            parent1, parent2 = selected[np.random.choice(len(selected), 2, replace=False)]
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutate(child1, mutation_rate))
            new_population.append(mutate(child2, mutation_rate))

        elite_indices = np.argsort(fitness)[-elite_size:]
        elite = population[elite_indices]
        new_population.extend(elite)

        population = np.array(new_population)

        # 记录适应度历史
        fitness_history.append(np.max(fitness))

        # 增加多样性 - 随机替换一些个体
        num_replacements = int(population_size * 0.1)
        population[:num_replacements] = initialize_population(num_replacements, num_genes)

    final_fitness = np.array([calculate_fitness(ind, data) for ind in population])
    best_index = np.argmax(final_fitness)
    best_individual = population[best_index]

    # 对最终结果进行局部优化
    best_individual = local_search(best_individual)
    best_fitness = calculate_fitness(best_individual, data)

    return best_individual, best_fitness, fitness_history

# 运行遗传算法并输出结果
best_decision, best_score, fitness_history = genetic_algorithm(data)

# 打印结果
print("最佳决策方案（编码）：")
results = []
profits = []
for i, situation in enumerate(data['情况']):
    decision = best_decision[i * 4:(i + 1) * 4]
    # 计算每种情况的利润
    total_cost = 0
    total_revenue = 0
    if decision[3] == 1:  # 不合格成品拆解
        total_cost += data['拆解费用'][i]
        if decision[0] == 1:
            total_cost += data['零配件 1 次品率'][i] * data['零配件 1 购买单价'][i] + data['零配件 1 检测成本'][i]
            total_revenue += data['市场售价'][i] - data['调换损失'][i]
        if decision[1] == 1:
            total_cost += data['零配件 2 次品率'][i] * data['零配件 2 购买单价'][i] + data['零配件 2 检测成本'][i]
            total_revenue += data['市场售价'][i] - data['调换损失'][i]
    else:  # 不拆解的情况
        if decision[0] == 1:
            total_cost += data['零配件 1 次品率'][i] * data['零配件 1 购买单价'][i] + data['零配件 1 检测成本'][i]
        if decision[1] == 1:
            total_cost += data['零配件 2 次品率'][i] * data['零配件 2 购买单价'][i] + data['零配件 2 检测成本'][i]
        if decision[2] == 1:
            total_cost += data['成品次品率'][i] * data['装配成本'][i]
            total_revenue += data['市场售价'][i] - data['调换损失'][i]

    profit = total_revenue - total_cost
    profits.append(profit)
    results.append([
        situation,
        decision[0],  # 零配件 1 检测
        decision[1],  # 零配件 2 检测
        decision[2],  # 成品检测
        decision[3],  # 拆解
    ])

# 转换为 DataFrame 并打印
df = pd.DataFrame(results, columns=['情况', '零配件 1 检测', '零配件 2 检测', '成品检测', '拆解'])
print(df)

print("最佳适应度值：", best_score)

# 绘制适应度变化图
plt.plot(range(len(fitness_history)), fitness_history)
plt.xlabel('代数')
plt.ylabel('适应度值')
plt.title('适应度变化图')
plt.savefig('适应度变化曲线.png', dpi=500)
plt.show()
