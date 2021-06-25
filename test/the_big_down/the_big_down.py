import pickle
import matplotlib.pyplot as plt

# Statistics the trend after market drop/rise.
# 统计指数大幅度下跌/上涨前后一段时间内的股价走势.

file = open(r"./all_index.data","rb")
data = pickle.load(file)
file.close()
szzs = [] # 上证指数

for i in range(len(data)): # For all stock.
	# 上证指数 SHSE.000001
	# 深圳成指 SZSE.399001
	# 创业板指 SZSE.399006
	if len(data[i]) > 1 and data[i][0]['symbol'] == 'SHSE.000001':
		szzs = data[i]
# print(szzs)
TREND_LENGTH = 200
DROP_RANGE = 0.98
RISE_RANGE = 1.02
drop_data_num = 0
drop_line = []
rise_data_num = 0
rise_line = []
for i in range(TREND_LENGTH * 2 + 1):
	drop_line.append(0)
	rise_line.append(0)
for i in range(TREND_LENGTH, len(szzs) - TREND_LENGTH): # For every day.
	if szzs[i]['close'] / szzs[i - 1]['close'] < DROP_RANGE:
		drop_data_num += 1
		for j in range(TREND_LENGTH * 2 + 1):
			drop_line[j] += (szzs[i - TREND_LENGTH + j]['close'] - szzs[i]['close']) / szzs[i]['close']
	if szzs[i]['close'] / szzs[i - 1]['close'] > RISE_RANGE:
		rise_data_num += 1
		for j in range(TREND_LENGTH * 2 + 1):
			rise_line[j] += (szzs[i - TREND_LENGTH + j]['close'] - szzs[i]['close']) / szzs[i]['close']
for i in range(TREND_LENGTH * 2 + 1):
	drop_line[i] /= drop_data_num
	rise_line[i] /= rise_data_num

print('drop_data_num:', drop_data_num)
print('rise_data_num:', rise_data_num)
title = 'drop_data_num: ' + str(drop_data_num) + ' / rise_data_num: ' + str(rise_data_num)
plt.title(title)
plt.plot(range(-TREND_LENGTH, TREND_LENGTH + 1), drop_line, color='green')
plt.plot(range(-TREND_LENGTH, TREND_LENGTH + 1), rise_line, color='red')
plt.plot(range(-1, 1), drop_line[TREND_LENGTH - 1:TREND_LENGTH + 1], color='blue', linewidth = 2, linestyle = 'dashed')
plt.plot(range(-1, 1), rise_line[TREND_LENGTH - 1:TREND_LENGTH + 1], color='blue', linewidth = 2, linestyle = 'dashed')
plt.plot([-TREND_LENGTH, TREND_LENGTH], [0, 0], color='black', linewidth = 0.5)
plt.show()
