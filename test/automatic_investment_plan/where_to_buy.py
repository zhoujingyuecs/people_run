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
YI_WAN_CI = 5000
D_SHI_JIAN = [100, 200, 300, 400]
D_ZHAN_JI = [0.1, 0.2, 0.3, 0.4]

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
	file = open(r"./akshare_fund-11420-clean-10804.data","rb")
	data = pickle.load(file)
	return data

# 机智的色子。
def science_random(data):
	# 活不过两百个交易日的基金不要。
	while True:
		the_fund = random.randint(0, len(data) - 1)
		the_day = random.randint(0, len(data[the_fund][2]))
		if len(data[the_fund][2]) > the_day + LIANG_BAI_TIAN:
			return the_fund, the_day

# 挑剔的色子。
def selective_random(data, time, profit):
	while True:
		the_fund = random.randint(0, len(data) - 1)
		the_day = random.randint(0, len(data[the_fund][2]))
		# 活不过两百个交易日的基金不要。
		if len(data[the_fund][2]) - 1 < the_day + LIANG_BAI_TIAN:
			continue
		# 历史数据不够的不要。
		if the_day < time:
			continue
		# 不符合要求的不要。
		real_profit = profit / 200 * time # 计算历史持续时间中要达到的收益。
		if profit > 0 and Decimal(data[the_fund][2]['累计净值'].iloc[the_day]) / \
		                  Decimal(data[the_fund][2]['累计净值'].iloc[the_day - time]) < 1 + real_profit:
			continue
		if profit < 0 and Decimal(data[the_fund][2]['累计净值'].iloc[the_day]) / \
		                  Decimal(data[the_fund][2]['累计净值'].iloc[the_day - time]) > 1 - real_profit:
			continue
		return the_fund, the_day


# 正式的比赛。
def real_game(data, money):
	for i in range(len(money)):
		money[i] = money[i] * Decimal(0.92) # 每次交易收取的佣金，在0.9115时可保持A的策略资产不变。
	result = []
	# 仍然使用扔色子确定A持有的基金，以及买入的时间节点。
	the_fund, the_day = science_random(data)
	# A自己策略仍然是持有两百个交易日后卖出。
	end_day = the_day + LIANG_BAI_TIAN
	A_fund = Decimal(money[0]) / Decimal(data[the_fund][2]['累计净值'].iloc[the_day])
	A_money = Decimal(A_fund) * Decimal(data[the_fund][2]['累计净值'].iloc[end_day])
	result.append(A_money)
	# D则扔一颗更为挑剔的色子。
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			the_fund, the_day = selective_random(data, D_SHI_JIAN[i], D_ZHAN_JI[j])
			end_day = the_day + LIANG_BAI_TIAN
			D_fund = Decimal(money[i * len(D_ZHAN_JI) + j + 1]) / Decimal(data[the_fund][2]['累计净值'].iloc[the_day])
			D_money = Decimal(D_fund) * Decimal(data[the_fund][2]['累计净值'].iloc[end_day])
			result.append(D_money)
	return result

def fill(lines, color):
	# 画上阴影。
	x = range(len(lines[0]))
	Y_max = []
	Y_min = []
	for i in range(len(lines[0])):
		Y_range = []
		for j in range(len(lines)):
			Y_range.append(lines[j][i])
		Y_max.append(max(Y_range))
		Y_min.append(min(Y_range))
	plt.fill_between(x, Y_max, Y_min, alpha = 0.3, color = color)

def show_result(result):
	print('result_A:', result[0][-1])
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			print('result_C', D_SHI_JIAN[i], D_ZHAN_JI[j], ':', result[i * len(D_ZHAN_JI) + j + 1][-1])
	plt.yscale('log')
	# 画上阴影。
	# for i in range(len(D_SHI_JIAN)):
	# 	lines = []
	# 	for j in range(len(D_ZHAN_JI)):
	# 		lines.append(result[i * len(D_ZHAN_JI) + j + 1])
	# 	color = [1 / len(D_SHI_JIAN) * (i + 1), 0.2, 0.2, 1]
	# 	fill(lines, color)
	# 画线。
	style = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H']
	for i in range(len(D_SHI_JIAN)):
		for j in range(len(D_ZHAN_JI)):
			label_str = str(D_SHI_JIAN[i]) + ' days annualized '
			if D_ZHAN_JI[j] > 0:
				label_str += '>'
			else:
				label_str += '<'
			label_str += ' ' + str(D_ZHAN_JI[j])
			color = [1 / len(D_SHI_JIAN) * (i + 1), 1 / len(D_ZHAN_JI) * (j + 1), 0.2, 1]
			the_style = style[(i * len(D_ZHAN_JI) + j) % len(style)]
			plt.plot(result[i * len(D_ZHAN_JI) + j + 1], color = color, linewidth = 2, label = label_str, \
			  marker = the_style, markevery = 0.05, markersize = 10)
	plt.plot(result[0], color='red', linewidth = 4, label='random')
	plt.legend()
	plt.show()

data = get_data()
# 一天，两个聪明的投资者，A和D碰面了。
# A表示，自己买基金靠扔色子，扔到啥是啥。
# D表示，A太草率了，买基金需要多重考虑。
# A问，比如？
# D表示，要看该基金以往业绩，基金经理任期长度以及个人战绩。
# 看看该基金公司的资料，该基金所处行业，乃至于宏观的大环境。
# 要看的东西多了去了，怎么能随便扔色子呢。
# A表示，这些东西太复杂了，有没有简单点的评价方法。
# D问，比如？
# A表示，比如，该基金前段时间跌没跌，涨没涨。
# D问，那是跌了好还是涨了好？
# A表示，我不知道啊，这不在问你嘛。
# D表示，我也不知道。
# A表示，我感觉是跌了好，价格围绕价值波动，跌了要涨回去。
# D表示，那感觉还是涨了好，跌了说明基金经理上班摸鱼，不好好干活，这只基金只会越来越差。
# D表示，小幅度/短期的跌是价格围绕价值波动，可以买入，大幅度/长期的跌说明这支基金出了问题，需要卖出。
# D总结，那应该买小幅度下跌，或者大幅度上涨的基金。
# D又表示，那不行啊。
# D表示，低买高卖是一定的，大幅度上涨了，正是在高位上，怎么能买入？
# A表示，是因为又有利好才会大幅度上涨，这只是价值回归，无论在回归途中哪个点买入，都是好的。
# D表示，刚开始可能是价值回归，后面涌入的资金会把价格抬高到超过资产价值的位置，这时入场就不明智了。
# A表示，那大幅度上涨的基金也不能买？
# A表示，那你的意思是应该买大幅度下跌的基金。
# D表示，也不一定。
# D表示，基金和股票不同，股票的价格高了就是高了，贵了就要降下来，便宜了就要升回去。
# D表示，但基金不同，基金有基金经理夹在中间，他可以卖出贵的股票买便宜的股票。
# D表示，在泡沫破灭前基金经理就可以提前离场，不一定需要承担崩盘的后果。
# D表示，不过这只代表他可能可以跑掉，实际跑的跑不掉还不知道。
# D表示，有可能他就觉得还会涨，不想跑。也有可能他想跑，但盘子太大，没下家接，他一时跑不掉。
# A问，那等于长期涨了不一定能不能买。
# D表示，是的。
# A问，那长期跌呢。
# D表示，长期跌可能是市场环境不好导致。也可能是基金经理水平不行。
# D表示，市场环境太差了终归会好起来的，但你也没法判断现在是在坏下去还是好起来的路上。
# A表示，长期那么复杂啊。
# A表示，那还是短期简单，短期高抛低吸，跌了买，涨了卖，一定赚。
# D表示，没那么简单的，短期波动是叠加在长期波动上的。
# D表示，低吸后可能会一直跌下去，直到长期循环完一个周期都涨不回来。
# D表示，要是碰上基金本身出了问题，那可能永远涨不回来。
# A表示，我琢磨琢磨。
# 一阵思考后A整理了一下。
# 
# 长期上涨利好：基金经理脑子好。市场大环境好。
# 长期上涨利空：资产价格虚高，泡沫要破裂。
# 长期下跌利好：资产价格低，能反弹。
# 长期下跌利空：基金经理脑子不好。市场大环境不好。
# 短期波动：短期波动（价格到达某人的止盈止损位置；某人发工资；某人找到了女朋友，于是想买房。及其它原因）和长期波动的叠加。
# 
# D表示赞同。
# A问，那到底啥时候买入？
# 谁知道呢，D表示。
# A决定自己试试。
# 老样子，两种策略初始资金都为一百万。
# 共给D设置 时间跨度选项 * 期望的年化收益率选项 种策略。
money = []
result = []
for i in range(len(D_SHI_JIAN) * len(D_ZHAN_JI) + 1):
	money.append(YI_BAI_WAN)
	result.append([YI_BAI_WAN])
# 还是重复一万次。
for i in range(YI_WAN_CI):
	money = real_game(data, money)
	for j in range(len(money)):
		result[j].append(money[j])
# 看看结果。
show_result(result)
# result_A: 3.820702554994020477786287438E+36
# result_C 100 0.1 : 2.988037053929355475962019672E+147
# result_C 100 0.2 : 5.255215312553378016268217997E+201
# result_C 100 0.3 : 1.861057873479607849354808722E+184
# result_C 100 0.4 : 4.884255312089069899688829735E+188
# result_C 200 0.1 : 2.840570217244573968905649097E+168
# result_C 200 0.2 : 4.569044381427349241280700819E+228
# result_C 200 0.3 : 3.236250831390555327447295207E+240
# result_C 200 0.4 : 1.129070372125394691796819558E+191
# result_C 300 0.1 : 5.072877384670775663898182390E+171
# result_C 300 0.2 : 1.981790521736792352924086319E+215
# result_C 300 0.3 : 2.195851017209648720566725653E+204
# result_C 300 0.4 : 5.586040611902809804561776876E+150
# result_C 400 0.1 : 8.904462913544313856350164855E+104
# result_C 400 0.2 : 2.932607445709897720190461484E+103
# result_C 400 0.3 : 3.891831154444907150399087629E+87
# result_C 400 0.4 : 8.769667898686324362150271935E+54
