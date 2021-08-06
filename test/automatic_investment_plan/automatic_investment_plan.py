import pickle
import matplotlib.pyplot as plt
import akshare as ak
import random
import numpy as np
from decimal import Decimal

# Automatic investment plan.
# 使用蒙特卡罗方法计算定投的期望。

YI_BAI_WAN = Decimal(1000000)
LIANG_BAI_TIAN = 200
SHI_CI = 10
SHI_GE_JIAO_YI_RI = 10
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
	file = open(r"./akshare_fund-1000.data","rb")
	data = pickle.load(file)
	clean_data = []
	for i in range(len(data)):
		if(not data[i][2]['累计净值'].isnull().any()):
			clean_data.append(data[i])
	return clean_data

# 机智的色子。
def science_random(data):
	# 活不过两百个交易日的基金不要(顺带在B开始定投前还没成立的基金也不要)。
	while True:
		the_fund = random.randint(0, len(data) - 1)
		if SHI_CI * SHI_GE_JIAO_YI_RI > len(data[the_fund][2]):
			continue
		the_day = random.randint(SHI_CI * SHI_GE_JIAO_YI_RI, len(data[the_fund][2]))
		if len(data[the_fund][2]) > the_day + LIANG_BAI_TIAN:
			return the_fund, the_day

# 定投。
def automatic_investment_plan(data, the_fund, the_day, money):
	every_money = money / SHI_CI
	B_fund = 0
	B_money = money
	for i in range(SHI_CI):
		B_money -= Decimal(every_money)
		B_fund += Decimal(every_money) / Decimal(data[the_fund][2]['累计净值'].iloc[the_day + i * SHI_GE_JIAO_YI_RI])
	B_money += Decimal(B_fund) * Decimal(data[the_fund][2]['累计净值'].iloc[the_day + LIANG_BAI_TIAN])
	return B_money

# 比赛。
def game(data):
	# A表示自己有穿越时空的能力，能带上一百万到过去的任意一个时间点，买任意一支基金。
	A_money = YI_BAI_WAN
	# B表示，A都回到过去了，那还不是看什么涨买什么，看来自己这个傻逼是当定了。
	# A表示，B别慌，自己扔色子，扔到哪支基金就买哪支基金。
	the_fund = random.randint(0, len(data) - 1)
	# 扔到哪天就回哪天。
	the_day = random.randint(0, len(data[the_fund][2]))
	# 自己直接梭哈。
	A_fund = A_money / Decimal(data[the_fund][2]['累计净值'].iloc[the_day])
	A_money = 0
	# 放两百个交易日后卖出。
	# B表示，呵呵
	# 还不到两百个交易日该基金就已倒闭，A倾家荡产。
	# A表示，...
	# A表示，那我掷色子的时候选能活满两百个交易日的基金买，放两百个交易日后卖出。
	the_fund, the_day = science_random(data)
	A_money = YI_BAI_WAN
	A_fund = A_money / Decimal(data[the_fund][2]['累计净值'].iloc[the_day])
	A_money = A_fund * Decimal(data[the_fund][2]['累计净值'].iloc[the_day + LIANG_BAI_TIAN])
	# A问，B，你怎么讲。
	# B表示，我和你买一样的基金，也拿两百天。
	# A表示，行啊，很公平。
	# B表示，不过我要定投，每次把资金分散为十次买入，每次隔十个交易日。
	B_money = YI_BAI_WAN
	B_money = automatic_investment_plan(data, the_fund, the_day, B_money) 
	# B表示，你都梭哈了，我才开始定投，等于你持仓的日子比我长，这不公平。
	# A表示，那你想怎么办。
	# B表示，我要搞三个策略：
	# 第一个策略在A梭哈前就定投完毕。
	# 第二个策略在A梭哈时正好定投了一半。
	# 第三个策略在A梭哈后才开始定投。
	# A表示，行啊，随便你搞。
	B1_money = automatic_investment_plan(data, the_fund, the_day - SHI_CI * SHI_GE_JIAO_YI_RI, B_money) 
	B2_money = automatic_investment_plan(data, the_fund, the_day - int(SHI_CI * SHI_GE_JIAO_YI_RI / 2), B_money) 
	B3_money = automatic_investment_plan(data, the_fund, the_day, B_money) 
	return [A_money, B1_money, B2_money, B3_money]

# 正式的比赛。
def real_game(data, money):
	the_fund, the_day = science_random(data)
	for i in range(len(money)):
		money[i] = money[i] * Decimal(0.95) # 每次交易收取五个点的佣金
	A_fund = Decimal(money[0]) / Decimal(data[the_fund][2]['累计净值'].iloc[the_day]) / Decimal(10) # 先除十再乘十避免精度误差。
	A_money = Decimal(A_fund) * Decimal(data[the_fund][2]['累计净值'].iloc[the_day + LIANG_BAI_TIAN]) * Decimal(10)
	B1_money = automatic_investment_plan(data, the_fund, the_day - SHI_CI * SHI_GE_JIAO_YI_RI, money[1]) 
	B2_money = automatic_investment_plan(data, the_fund, the_day - int(SHI_CI * SHI_GE_JIAO_YI_RI / 2), money[2]) 
	B3_money = automatic_investment_plan(data, the_fund, the_day, money[3]) 
	return [A_money, B1_money, B2_money, B3_money]

def show_result(result):
	print('result_A:', result[0][-1])
	print('result_B1:', result[1][-1])
	print('result_B2:', result[2][-1])
	print('result_B3:', result[3][-1])
	plt.yscale('log')
	plt.plot(result[0], color='red', linewidth = 1)
	plt.plot(result[1], color='blue', linewidth = 1, linestyle = '--')
	plt.plot(result[2], color='blue', linewidth = 1)
	plt.plot(result[3], color='blue', linewidth = 1, linestyle = ':')
	plt.show()

data = get_data()
# 一天，两个聪明的投资者，A和B碰面了。
# A表示，投资就要一把梭哈，谁定投谁是傻逼。
# B表示，定投更为稳妥，梭哈的才是傻逼。
# 于是A和B打了一架。
# 打完后A和B还是不知道谁是傻逼。
# 于是A和B打算进行一场比赛，输的人就是傻逼。
result = game(data)
# A问，咱们比几次。
# B表示，都行啊，一万次呗。
# A表示，行的。
money = [YI_BAI_WAN, YI_BAI_WAN, YI_BAI_WAN, YI_BAI_WAN]
result_A = [money[0]]
result_B1 = [money[1]]
result_B2 = [money[2]]
result_B3 = [money[3]]
for i in range(YI_WAN_CI):
	money = real_game(data, money)
	result_A.append(money[0])
	result_B1.append(money[1])
	result_B2.append(money[2])
	result_B3.append(money[3])
result = [result_A, result_B1, result_B2, result_B3]
# 比完了，让我们看看谁才是傻逼。
show_result(result)
# result_A: 5.577709324451721472753628027E+184
# result_B1: 6.973293256880032081976803930E+104
# result_B2: 8.240322023058569382907544563E+101
# result_B3: 2.800527497726490029222361886E+95



