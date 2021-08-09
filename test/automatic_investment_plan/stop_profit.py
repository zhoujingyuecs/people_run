import pickle
import matplotlib.pyplot as plt
from matplotlib import cm
import akshare as ak
import random
import numpy as np
from decimal import Decimal

# Stop profit.
# 使用蒙特卡罗方法比较止盈策略和不止盈策略的优劣。

YI_BAI_WAN = Decimal(1000000)
LIANG_BAI_TIAN = 200
C1_ZHI_YING_DIAN = 1.1
C2_ZHI_YING_DIAN = 1.2
C3_ZHI_YING_DIAN = 1.3
C4_ZHI_YING_DIAN = 1.6
C5_ZHI_YING_DIAN = 1.9
YI_WAN_CI = 10000

# 获取所有基金数据。
def get_data():
	# 数据格式为：
	# data = [ [基金代码, 基金简称, [累计净值走势]], ... ]
	# ----------------------------
	# 其中，[累计净值走势]的格式为：
	#             净值日期    累计净值
	# 0     2011-09-21  1.0000
	# 1     2011-09-23  1.0000
	# 2     2011-09-30  1.0001
	# 3     2011-10-14  1.0005
	# 4     2011-10-21  1.0007
	# ...          ...     ...
	# 2389  2021-07-30  3.5952
	# 2390  2021-08-02  3.6250
	# 2391  2021-08-03  3.5642
	# 2392  2021-08-04  3.6691
	# 2393  2021-08-05  3.6751
	# <class 'pandas.core.frame.DataFrame'>
	file = open(r"./akshare_fund-11420.data","rb")
	data = pickle.load(file)
	# 清除有空值的基金。
	clean_data = []
	for i in range(len(data)):
		if(not data[i][2]['累计净值'].isnull().any()):
			clean_data.append(data[i])
	return clean_data

# 机智的色子。
def science_random(data):
	# 活不过两百个交易日的基金不要。
	while True:
		the_fund = random.randint(0, len(data) - 1)
		the_day = random.randint(0, len(data[the_fund][2]))
		if len(data[the_fund][2]) > the_day + LIANG_BAI_TIAN:
			return the_fund, the_day

# 指定日期的色子。
def science_random_specify_the_day(data, the_day):
	# 活不过两百个交易日的基金不要。
	while True:
		the_fund = random.randint(0, len(data) - 1)
		if len(data[the_fund][2]) > the_day + LIANG_BAI_TIAN:
			return the_fund

# 止盈。
def stop_profit(data, the_fund, the_day, money, zhi_ying_dian):
	C_the_fund = the_fund
	C_the_day = the_day
	C_fund = Decimal(money) / Decimal(data[C_the_fund][2]['累计净值'].iloc[C_the_day])
	# A琢磨，自己一次交易持有两百天，那C肯定也要一次持有两百天。
	# 不过C有止盈策略。
	# 那就让C达到止盈点后就卖出，卖出后再随机买入一支基金，如此循环往复，直到过完两百天。
	# A认为很公平。
	remain_days = LIANG_BAI_TIAN
	pass_day = 0
	while remain_days > 0:
		pass_day += 1
		remain_days -= 1
		if Decimal(data[C_the_fund][2]['累计净值'].iloc[C_the_day + pass_day]) / \
		   Decimal(data[C_the_fund][2]['累计净值'].iloc[C_the_day]) >= zhi_ying_dian:
			# 达到止盈点后就卖出。
			C_money = Decimal(C_fund) * Decimal(data[C_the_fund][2]['累计净值'].iloc[C_the_day + pass_day])
			pass_day = 0
			# 继续买入下一支随机基金。
			C_the_day += pass_day
			C_the_fund = science_random_specify_the_day(data, C_the_day)
			C_fund = Decimal(C_money) / Decimal(data[C_the_fund][2]['累计净值'].iloc[C_the_day])
	# 过完两百天后卖出。
	C_money = Decimal(C_fund) * Decimal(data[C_the_fund][2]['累计净值'].iloc[C_the_day + pass_day])
	return C_money	

# 正式的比赛。
def real_game(data, money):
	# 仍然使用扔色子确定持有的基金，以及买入的时间节点。
	the_fund, the_day = science_random(data)
	for i in range(len(money)):
		money[i] = money[i] * Decimal(0.93) # 每次交易收取的佣金，在0.9115时可保持A的策略资产不变。
	# A自己策略仍然是持有两百个交易日后卖出。
	end_day = the_day + LIANG_BAI_TIAN
	A_fund = Decimal(money[0]) / Decimal(data[the_fund][2]['累计净值'].iloc[the_day])
	A_money = Decimal(A_fund) * Decimal(data[the_fund][2]['累计净值'].iloc[end_day])
	# 再琢磨琢磨C的策略。
	C1_money = stop_profit(data, the_fund, the_day, money[1], C1_ZHI_YING_DIAN) 
	C2_money = stop_profit(data, the_fund, the_day, money[2], C2_ZHI_YING_DIAN) 
	C3_money = stop_profit(data, the_fund, the_day, money[3], C3_ZHI_YING_DIAN) 
	C4_money = stop_profit(data, the_fund, the_day, money[4], C4_ZHI_YING_DIAN) 
	C5_money = stop_profit(data, the_fund, the_day, money[5], C5_ZHI_YING_DIAN) 
	return [A_money, C1_money, C2_money, C3_money, C4_money, C5_money]

def show_result(result):
	print('result_A:', result[0][-1])
	print('result_C1:', result[1][-1])
	print('result_C2:', result[2][-1])
	print('result_C3:', result[3][-1])
	print('result_C4:', result[4][-1])
	print('result_C5:', result[5][-1])
	plt.yscale('log')
	# 画上阴影。
	x = range(len(result[0]))
	C_max = []
	C_min = []
	for i in range(len(result[0])):
		C_range = []
		for j in range(1, len(result)):
			C_range.append(result[j][i])
		C_max.append(max(C_range))
		C_min.append(min(C_range))
	plt.fill_between(x, C_max, C_min, alpha=0.3, color='blue')
	# 搞颜色。
	viridis = cm.get_cmap('viridis', 256)
	newcolors = viridis(np.linspace(0, 1, 256))
	# 画线。
	plt.plot(result[1], color= newcolors[0], linewidth = 1, label='stop profit 10%')
	plt.plot(result[2], color= newcolors[50], linewidth = 1, label='stop profit 20%')
	plt.plot(result[3], color= newcolors[100], linewidth = 1, label='stop profit 30%')
	plt.plot(result[4], color= newcolors[150], linewidth = 1, label='stop profit 60%')
	plt.plot(result[5], color= newcolors[200], linewidth = 1, label='stop profit 90%')
	plt.plot(result[0], color='red', linewidth = 2, label='not stop profit')
	plt.legend()
	plt.show()


data = get_data()
# 一天，两个聪明的投资者，A和C碰面了。
# A表示，买基金就要长期持有，只管买入，从不卖出。
# A表示，自己有经验，基金这个东西，买到就是赚到，持有一天，就多赚一天。
# C表示不服。
# C表示，自己信仰伟大的止盈神教。
# C表示，那贪得无厌的，皆是异端。
# C表示，从神身上索取的，终将偿还。
# A问，如何才是不贪。
# C表示，知足即是不贪，是滚滚洪流中的抽身而退，是疯狂时的沉默，亦是衰落前的心安。
# A问，止盈？
# C表示，止盈。
# A问，涨多少才应该止盈？
# C表示，不重要。
# A问，止盈后何时再买入？
# C表示，不重要。
# A沉思良久。
# A问，从神身上索取的，终将偿还？
# C看了A一眼。
# 终将偿还，C表示。
# C离开了，A却还在思考。
# A琢磨，那涨了的，终将跌回去。
# A疑惑，对，还是不对？
# 好在A有穿越时空的能力，A决定一试。
# 老样子，两种策略初始资金都为一百万。
money = [YI_BAI_WAN, YI_BAI_WAN, YI_BAI_WAN, YI_BAI_WAN, YI_BAI_WAN, YI_BAI_WAN]
result_A = [money[0]]
result_C1 = [money[1]]
result_C2 = [money[2]]
result_C3 = [money[3]]
result_C4 = [money[4]]
result_C5 = [money[5]]
# 还是重复一万次。
for i in range(YI_WAN_CI):
	money = real_game(data, money)
	result_A.append(money[0])
	result_C1.append(money[1])
	result_C2.append(money[2])
	result_C3.append(money[3])
	result_C4.append(money[4])
	result_C5.append(money[5])
# 看看结果。
result = [result_A, result_C1, result_C2, result_C3, result_C4, result_C5]
show_result(result)
# result_A: 1.669705651476775619279506968E+91
# result_C1: 4.060110497984485055315275236E-41
# result_C2: 5.190512346389447512302115296E+39
# result_C3: 9.596585004050730189454035698E+66
# result_C4: 4.017115659084595754886481370E+95
# result_C5: 1.924093234754594565408168929E+97