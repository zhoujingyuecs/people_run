import pickle
import matplotlib.pyplot as plt

# The Support.
# 统计之前若干交易日的收盘价，找出最低点和最高点，作为支撑位。
# 统计当股价变动遇到支撑位时，被拦下的概率和突破的概率哪个大。

# 获取上证指数数据
def get_data():
	file = open(r"../all_index.data","rb")
	data = pickle.load(file)
	file.close()
	szzs = [] # 上证指数
	for i in range(len(data)): # For all stock.
		# 上证指数 SHSE.000001
		# 深圳成指 SZSE.399001
		# 创业板指 SZSE.399006
		if len(data[i]) > 1 and data[i][0]['symbol'] == 'SHSE.000001':
			szzs = data[i]
	# szzs 数据长度为1946
	return szzs

# 获取上升支撑位，下降支撑位
def get_support(szzs, the_day):
	up = -100000000
	down = 100000000
	for i in range(the_day - DATA_LENGTH, the_day - DATA_MIN):
		if szzs[i]['close'] > up:
			up = szzs[i]['close']
		if szzs[i]['close'] < down:
			down = szzs[i]['close']
	return up, down

# 展示结果
def show_result(szzs, the_day, up_up, up_down, down_up, down_down, up_num, down_num, up_break, down_break):
	plt.cla()
	# 绘制数据线
	x_axis = range(the_day - DATA_LENGTH - 100, the_day + 100)
	show_szzs = []
	for i in x_axis:
		show_szzs.append(szzs[i]['close'])
	title = str(szzs[the_day]['eob'])[:10]
	plt.plot(x_axis, show_szzs, color='blue', linewidth = 2)
	title += '\n'
	tmp = 1
	if up_num > 0:
		tmp = up_num
	title += 'up_num: ' + str(up_num) + ', up_break: ' + str(up_break) + ', break_probability: ' + str(up_break / tmp)[:4] + '\n'
	tmp = 1
	if down_num > 0:
		tmp = down_num
	title += 'down_num: ' + str(down_num) + ', down_break: ' + str(down_break) + ', break_probability: ' + str(down_break / tmp)[:4]
	# 绘制上下支撑位
	plt.plot([x_axis[0], x_axis[-1]], [up_up, up_up], color='red', linewidth = 1)
	plt.plot([x_axis[0], x_axis[-1]], [up_down, up_down], color='red', linewidth = 1)
	plt.plot([x_axis[0], x_axis[-1]], [down_up, down_up], color='green', linewidth = 1)
	plt.plot([x_axis[0], x_axis[-1]], [down_down, down_down], color='green', linewidth = 1)
	# 绘制辅助信息
	plt.title(title)
	plt.plot([the_day, the_day], [max(show_szzs), min(show_szzs)], color='black', linewidth = 1)
	plt.plot([the_day - DATA_LENGTH, the_day - DATA_LENGTH], [max(show_szzs), min(show_szzs)], color='black', linewidth = 1)
	plt.plot([the_day - DATA_MIN, the_day - DATA_MIN], [max(show_szzs), min(show_szzs)], color='black', linewidth = 1, linestyle = '--')
	# 自动播放
	plt.show(block = False)
	plt.pause(0.001)
	# plt.pause(500)


szzs = get_data()
DATA_LENGTH = 100 # 支撑位所在的最远时间跨度
DATA_MIN = 20 # 支撑位所在的最近时间跨度
SUPPORT_RANGE = 0.01 # 支撑位在支撑点附近的范围
up_num = 0 # 进入上升支撑位次数
down_num = 0 # 进入下降支撑位次数
up_break = 0 # 进入上升支撑位并且突破的次数
down_break = 0 # 进入下降支撑位并且突破的次数
for the_day in range(DATA_LENGTH + 300, 1600):
	# 获取上升支撑位上沿/下沿，下降支撑位上沿/下沿
	up, down = get_support(szzs, the_day)
	up_up = up * (1 + SUPPORT_RANGE)
	up_down = up * (1 - SUPPORT_RANGE)
	down_up = down * (1 + SUPPORT_RANGE)
	down_down = down * (1 - SUPPORT_RANGE)
	# 统计是否进入支撑位，以及是否突破
	if szzs[the_day - 1]['close'] > up_down and szzs[the_day - 1]['close'] < up_up: # 昨日在上升支撑位中
		if szzs[the_day]['close'] > up_up: # 今日向上突破
			up_num += 1
			up_break += 1
		if szzs[the_day]['close'] < up_down: # 今日被打回
			up_num += 1
	if szzs[the_day - 1]['close'] > down_down and szzs[the_day - 1]['close'] < down_up: # 昨日在下降支撑位中
		if szzs[the_day]['close'] > down_up: # 今日被打回
			down_num += 1
		if szzs[the_day]['close'] < down_down: # 今日向下突破
			down_num += 1
			down_break += 1
	show_result(szzs, the_day, up_up, up_down, down_up, down_down, up_num, down_num, up_break, down_break)

print('up_num:', up_num)
print('down_num:', down_num)
print('up_break:', up_break)
print('down_break:', down_break)
print('The probability of up_break is:', str(up_break / up_num)[:5])
print('The probability of down_break is:', str(down_break / down_num)[:5])
