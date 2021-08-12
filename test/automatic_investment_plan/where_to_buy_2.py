import pickle
import matplotlib.pyplot as plt
import akshare as ak
import random
import numpy as np
from decimal import Decimal
from matplotlib import cm
import copy

# Where to buy.
# 使用蒙特卡罗方法琢磨一下在什么时候买入比较合适。

YI_BAI_WAN = Decimal(1000000)
LIANG_BAI_TIAN = 20
YI_WAN_CI = 20000
D_SHI_JIAN = [50, 100, 200, 400, 600]
D_ZHAN_JI = [[-0.1, 0], [0, 0.1], [0.1, 0.2], [0.2, 0.3], [0.3, 1.0]]
SUN_HAO = 0.94 # 年化损耗。
# ----------------------------
TEST_LENGTH = 300 # 测试集长度。 
TRAIN_LENGTH = 2000 # 训练集长度。
TEST_FUND_NUM = 20 # 测试时每次购买的基金数量。
CPU_COST_MAX = 1000 # 最多寻找次数

# 获取所有基金数据。
def get_data():
	# 数据格式为：
	# dict_name: {基金代码: 基金简称, ...}
	# list_date: [2011-09-21, ..., 2021-08-05]
	# list_data: [{基金代码: 当日累计净值, ...}, ...]
	# data_dict: [dict_name, list_date, list_data]
	file = open(r"./210812-akshare_fund_dict.data","rb")
	data = pickle.load(file)
	return data

def save_result(result):
	file = open(r"./where_to_buy_2.result", "wb")
	pickle.dump(result, file)
	file.close()

def load_result():
	file = open(r"./where_to_buy_2.result", "rb")
	result = pickle.load(file)
	return result

# 帮A挑选某日的基金。
def A_choose_fund(the_day, fund_enumerate):
	cpu_cost = 0
	while True:
		cpu_cost += 1
		if cpu_cost > CPU_COST_MAX:
			return -1
		A_fund_index = random.randint(0, len(fund_enumerate) - 1)
		# 活不过两百个交易日的基金不要。
		if fund_enumerate[A_fund_index][1] not in list_data[the_day + LIANG_BAI_TIAN]:
			continue
		return A_fund_index

# 帮D挑选某日的基金。
def D_choose_fund(the_day, fund_enumerate, time, profit):
	cpu_cost = 0
	while True:
		cpu_cost += 1
		if cpu_cost > CPU_COST_MAX:
			return -1
		D_fund_index = random.randint(0, len(fund_enumerate) - 1)
		D_fund = fund_enumerate[D_fund_index][1]
		# 活不过两百个交易日的基金不要。
		if D_fund not in list_data[the_day + LIANG_BAI_TIAN]:
			continue
		# 没有历史数据的不要。
		if D_fund not in list_data[the_day - time]:
			continue
		# 不符合要求的不要。
		real_profit_min = profit[0] / 200 * time # 计算历史持续时间中允许的最小收益。
		real_profit_max = profit[1] / 200 * time # 计算历史持续时间中允许的最大收益。
		the_real_profit = Decimal(list_data[the_day][D_fund]) / Decimal(list_data[the_day - time][D_fund])
		if the_real_profit < 1 + real_profit_min:
			continue
		if the_real_profit > 1 + real_profit_max:
			continue
		# print(cpu_cost)
		return D_fund_index

# 用D的方法推荐基金。
def D_choose_fund_real(the_day, fund_enumerate, time, profit):
	cpu_cost = 0
	while True:
		cpu_cost += 1
		if cpu_cost > CPU_COST_MAX:
			return -1
		D_fund_index = random.randint(0, len(fund_enumerate) - 1)
		D_fund = fund_enumerate[D_fund_index][1]
		# 没有历史数据的不要。
		if D_fund not in list_data[the_day - time]:
			continue
		# 不符合要求的不要。
		real_profit_min = profit[0] / 200 * time # 计算历史持续时间中允许的最小收益。
		real_profit_max = profit[1] / 200 * time # 计算历史持续时间中允许的最大收益。
		the_real_profit = Decimal(list_data[the_day][D_fund]) / Decimal(list_data[the_day - time][D_fund])
		if the_real_profit < 1 + real_profit_min:
			continue
		if the_real_profit > 1 + real_profit_max:
			continue
		# print(cpu_cost)
		return D_fund_index

# 返回可以同一天内买入的基金
def one_day_random():
	while True:
		# A先扔一颗色子决定日期。
		the_day = random.randint(len(list_date) - TRAIN_LENGTH - TEST_LENGTH, \
		     len(list_date) - TEST_LENGTH - LIANG_BAI_TIAN)
		the_funds = fix_day_random_do(the_day)
		if the_funds != -1:
			break
	return the_funds, the_day

# 指定日期，挑选基金，挑不到返回-1。
def fix_day_random_do(the_day):
	# 挑选当日基金
	the_funds = []
	fund_enumerate = list(enumerate(list_data[the_day])) # [(0, 基金代码), ...]
	# 给A随机一个基金。
	A_fund_index = A_choose_fund(the_day, fund_enumerate)
	if A_fund_index == -1:
		return -1
	the_funds.append(fund_enumerate[A_fund_index][1])
	# 给D们随机一个基金。
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			D_fund_index = D_choose_fund(the_day, fund_enumerate, D_SHI_JIAN[i], D_ZHAN_JI[j])
			if D_fund_index == -1:
				return -1
			the_funds.append(fund_enumerate[D_fund_index][1])
	return the_funds

# 正式的比赛。
def real_game(money):
	for i in range(len(money)):
		the_cost = pow(SUN_HAO, float(LIANG_BAI_TIAN) / 200)
		money[i] = money[i] * Decimal(the_cost) # 每年收取的佣金，在0.9115时可保持A的策略资产不变。
	result = []
	# 扔色子决定买入的时间点，以及D买入的基金。
	the_funds, the_day = one_day_random() # the_day 是在 list_date 中的下标。 the_funds 是基金编号。
	end_day = the_day + LIANG_BAI_TIAN
	# A自己策略仍然是持有两百个交易日后卖出。
	A_the_fund = the_funds[0]
	A_fund = Decimal(money[0]) / Decimal(list_data[the_day][A_the_fund])
	A_money = Decimal(A_fund) * Decimal(list_data[end_day][A_the_fund])
	result.append(A_money)
	# D们也是持有两百个交易日后卖出
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			D_the_fund = the_funds[i * len(D_ZHAN_JI) + j + 1]
			D_fund = Decimal(money[i * len(D_ZHAN_JI) + j + 1]) / Decimal(list_data[the_day][D_the_fund])
			D_money = Decimal(D_fund) * Decimal(list_data[end_day][D_the_fund])
			result.append(D_money)
	return result

def game_test(d_i, d_j):
	print('TEST!')
	result = []
	for the_day in range(len(list_date) - TEST_LENGTH, len(list_date) - LIANG_BAI_TIAN):
		end_day = the_day + LIANG_BAI_TIAN
		fund_enumerate = list(enumerate(list_data[the_day])) # [(0, 基金代码), ...]
		one_result = []
		for i in range(TEST_FUND_NUM):
			D_fund_index = D_choose_fund(the_day, fund_enumerate, D_SHI_JIAN[d_i], D_ZHAN_JI[d_j])
			the_fund = fund_enumerate[D_fund_index][1]
			if D_fund_index == -1:
				# print('LOST the test for', list_date[the_day])
				break
			D_profit = Decimal(list_data[end_day][the_fund]) / Decimal(list_data[the_day][the_fund])
			one_result.append(D_profit)
		if (len(one_result)) > 0:
			avg_profit = sum(one_result) / len(one_result)
			avg_annualized = pow(float(avg_profit), 200.0 / LIANG_BAI_TIAN)
			result.append(avg_annualized)
	return result

def show_result(result):
	A_annualized = pow( pow(float(result[0][-1]), 1.0 / YI_WAN_CI), 200.0 / LIANG_BAI_TIAN) / SUN_HAO
	print('result_A:', result[0][-1], ', Annualized:', A_annualized)
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			D_annualized = pow( pow(float(result[i * len(D_ZHAN_JI) + j + 1][-1]), 1.0 / YI_WAN_CI), 200.0 / LIANG_BAI_TIAN) / SUN_HAO
			print('result_D', D_SHI_JIAN[i], D_ZHAN_JI[j], ':', result[i * len(D_ZHAN_JI) + j + 1][-1], \
				 ', Annualized:', D_annualized)
	plt.figure()
	plt.yscale('log')
	# 画线。
	style = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'X']
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			label_str = str(D_SHI_JIAN[i]) + ' days annualized '
			label_str += ' ' + str(D_ZHAN_JI[j][0]) + ' - ' + str(D_ZHAN_JI[j][1])
			color = [1 / len(D_SHI_JIAN) * (i + 1), 1 / len(D_ZHAN_JI) * (j + 1), 0.2, 1]
			the_style = style[(i * len(D_ZHAN_JI) + j) % len(style)]
			plt.plot(result[i * len(D_ZHAN_JI) + j + 1], color = color, linewidth = 2, label = label_str, \
			  marker = the_style, markevery = 0.05, markersize = 10)
	plt.plot(result[0], color='red', linewidth = 5, label='random')
	plt.legend()
	plt.show(block = False)
	plt.pause(1)

def show_test_result(test_result):
	the_sum = 1.0
	for i in range(len(test_result)):
		the_sum *= test_result[i]
	the_avg = pow(the_sum, 1.0 / len(test_result))
	print('The Test Annualized is: ', the_avg)
	plt.figure()
	plt.bar(range(len(test_result)), test_result, color='blue')
	plt.show(block = False)
	plt.pause(1)

def show_which_to_buy(d_i, d_j, the_day):
	fund_enumerate = list(enumerate(list_data[the_day])) # [(0, 基金代码), ...]
	print('You can buy:')
	for i in range(TEST_FUND_NUM):
		D_fund_index = D_choose_fund_real(the_day, fund_enumerate, D_SHI_JIAN[d_i], D_ZHAN_JI[d_j])
		the_fund = fund_enumerate[D_fund_index][1]
		the_fund_name = dict_name[the_fund]
		print(the_fund, the_fund_name)
		if D_fund_index == -1:
			print('Lost the data for today:', list_date[the_day])
			return -1
	return 0



data_dict = get_data()
dict_name = data_dict[0]
list_date = data_dict[1]
list_data = data_dict[2]
# A表示惊讶。
# A表示疑惑。
# A表示难以置信。
# A表示一定是哪里出了问题。
# 可能和时间有关，D的策略有时间倾向性，导致不均匀的时间选择。
# 这在现实中是不能实现的，毕竟D只能在当前进行买入卖出，不能因为过去的选择更多而回到过去。
# 因此，将游戏规则做出一定的改动会更公平。
# 即，每次A和D都在同一个时间点买入。
# 时间点的选择需要能够同时满足A和D的条件，会导致策略A的绝对收益变动，但不会影响A和D之间的相对好坏。
money = []
result = []
for i in range(len(D_SHI_JIAN) * len(D_ZHAN_JI) + 1):
	money.append(YI_BAI_WAN)
	result.append([YI_BAI_WAN])
# 还是重复一万次。
for i in range(YI_WAN_CI):
	if i % 500 == 0:
		print(i)
	money = real_game(money)
	for j in range(len(money)):
		result[j].append(money[j])
# 保存结果
save_result(result)
result = load_result()
# 看看结果。
print('---------------------------------')
show_result(result)
# 选出最佳方案。
print('---------------------------------')
the_end = []
for i in range(len(result)):
	the_end.append(result[i][-1])
the_best = np.argmax(the_end) - 1
print('The best one is:')
d_i = int(the_best / len(D_ZHAN_JI))
d_j = int(the_best % len(D_ZHAN_JI))
D_annualized = pow( pow(float(result[d_i * len(D_ZHAN_JI) + d_j + 1][-1]), 1.0 / YI_WAN_CI), 200.0 / LIANG_BAI_TIAN) / SUN_HAO
print('result_D', D_SHI_JIAN[d_i], D_ZHAN_JI[d_j], ', Annualized:', D_annualized)
print('---------------------------------')
# 使用测试集测试。
test_result = game_test(d_i, d_j)
show_test_result(test_result)
# 开始荐股。 
print('---------------------------------')
the_day = len(list_date) - 1
while show_which_to_buy(d_i, d_j, the_day) == -1:
	the_day -= 1
input("Press Enter to continue...")

# 开方显示收益，直接推荐，排名幅度同时。
# 测试集使用最近一个月数据，每日尝试。


# 20-10000-0.93
# max: # result_C 200 [0.3, 1.0] : 550725188605637903465019749.7 , Annualized: 1.1435574469041072
# result_A: 628.8521026462285254787293279 , Annualized: 1.0822201103917861
# result_C 5 [-0.1, 0] : 0.8774804599871091976658542990 , Annualized: 1.0751282881174613
# result_C 5 [0, 0.1] : 0.3220762293877168091448675394 , Annualized: 1.0740512629468808
# result_C 5 [0.1, 0.2] : 75474.24585817346610909708858 , Annualized: 1.0874138251476613
# result_C 5 [0.2, 0.3] : 20614.33716351029963367799840 , Annualized: 1.0860034897738613
# result_C 5 [0.3, 1.0] : 33897547975.84392108478110709 , Annualized: 1.1016590836092348
# result_C 20 [-0.1, 0] : 0.0005139964946518387707728416113 , Annualized: 1.0671562484111072
# result_C 20 [0, 0.1] : 0.00009409971340329180949943483951 , Annualized: 1.065345902254758
# result_C 20 [0.1, 0.2] : 82.76362300720656735481997240 , Annualized: 1.080027691909146
# result_C 20 [0.2, 0.3] : 120960242.3407283156583870706 , Annualized: 1.0954679957147067
# result_C 20 [0.3, 1.0] : 84564035874139.92203382010418 , Annualized: 1.1103099638114424
# result_C 200 [-0.1, 0] : 1.283249583243314940617338966E-16 , Annualized: 1.036633793888258
# result_C 200 [0, 0.1] : 11.52767345512668524441252852 , Annualized: 1.0779007971735795
# result_C 200 [0.1, 0.2] : 208368192061.1704964892934608 , Annualized: 1.1036614744169635
# result_C 200 [0.2, 0.3] : 181381900454250856126.9356358 , Annualized: 1.1266153013439777
# result_C 200 [0.3, 1.0] : 550725188605637903465019749.7 , Annualized: 1.1435574469041072
# result_C 600 [-0.1, 0] : 793091231678.5116589626408046 , Annualized: 1.105137649542256
# result_C 600 [0, 0.1] : 3937370.370948159533680503560 , Annualized: 1.0917224916213948
# result_C 600 [0.1, 0.2] : 2659799053972120620732229.381 , Annualized: 1.1374751047199827
# result_C 600 [0.2, 0.3] : 183920377092563527732.8531333 , Annualized: 1.126630959349454
# result_C 600 [0.3, 1.0] : 0.09987975888644672667703984843 , Annualized: 1.0727944768341893


# 200-10000-0.93 
# max: # result_D 200 [0.2, 0.3] : 8.716452702596289631699528364E+104 , Annualized: 1.09273052249708
# result_A: 2.943713091708591208041391350E-122 , Annualized: 1.0553948674669535
# result_D 5 [-0.1, 0] : 5.000077693890895326620934516E-117 , Annualized: 1.0562425284487302
# result_D 5 [0, 0.1] : 2.193635422515208641461689388E-146 , Annualized: 1.0514931853707306
# result_D 5 [0.1, 0.2] : 6.797033781713856954834249091E-99 , Annualized: 1.0591867503110786
# result_D 5 [0.2, 0.3] : 8.680858831725370504939187149E-54 , Annualized: 1.0665460762147785
# result_D 5 [0.3, 1.0] : 3.712418519353519945753987831E-25 , Annualized: 1.071243899948939
# result_D 20 [-0.1, 0] : 2.052635145169502593063034831E-90 , Annualized: 1.0605664200084257
# result_D 20 [0, 0.1] : 2.383062978922594413350583156E-109 , Annualized: 1.057488193074036
# result_D 20 [0.1, 0.2] : 2.201568880909644413809348611E-48 , Annualized: 1.067431218670672
# result_D 20 [0.2, 0.3] : 0.04954937093014879710594129865 , Annualized: 1.0750534419515316
# result_D 20 [0.3, 1.0] : 2.687904359470881378524820753E+54 , Annualized: 1.0842905656873911
# result_D 200 [-0.1, 0] : 1.182345693395023017639725633E-109 , Annualized: 1.0574387822970066
# result_D 200 [0, 0.1] : 1.136567961646395330867862633E-101 , Annualized: 1.058735375695232
# result_D 200 [0.1, 0.2] : 6.526423083914822842549028391E+55 , Annualized: 1.0845211596973556
# result_D 200 [0.2, 0.3] : 8.716452702596289631699528364E+104 , Annualized: 1.09273052249708
# result_D 200 [0.3, 1.0] : 1.189827274735326192500208913E-13 , Annualized: 1.073137613186092
# result_D 600 [-0.1, 0] : 1.177846086498879121973988357E-152 , Annualized: 1.0504816182501617
# result_D 600 [0, 0.1] : 1.838420958756789341158351440E-129 , Annualized: 1.0542283260999468
# result_D 600 [0.1, 0.2] : 3422837583043142485925.823488 , Annualized: 1.0788291614465342
# result_D 600 [0.2, 0.3] : 1.820269613368583015186099744E-15 , Annualized: 1.0728386076181566
# result_D 600 [0.3, 1.0] : 4.001380196678809909757946763E-61 , Annualized: 1.0653456381934483

