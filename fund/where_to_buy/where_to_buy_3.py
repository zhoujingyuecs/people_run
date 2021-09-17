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
LIANG_BAI_TIAN = 200
YI_WAN_CI = 30000
D_SHI_JIAN = [10, 20, 40, 50, 60, 70, 80, 100, 200]
D_ZHAN_JI = [[0, 0.001], [0, 0.005], [0, 0.01], [0, 0.05], [0, 0.1]]
SUN_HAO = 0.80 # 年化损耗。
# ----------------------------
TEST_LENGTH = 1000 # 测试集长度。 
TRAIN_LENGTH = 3000 # 训练集长度。
TEST_FUND_NUM = 30 # 测试时每次购买的基金数量。
CPU_COST_MAX = 1000 # 最多寻找次数。
# ----------------------------
THE_FILE_NAME = r"210917"
DATA_FILE = r"../" + THE_FILE_NAME + r"-akshare_fund-dict.data"
MODULE_FILE = r"./" + THE_FILE_NAME + r"-where_to_buy_3.result"
D_CACHE_FILE = r"./" + THE_FILE_NAME + r"-where_to_buy_3_D_cache.data"

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

def save_file(file_name, result):
	file = open(file_name, "wb")
	pickle.dump(result, file)
	file.close()

def load_file(file_name):
	file = open(file_name, "rb")
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
# def D_choose_fund(the_day, fund_enumerate, time, profit, is_real = False):
def D_choose_fund(the_day, fund_enumerate, D_i, D_j, is_real = False):
	cpu_cost = 0
	while True:
		cpu_cost += 1
		if cpu_cost > CPU_COST_MAX:
			return -1
		D_fund_index = random.randint(0, len(fund_enumerate) - 1)
		D_fund = fund_enumerate[D_fund_index][1]
		# 在训练时活不过两百个交易日的基金不要。
		if (is_real == False) and (D_fund not in list_data[the_day + LIANG_BAI_TIAN]):
			continue
		# 没有历史数据的不要。
		if D_fund not in list_data[the_day - D_SHI_JIAN[D_i]]:
			continue
		# 不符合要求的不要。
		if D_cache[D_i][the_day][D_fund] > D_ZHAN_JI[D_j][1]:
			continue
		if D_cache[D_i][the_day][D_fund] < D_ZHAN_JI[D_j][0]:
			continue
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
			D_fund_index = D_choose_fund(the_day, fund_enumerate, i, j)
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
			D_fund_index = D_choose_fund(the_day, fund_enumerate, d_i, d_j)
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
		D_fund_index = D_choose_fund(the_day, fund_enumerate, d_i, d_j, is_real = True)
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
	save_file(MODULE_FILE, result)

def get_D_cache():
	D_cache = []
	for i in range(len(D_SHI_JIAN)):
		print(i)
		one_D_cache = []
		for j in range(len(list_data)):
			dic_sort = {}
			list_return = [] # [[基金代码, 期间收益率], ...(当日基金数)]
			for k in list_data[j]:
				if (j - D_SHI_JIAN[i] < 0) or (k not in list_data[j - D_SHI_JIAN[i]]):
					dic_sort[k] = -1
					continue
				one_list_return = []
				one_list_return.append(k)
				one_list_return.append( Decimal(list_data[j][k]) / Decimal(list_data[j - D_SHI_JIAN[i]][k]) )
				list_return.append(one_list_return)
			list_return_sorted = sorted(list_return, key = lambda x: x[1], reverse = True)
			fun_mun = len(list_return_sorted)
			for k in range(fun_mun):
				dic_sort[list_return_sorted[k][0]] = float(k) / fun_mun
			one_D_cache.append(dic_sort)
		D_cache.append(one_D_cache)
	save_file(D_CACHE_FILE, D_cache)

data_dict = get_data()
dict_name = data_dict[0]
list_date = data_dict[1]
list_data = data_dict[2]
# 按照收益率排名，然后选择固定段位的基金。
# 存储排名的数据结构。
# D_cache: [[{基金代码: 当日排名, ...(当日基金数)}, ...(日期数)], ...(D_SHI_JIAN数量)]
# get_D_cache()
D_cache = load_file(D_CACHE_FILE)
# ------------------
# train()
# ------------------
result = load_file(MODULE_FILE)
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



# YI_BAI_WAN = Decimal(1000000)
# LIANG_BAI_TIAN = 200
# YI_WAN_CI = 30000
# D_SHI_JIAN = [10, 20, 40, 50, 60, 70, 80, 100, 200]
# D_ZHAN_JI = [[0, 0.001], [0, 0.005], [0, 0.01], [0, 0.05], [0, 0.1]]
# SUN_HAO = 0.80 # 年化损耗。
# # ----------------------------
# TEST_LENGTH = 1000 # 测试集长度。 
# TRAIN_LENGTH = 3000 # 训练集长度。
# TEST_FUND_NUM = 30 # 测试时每次购买的基金数量。
# CPU_COST_MAX = 1000 # 最多寻找次数。
# # ----------------------------
# THE_FILE_NAME = r"210917"
# DATA_FILE = r"../" + THE_FILE_NAME + r"-akshare_fund-dict.data"
# MODULE_FILE = r"./" + THE_FILE_NAME + r"-where_to_buy_3.result"
# D_CACHE_FILE = r"./" + THE_FILE_NAME + r"-where_to_buy_3_D_cache.data"
# ---------------------------------
# result_A: 1.430189753325643482476391902E-656 , Annualized: 0.0
# result_D 10 [0, 0.001] : 8.902232777079573491355119414E-230 , Annualized: 1.2282166947397362
# result_D 10 [0, 0.005] : 2.882631819867553425692437436E-222 , Annualized: 1.228924887247943
# result_D 10 [0, 0.01] : 1.681939402629794369028655403E-215 , Annualized: 1.2295632475880016
# result_D 10 [0, 0.05] : 1.212954852971198390122597185E-239 , Annualized: 1.2272870202653758
# result_D 10 [0, 0.1] : 1.835435241506880118274845193E-266 , Annualized: 1.2247632249315228
# result_D 20 [0, 0.001] : 1.633429146328730135218735892E-188 , Annualized: 1.2321127442538424
# result_D 20 [0, 0.005] : 1.532728932535868729074648949E-161 , Annualized: 1.2346661129493381
# result_D 20 [0, 0.01] : 2.473647361691547325391315090E-127 , Annualized: 1.2379120514143154
# result_D 20 [0, 0.05] : 8.906478297396080154542411354E-160 , Annualized: 1.2348333109937097
# result_D 20 [0, 0.1] : 2.052900565669949640986818543E-207 , Annualized: 1.2303266328531914
# result_D 40 [0, 0.001] : 4.268344621543137472354609036E+120 , Annualized: 1.2616271363263336
# result_D 40 [0, 0.005] : 9.096886635913023560689248154E+112 , Annualized: 1.2608845099872918
# result_D 40 [0, 0.01] : 9.628027002941430454864995911E+35 , Annualized: 1.253457069927836
# result_D 40 [0, 0.05] : 9.785435495701429546968776232E-28 , Annualized: 1.2474113721249653
# result_D 40 [0, 0.1] : 1.036381045630069085247230227E-100 , Annualized: 1.240444097734981
# result_D 50 [0, 0.001] : 1.431986027095689612661951587E+208 , Annualized: 1.2701310829125712
# result_D 50 [0, 0.005] : 7.032577367205832147504015030E+220 , Annualized: 1.2713688997132382
# result_D 50 [0, 0.01] : 1.760163202416697613970000225E+138 , Annualized: 1.263334039789788
# result_D 50 [0, 0.05] : 4.251469300728052911876459212E-44 , Annualized: 1.2458458149230653
# result_D 50 [0, 0.1] : 1.445977081597399247025832646E-91 , Annualized: 1.2413150427870587
# result_D 60 [0, 0.001] : 5.689887572449222417133575624E+152 , Annualized: 1.2647417343947533
# result_D 60 [0, 0.005] : 5.205941544254605096262489323E+205 , Annualized: 1.2698932935777099
# result_D 60 [0, 0.01] : 3.839251292550389625538420278E+170 , Annualized: 1.2664736388713294
# result_D 60 [0, 0.05] : 2.167301353778917816311824114E-11 , Annualized: 1.248977295546218
# result_D 60 [0, 0.1] : 7.010271994633229881944670080E-98 , Annualized: 1.2407135850285955
# result_D 70 [0, 0.001] : 1.083185220009545351868727534E+95 , Annualized: 1.2591510629324372
# result_D 70 [0, 0.005] : 5.546921629706412513315177818E+153 , Annualized: 1.2648377377417512
# result_D 70 [0, 0.01] : 3.169179853420635636425499680E+123 , Annualized: 1.2619051455505803
# result_D 70 [0, 0.05] : 6.885429854192641124189831347E-46 , Annualized: 1.2456746048130396
# result_D 70 [0, 0.1] : 4.993654427627397863520940706E-76 , Annualized: 1.2427963248075495
# result_D 80 [0, 0.001] : 2.320631989340543347400794284E+110 , Annualized: 1.2606335658676995
# result_D 80 [0, 0.005] : 2.875707100753902948528352334E+150 , Annualized: 1.2645188406900811
# result_D 80 [0, 0.01] : 3.311845565329710626606745442E+96 , Annualized: 1.259294622089836
# result_D 80 [0, 0.05] : 1.172865990340359475063497789E-65 , Annualized: 1.2437859728372809
# result_D 80 [0, 0.1] : 4.964663758812472199754831378E-85 , Annualized: 1.2419378869289077
# result_D 100 [0, 0.001] : 3.379736057734953206849233474E+110 , Annualized: 1.2606493641449852
# result_D 100 [0, 0.005] : 2.646980771977743874203289184E+169 , Annualized: 1.2663607401933585
# result_D 100 [0, 0.01] : 1.459658403479500316670734178E+192 , Annualized: 1.2685730710027587
# result_D 100 [0, 0.05] : 3.934140141435417983278903955E-91 , Annualized: 1.2413564581779513
# result_D 100 [0, 0.1] : 2.416318038282053359825155752E-163 , Annualized: 1.2344953303103345
# result_D 200 [0, 0.001] : 1.098830102717651467232787318E-188 , Annualized: 1.2320964625868251
# result_D 200 [0, 0.005] : 1.957071679912506623962458349E-212 , Annualized: 1.2298526083990906
# result_D 200 [0, 0.01] : 1.007257639609505915286553421E-351 , Annualized: 0.0
# result_D 200 [0, 0.05] : 4.615952372611349603463413223E-388 , Annualized: 0.0
# result_D 200 [0, 0.1] : 9.276831587482734810598702484E-572 , Annualized: 0.0
# ---------------------------------
# The best one is:
# result_D 50 [0, 0.005] , Annualized: 1.2713688997132382
# ---------------------------------
# You can buy:
# 001300 大成睿景灵活配置混合A
# 007689 国投瑞银新能源混合A
# 012810 鹏华国证钢铁行业指数(LOF)C
# 290014 泰信现代服务业混合
# 002667 前海开源沪港深创新成长混合C
# 161715 招商大宗商品(LOF)
# 010085 蜂巢丰瑞债券C
# 010826 大成产业趋势混合A
# 008190 国泰中证钢铁ETF联接C
# 011707 东吴配置优化混合C
# 004475 华泰柏瑞富利混合
# 007690 国投瑞银新能源混合C
# 012891 安信鑫发优选混合C
# 090018 大成新锐产业混合
# 590003 中邮核心优势灵活配置混合
# 011129 华安精致生活混合C
# 011128 华安精致生活混合A
# 011251 华安聚嘉精选混合A
# 000729 建信中小盘先锋股票
# 010827 大成产业趋势混合C
# 010963 信达澳银周期动力混合
# 010084 蜂巢丰瑞债券A
# 008189 国泰中证钢铁ETF联接A
# 002258 大成国企改革灵活配置混合
# 008280 国泰中证煤炭ETF联接C
# 002601 中银证券价值精选混合
# 003175 华泰柏瑞多策略混合
# 160620 鹏华中证A股资源产业指数(LOF)A
# 006736 国投瑞银先进制造混合
# 009999 东方中国红利混合
# 050024 博时上证自然资源ETF联接
# 582003 东吴配置优化混合A
# 167503 安信中证一带一路主题指数
# 002666 前海开源沪港深创新成长混合A
# 519183 万家双引擎灵活配置混合
# 012808 鹏华中证A股资源产业指数(LOF)C
# 168204 中融中证煤炭指数(LOF)
# 011252 华安聚嘉精选混合C
# 001301 大成睿景灵活配置混合C
# 000433 安信鑫发优选混合A
# And hold 200 days.
# ---------------------------------
# TEST!
# BASE TEST!
# The Test Annualized is:  1.1643671158097384
# 429 times in 534 win, the win rate is:  0.8033707865168539
# The Base Annualized is:  1.0989062274521924
# 598 times in 693 win, the win rate is:  0.862914862914863

