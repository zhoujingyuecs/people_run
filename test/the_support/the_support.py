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

# =========================
# 以下是一次运行的结果
# DATA_LENGTH = 200 # 支撑位所在的最远时间跨度
# DATA_MIN = 40 # 支撑位所在的最近时间跨度
# SUPPORT_RANGE = 0.01 # 支撑位在支撑点附近的范围
# -----------------
# all_num: 300
# right_num: 145
# up_num: 147
# The probability of correct is: 0.48333333333333334
# The probability of up is: 0.49
# The probability of up and right is: 0.47802197802197804
# =========================

	# result_image = get_image_trend(szzs, the_day)
	# show_result(szzs, the_day, result_image)
	# # 统计正确率
	# all_num += 1
	# if result_image[IMAGE_RANGE - 1 + IMAGE_RANGE] > result_image[IMAGE_RANGE - 1 + IMAGE_LENGTH]:
	# 	say_up_num += 1
	# if szzs[the_day + IMAGE_RANGE]['close'] > szzs[the_day + IMAGE_LENGTH]['close']:
	# 	up_num += 1
	# if szzs[the_day + IMAGE_RANGE]['close'] > szzs[the_day + IMAGE_LENGTH]['close'] and \
	#    result_image[IMAGE_RANGE - 1 + IMAGE_RANGE] > result_image[IMAGE_RANGE - 1 + IMAGE_LENGTH]:
	# 	right_num += 1
	# 	up_right_num += 1
	# if szzs[the_day + IMAGE_RANGE]['close'] < szzs[the_day + IMAGE_LENGTH]['close'] and \
	#    result_image[IMAGE_RANGE - 1 + IMAGE_RANGE] < result_image[IMAGE_RANGE - 1 + IMAGE_LENGTH]:
	# 	right_num += 1

# # 统计相似趋势的走势
# def get_image_trend(szzs, the_day):
# 	result_image = [0] * (IMAGE_RANGE * 2)  # 统计得到的趋势
# 	# 统计趋势差距
# 	image_diff = [] # 趋势与被统计趋势的差距
# 	for i in range(DAY_START, the_day - IMAGE_RANGE): # 不能得到被统计日之后的任何数据
# 		# 计算趋势差距
# 		one_image_diff = 0 # 当日趋势与被统计趋势的差距
# 		for j in range(IMAGE_LENGTH):
# 			# 也可以引入成交量
# 			tmp_diff = (szzs[i + j + 1]['close'] / szzs[i]['close']) - (szzs[the_day + j + 1]['close'] / szzs[the_day]['close'])
# 			one_image_diff += tmp_diff * tmp_diff
# 		image_diff.append(one_image_diff)
# 	# 只使用最接近的 USED_COUNT 条数据，计算出该条数据的 diff 值
# 	tmp = image_diff[:]
# 	tmp.sort()
# 	used_threshold = tmp[USED_COUNT]
# 	# 根据差距计入统计趋势
# 	for i in range(DAY_START, the_day - IMAGE_RANGE): # 不能得到被统计日之后的任何数据
# 		for j in range(-IMAGE_RANGE, IMAGE_RANGE):
# 			if image_diff[i - DAY_START] < used_threshold:
# 				result_image[j + IMAGE_RANGE] += (szzs[i + j + 1]['close'] / szzs[i]['close'])
# 	# 归一化
# 	for i in range(IMAGE_RANGE * 2):
# 		result_image[i] /= USED_COUNT
# 	return result_image

# # 展示结果
# def show_result(szzs, the_day, result_image):
# 	plt.cla()
# 	# 绘制数据线
# 	x_axis = range(the_day - IMAGE_RANGE - 10, the_day + IMAGE_RANGE + 10)
# 	show_szzs = []
# 	for i in range(the_day - IMAGE_RANGE - 10, the_day + IMAGE_RANGE + 10):
# 		show_szzs.append(szzs[i]['close'])
# 	title = str(szzs[the_day]['eob'])[:10]
# 	plt.plot(x_axis, show_szzs, color='blue', linewidth = 2)
# 	# 绘制结果线
# 	result_x_axis = range(the_day - IMAGE_RANGE + 1, the_day + IMAGE_RANGE + 1)
# 	show_y = [szzs[the_day]['close']] * (IMAGE_RANGE * 2)
# 	for i in range(2 * IMAGE_RANGE):
# 		show_y[i] *= result_image[i]
# 	plt.plot(result_x_axis, show_y, color='red', linewidth = 2)
# 	# 绘制辅助信息
# 	plt.title(title)
# 	plt.plot([the_day, the_day], [max(show_szzs + show_y), min(show_szzs + show_y)], color='black', linewidth = 1)
# 	plt.plot([the_day + IMAGE_LENGTH, the_day + IMAGE_LENGTH], [max(show_szzs + show_y), min(show_szzs + show_y)], color='black', linewidth = 1)
# 	# 自动播放
# 	plt.show(block = False)
# 	plt.pause(0.001)
# 	# plt.pause(500)


# IMAGE_LENGTH = 5 # 趋势包含的交易日数量
# IMAGE_RANGE = 8 # 纳入统计的受趋势影响的交易日范围
# DAY_START = 100 # 统计使用的数据开始
# USED_COUNT = 20 # 使用的数据数量
# all_num = 0
# right_num = 0
# up_num = 0
# say_up_num = 0
# up_right_num = 0
# szzs = get_data()
# for the_day in range(1300, 1600):
# 	result_image = get_image_trend(szzs, the_day)
# 	show_result(szzs, the_day, result_image)
# 	# 统计正确率
# 	all_num += 1
# 	if result_image[IMAGE_RANGE - 1 + IMAGE_RANGE] > result_image[IMAGE_RANGE - 1 + IMAGE_LENGTH]:
# 		say_up_num += 1
# 	if szzs[the_day + IMAGE_RANGE]['close'] > szzs[the_day + IMAGE_LENGTH]['close']:
# 		up_num += 1
# 	if szzs[the_day + IMAGE_RANGE]['close'] > szzs[the_day + IMAGE_LENGTH]['close'] and \
# 	   result_image[IMAGE_RANGE - 1 + IMAGE_RANGE] > result_image[IMAGE_RANGE - 1 + IMAGE_LENGTH]:
# 		right_num += 1
# 		up_right_num += 1
# 	if szzs[the_day + IMAGE_RANGE]['close'] < szzs[the_day + IMAGE_LENGTH]['close'] and \
# 	   result_image[IMAGE_RANGE - 1 + IMAGE_RANGE] < result_image[IMAGE_RANGE - 1 + IMAGE_LENGTH]:
# 		right_num += 1
# print('all_num:', all_num)
# print('right_num:', right_num)
# print('up_num:', up_num)
# print('The probability of correct is:', right_num / all_num)
# print('The probability of up is:', up_num / all_num)
# print('The probability of up and right is:', up_right_num / say_up_num)

# =========================
# 以下是一次运行的结果
# IMAGE_LENGTH = 5 # 趋势包含的交易日数量
# IMAGE_RANGE = 8 # 纳入统计的受趋势影响的交易日范围
# DAY_START = 100 # 统计使用的数据开始
# USED_COUNT = 20 # 使用的数据数量
# -----------------
# all_num: 300
# right_num: 145
# up_num: 147
# The probability of correct is: 0.48333333333333334
# The probability of up is: 0.49
# The probability of up and right is: 0.47802197802197804
# =========================
