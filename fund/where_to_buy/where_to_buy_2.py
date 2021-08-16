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
LIANG_BAI_TIAN = 40
YI_WAN_CI = 30000
D_SHI_JIAN = [50, 100, 200, 300, 400, 500, 600]
D_ZHAN_JI = [[-0.1, 0], [0, 0.1], [0.1, 0.2], [0.15, 0.25], [0.2, 0.3], [0.3, 1.0]]
SUN_HAO = 0.93 # 年化损耗。
# ----------------------------
TEST_LENGTH = 1000 # 测试集长度。 
TRAIN_LENGTH = 3000 # 训练集长度。
TEST_FUND_NUM = 30 # 测试时每次购买的基金数量。
CPU_COST_MAX = 1000 # 最多寻找次数
# ----------------------------
DATA_FILE = r"../210812-akshare_fund_dict.data"
MODULE_FILE = r"./where_to_buy_2-40-1000-3000.result"

# 获取所有基金数据。
def get_data():
	# 数据格式为：
	# dict_name: {基金代码: 基金简称, ...}
	# list_date: [2011-09-21, ..., 2021-08-05]
	# list_data: [{基金代码: 当日累计净值, ...}, ...]
	# data_dict: [dict_name, list_date, list_data]
	file = open(DATA_FILE, "rb")
	data = pickle.load(file)
	return data

def save_result(result):
	file = open(MODULE_FILE, "wb")
	pickle.dump(result, file)
	file.close()

def load_result():
	file = open(MODULE_FILE, "rb")
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
	test_day = []
	for the_day in range(len(list_date) - TEST_LENGTH, len(list_date) - LIANG_BAI_TIAN):
		end_day = the_day + LIANG_BAI_TIAN
		fund_enumerate = list(enumerate(list_data[the_day])) # [(0, 基金代码), ...]
		one_result = []
		for i in range(TEST_FUND_NUM):
			D_fund_index = D_choose_fund(the_day, fund_enumerate, D_SHI_JIAN[d_i], D_ZHAN_JI[d_j])
			if D_fund_index == -1:
				# print('LOST the test for', list_date[the_day])
				break
			the_fund = fund_enumerate[D_fund_index][1]
			D_profit = Decimal(list_data[end_day][the_fund]) / Decimal(list_data[the_day][the_fund])
			one_result.append(D_profit)
		if (len(one_result)) == TEST_FUND_NUM:
			avg_profit = sum(one_result) / len(one_result)
			avg_annualized = pow(float(avg_profit), 200.0 / LIANG_BAI_TIAN)
			result.append(avg_annualized)
			test_day.append(the_day)
	return result, test_day

def base_game_test():
	print('BASE TEST!')
	result = []
	test_day = []
	for the_day in range(len(list_date) - TEST_LENGTH, len(list_date) - LIANG_BAI_TIAN):
		end_day = the_day + LIANG_BAI_TIAN
		fund_enumerate = list(enumerate(list_data[the_day])) # [(0, 基金代码), ...]
		one_result = []
		for i in range(TEST_FUND_NUM):
			A_fund_index = A_choose_fund(the_day, fund_enumerate)
			if A_fund_index == -1:
				# print('LOST the test for', list_date[the_day])
				break
			the_fund = fund_enumerate[A_fund_index][1]
			A_profit = Decimal(list_data[end_day][the_fund]) / Decimal(list_data[the_day][the_fund])
			one_result.append(A_profit)
		if (len(one_result)) == TEST_FUND_NUM:
			avg_profit = sum(one_result) / len(one_result)
			avg_annualized = pow(float(avg_profit), 200.0 / LIANG_BAI_TIAN)
			result.append(avg_annualized)
			test_day.append(the_day)
	return result, test_day

def show_result(result):
	A_annualized = pow( pow(float(result[0][-1]), 1.0 / YI_WAN_CI), 200.0 / LIANG_BAI_TIAN) / SUN_HAO
	print('result_A:', result[0][-1], ', Annualized:', A_annualized)
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			D_annualized = pow( pow(float(result[i * len(D_ZHAN_JI) + j + 1][-1]), 1.0 / YI_WAN_CI), 200.0 / LIANG_BAI_TIAN) / SUN_HAO
			print('result_D', D_SHI_JIAN[i], D_ZHAN_JI[j], ':', result[i * len(D_ZHAN_JI) + j + 1][-1], \
				 ', Annualized:', D_annualized)
	# 画线。
	# plt.figure()
	# plt.yscale('log')
	# style = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'X']
	# for i in range(len(D_SHI_JIAN)):
	# 	for j in range(len(D_ZHAN_JI)):
	# 		label_str = str(D_SHI_JIAN[i]) + ' days annualized '
	# 		label_str += ' ' + str(D_ZHAN_JI[j][0]) + ' - ' + str(D_ZHAN_JI[j][1])
	# 		color = [1 / len(D_SHI_JIAN) * (i + 1), 1 / len(D_ZHAN_JI) * (j + 1), 0.2, 1]
	# 		the_style = style[(i * len(D_ZHAN_JI) + j) % len(style)]
	# 		plt.plot(result[i * len(D_ZHAN_JI) + j + 1], color = color, linewidth = 2, label = label_str, \
	# 		  marker = the_style, markevery = 0.05, markersize = 10)
	# plt.plot(result[0], color='red', linewidth = 5, label='random')
	# plt.legend()
	# plt.show()

def show_test_result(test_result, test_day, A_test_result, A_test_day):
	# 输出D的统计信息。
	the_sum = 1.0
	the_win = 0
	for i in range(len(test_result)):
		the_sum *= test_result[i]
		if test_result[i] > 1:
			the_win += 1
	the_avg = pow(the_sum, 1.0 / len(test_result))
	print('The Test Annualized is: ', the_avg)
	print(the_win, 'times in', len(test_result), 'win, the win rate is: ', float(the_win) / len(test_result))
	# 输出A（基准）的统计信息。
	the_sum = 1.0
	the_win = 0
	for i in range(len(A_test_result)):
		the_sum *= A_test_result[i]
		if A_test_result[i] > 1:
			the_win += 1
	the_avg = pow(the_sum, 1.0 / len(A_test_result))
	print('The Base Annualized is: ', the_avg)
	print(the_win, 'times in', len(A_test_result), 'win, the win rate is: ', float(the_win) / len(A_test_result))
	# 绘图。
	plt.figure()
	plt.plot(test_day, test_result, color='blue', label = 'plan D')
	plt.plot(A_test_day, A_test_result, color='red', label = 'plan A')
	plt.plot(A_test_day, [1] * len(A_test_result), color='black') 
	plt.plot(A_test_day, [1.2] * len(A_test_result), color='green') 
	x_index = []
	x_value = []
	space = int(len(test_day) / 10)
	for i in range(len(test_day)):
		if i % space == 0:
			x_index.append(test_day[i])
			x_value.append(list_date[test_day[i]])
	plt.xticks(x_index, x_value)
	plt.legend()
	plt.show()
	# plt.show(block = False)
	# plt.pause(1)

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
	print('And hold', LIANG_BAI_TIAN, 'days.')
	return 0

def train():
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
# ------------------
# train()
# ------------------
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
# 开始荐股。 
print('---------------------------------')
the_day = len(list_date) - 1
while show_which_to_buy(d_i, d_j, the_day) == -1:
	the_day -= 1
# 使用测试集测试。
print('---------------------------------')
test_result, test_day = game_test(d_i, d_j)
A_test_result, A_test_day = base_game_test()
show_test_result(test_result, test_day, A_test_result, A_test_day)
# input("Press Enter to continue...")

# YI_BAI_WAN = Decimal(1000000)
# LIANG_BAI_TIAN = 20
# YI_WAN_CI = 20000
# D_SHI_JIAN = [50, 100, 200, 400, 600]
# D_ZHAN_JI = [[-0.1, 0], [0, 0.1], [0.1, 0.2], [0.2, 0.3], [0.3, 1.0]]
# SUN_HAO = 0.94 # 年化损耗。
# # ----------------------------
# TEST_LENGTH = 300 # 测试集长度。 
# TRAIN_LENGTH = 2000 # 训练集长度。
# TEST_FUND_NUM = 30 # 测试时每次购买的基金数量。
# CPU_COST_MAX = 1000 # 最多寻找次数
# ---------------------------------
# result_A: 0.0001032281121236310776516036169 , Annualized: 1.0589587553265243
# result_D 50 [-0.1, 0] : 10536767.44634003132854170955 , Annualized: 1.07246591925654
# result_D 50 [0, 0.1] : 76390091.83256389452617996732 , Annualized: 1.0735287134605016
# result_D 50 [0.1, 0.2] : 302803313483295449.0550960020 , Annualized: 1.0854572574461578
# result_D 50 [0.2, 0.3] : 3664903734246962034429.019571 , Annualized: 1.0905715844808166
# result_D 50 [0.3, 1.0] : 1387036930960836243.929770326 , Annualized: 1.086283518761012
# result_D 100 [-0.1, 0] : 1.519972783327030739032067550E-50 , Annualized: 1.00453035377149
# result_D 100 [0, 0.1] : 1.792409842591400361780422815E-15 , Annualized: 1.045920957159434
# result_D 100 [0.1, 0.2] : 1.361091683388269888531881867E-26 , Annualized: 1.0326165708731707
# result_D 100 [0.2, 0.3] : 5.235306672510146438118086383E-24 , Annualized: 1.035694374819274
# result_D 100 [0.3, 1.0] : 7.903613346935958630376044136E-10 , Annualized: 1.0527398412362907
# result_D 200 [-0.1, 0] : 4.047309635646517854037717825E-36 , Annualized: 1.0213526724839312
# result_D 200 [0, 0.1] : 4784.575998790836037307777214 , Annualized: 1.068346343958671
# result_D 200 [0.1, 0.2] : 71544333916932602.71036911848 , Annualized: 1.0846745093154941
# result_D 200 [0.2, 0.3] : 16384082845090883276592783.23 , Annualized: 1.095164499661426
# result_D 200 [0.3, 1.0] : 3438015528349568472127343.573 , Annualized: 1.0943098297072367
# result_D 400 [-0.1, 0] : 152761322932611166.7042970331 , Annualized: 1.0850859823702719
# result_D 400 [0, 0.1] : 852832553139647078.8124221244 , Annualized: 1.0860193874626183
# result_D 400 [0.1, 0.2] : 1.840683223777773540206638774E+50 , Annualized: 1.1272094886411224
# result_D 400 [0.2, 0.3] : 3.401498323309085127876570313E+61 , Annualized: 1.141926053131528
# result_D 400 [0.3, 1.0] : 3.927814955948733899121101786E-8 , Annualized: 1.0547978160275964
# result_D 600 [-0.1, 0] : 7717601374358753.035915179923 , Annualized: 1.0834674973595242
# result_D 600 [0, 0.1] : 2018386867802.749769763175209 , Annualized: 1.0790079601426392
# result_D 600 [0.1, 0.2] : 1.783855646739150862595658932E+45 , Annualized: 1.120721816646478
# result_D 600 [0.2, 0.3] : 9.748843660209453396563999419E+29 , Annualized: 1.101201065543326
# result_D 600 [0.3, 1.0] : 1.624867264311455586143677266E-10 , Annualized: 1.051907509072279
# findfont: Font family ['sans-serif'] not found. Falling back to DejaVu Sans.
# ---------------------------------
# The best one is:
# result_D 400 [0.2, 0.3] , Annualized: 1.141926053131528
# ---------------------------------
# TEST!
# BASE TEST!
# The Test Annualized is:  1.2172442944720956
# 196 times in 255 win, the win rate is:  0.7686274509803922
# The Base Annualized is:  1.1088205367155777
# 205 times in 267 win, the win rate is:  0.7677902621722846
# ---------------------------------
# You can buy:
# 519995 长信金利趋势混合
# Lost the data for today: 2021-08-11
# You can buy:
# 050012 博时策略混合
# 720001 财通价值动量混合
# 002906 南方中证500量化增强A
# 006063 景顺长城MSCI中国A股国际通
# 002424 博时文体娱乐主题混合
# 003434 博时鑫泽灵活配置混合A
# 000556 国投瑞银新机遇灵活配置混合A
# 006048 长城中证500指数增强A
# 001256 泓德优选成长混合
# 008084 海富通先进制造股票C
# 008477 安信价值驱动三年持有混合
# 005437 易方达易百智能量化策略A
# 001618 天弘中证电子ETF联接C
# 519697 交银优势行业混合
# 162208 泰达宏利首选企业股票
# 160921 大成多策略混合(LOF)
# 202017 南方深证成份ETF联接A
# 560002 益民红利成长混合
# 003884 汇安沪深300指数增强A
# 000457 上投摩根核心成长股票
# 161038 富国新兴成长量化精选混合
# 001357 泓德泓富混合A
# 006783 红土创新中证500增强A
# 005225 广发量化多因子混合
# 006449 浙商汇金量化精选混合
# 004206 华商元亨灵活配置混合
# 001607 英大策略优选A
# 373020 上投摩根双核平衡混合
# 000165 国投瑞银策略精选混合
# 004481 华宝第三产业混合A




# YI_BAI_WAN = Decimal(1000000)
# LIANG_BAI_TIAN = 40
# YI_WAN_CI = 30000
# D_SHI_JIAN = [50, 100, 200, 300, 400, 500, 600]
# D_ZHAN_JI = [[-0.1, 0], [0, 0.1], [0.1, 0.2], [0.15, 0.25], [0.2, 0.3], [0.3, 1.0]]
# SUN_HAO = 0.93 # 年化损耗。
# # ----------------------------
# TEST_LENGTH = 1000 # 测试集长度。 
# TRAIN_LENGTH = 3000 # 训练集长度。
# TEST_FUND_NUM = 30 # 测试时每次购买的基金数量。
# CPU_COST_MAX = 1000 # 最多寻找次数
# # ----------------------------
# DATA_FILE = r"../210812-akshare_fund_dict.data"
# MODULE_FILE = r"./where_to_buy_2-40-1000-3000.result"
# ---------------------------------
# result_A: 3.654191147858240946655060816E+44 , Annualized: 1.0938157771371366
# result_D 50 [-0.1, 0] : 319916959161817821335006028.9 , Annualized: 1.086261926206186
# result_D 50 [0, 0.1] : 1.217637361016397162851768099E+28 , Annualized: 1.0869209785467804
# result_D 50 [0.1, 0.2] : 1.290127770617591800311771782E+80 , Annualized: 1.1088398452568915
# result_D 50 [0.15, 0.25] : 9.423662125880884217081631733E+78 , Annualized: 1.1083563694309775
# result_D 50 [0.2, 0.3] : 1.508604936399231139541541805E+88 , Annualized: 1.1122783416606183
# result_D 50 [0.3, 1.0] : 0.000007527349439735362727830217494 , Annualized: 1.07315674232888
# result_D 100 [-0.1, 0] : 4.733186814586316163907082985E-153 , Annualized: 1.0142139436942312
# result_D 100 [0, 0.1] : 3.873973817184645194590798624E-57 , Annualized: 1.0522406552729127
# result_D 100 [0.1, 0.2] : 1.729470503011940192971716800E-78 , Annualized: 1.0436543885210958
# result_D 100 [0.15, 0.25] : 3.123353308267307994488657056E-93 , Annualized: 1.037766120336091
# result_D 100 [0.2, 0.3] : 1.037034098421206264612705826E-92 , Annualized: 1.0379737017038722
# result_D 100 [0.3, 1.0] : 6.484662039615276875201512889E-28 , Annualized: 1.064107978175369
# result_D 200 [-0.1, 0] : 0.0001256749039195982532799970897 , Annualized: 1.0736603776486577
# result_D 200 [0, 0.1] : 9.350714351335854374003035059E+41 , Annualized: 1.0927283036633475
# result_D 200 [0.1, 0.2] : 9.489978241978346243069720120E+99 , Annualized: 1.1173260620915055
# result_D 200 [0.15, 0.25] : 4.688731515208233704349212036E+101 , Annualized: 1.1180525779969486
# result_D 200 [0.2, 0.3] : 3.965834463467097299047851281E+83 , Annualized: 1.1103249712145078
# result_D 200 [0.3, 1.0] : 5.828514461949432500546819532E+84 , Annualized: 1.1108224399188376
# result_D 300 [-0.1, 0] : 6.622736075533941362189325745E+135 , Annualized: 1.1328016972015622
# result_D 300 [0, 0.1] : 2.069354251508315713615472303E+83 , Annualized: 1.1102046037659583
# result_D 300 [0.1, 0.2] : 5.962094786023054450977104671E+206 , Annualized: 1.1640713965570808
# result_D 300 [0.15, 0.25] : 4.306891531463554392345078480E+279 , Annualized: 1.1970788160514023
# result_D 300 [0.2, 0.3] : 7.112196058347767003420935891E+287 , Annualized: 1.2008600178322149
# result_D 300 [0.3, 1.0] : 4.592585944988302679709687155E+62 , Annualized: 1.1014397041570896
# result_D 400 [-0.1, 0] : 1.529835472305228068497956282E+211 , Annualized: 1.1660428015860038
# result_D 400 [0, 0.1] : 1.206437568814178852823452796E+107 , Annualized: 1.1203764433513024
# result_D 400 [0.1, 0.2] : 1.112498457791398235069092671E+256 , Annualized: 1.1862915438968493
# result_D 400 [0.15, 0.25] : 9.411293385329161479471226452E+285 , Annualized: 1.1999946956398635
# result_D 400 [0.2, 0.3] : 1.676616852558818851688044129E+229 , Annualized: 1.1741433527531917
# result_D 400 [0.3, 1.0] : 158423313193308414269053804.2 , Annualized: 1.0861346978407704
# result_D 500 [-0.1, 0] : 3.373615904979507879770916572E+271 , Annualized: 1.1933607070992553
# result_D 500 [0, 0.1] : 2.957966710012536251781083840E+75 , Annualized: 1.106867282112917
# result_D 500 [0.1, 0.2] : 5.600241402388781054393345835E+245 , Annualized: 1.1816125252404002
# result_D 500 [0.15, 0.25] : 3.533414996495311826889092219E+217 , Annualized: 1.16889387755621
# result_D 500 [0.2, 0.3] : 3.778771213065275204787671456E+154 , Annualized: 1.140985021607758
# result_D 500 [0.3, 1.0] : 1.813324295046329815265566119E+81 , Annualized: 1.109328397843445
# result_D 600 [-0.1, 0] : 4.836542911854525230861292510E+135 , Annualized: 1.1327423572413955
# result_D 600 [0, 0.1] : 3.910077813705311478486958957E+76 , Annualized: 1.1073436401102763
# result_D 600 [0.1, 0.2] : 3.654604853743124312007296969E+201 , Annualized: 1.1617451235218796
# result_D 600 [0.15, 0.25] : 1.311158314659559869397676205E+178 , Annualized: 1.1513392949872863
# result_D 600 [0.2, 0.3] : 1.133325768030754465251669582E+130 , Annualized: 1.130297526582025
# result_D 600 [0.3, 1.0] : 3.132636177045854969791703152E+77 , Annualized: 1.1077277524426892
# ---------------------------------
# The best one is:
# result_D 300 [0.2, 0.3] , Annualized: 1.2008600178322149
# ---------------------------------
# You can buy:
# 005146 兴银丰润灵活配置混合
# 001305 九泰天富改革混合A
# 050111 博时信用债券C
# 003131 国寿安保强国智造混合
# 004875 融通深证成份指数C
# 002778 新疆前海联合新思路混合A
# 540007 汇丰晋信中小盘股票
# 004453 前海开源盈鑫A
# 202021 南方小康ETF联接A
# 004653 建信鑫利回报灵活配置混合C
# 005919 天弘中证500ETF联接C
# 008397 博时中证500ETF联接C
# 004726 先锋聚优A
# 004194 招商中证1000指数增强A
# 007032 平安可转债债券A
# 163821 中银沪深300等权重指数
# 002031 华夏策略混合
# 006887 诺德新生活混合A
# 008998 同泰竞争优势混合C
# 007797 博时央企创新驱动ETF联接C
# 001174 中欧瑾和灵活配置混合C
# 001874 前海开源沪港深价值精选混合
# 373020 上投摩根双核平衡混合
# 160813 长盛同盛成长优选(LOF)
# 005618 融通红利机会主题精选混合A
# 160616 鹏华中证500指数(LOF)A
# 001357 泓德泓富混合A
# 470028 汇添富社会责任混合
# 001411 诺安创新驱动混合A
# 008270 大成睿享混合C
# And hold 40 days.
# ---------------------------------
# TEST!
# BASE TEST!
# The Test Annualized is:  1.1351962171314733
# 445 times in 675 win, the win rate is:  0.6592592592592592
# The Base Annualized is:  1.078754429493064
# 596 times in 934 win, the win rate is:  0.6381156316916489
# findfont: Font family ['sans-serif'] not found. Falling back to DejaVu Sans.
