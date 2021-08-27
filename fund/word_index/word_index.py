import pickle
import matplotlib.pyplot as plt

DATA_FILE = r"./words_index.data"

# 获取所有百度搜索指数。
def get_data():
	# 数据格式为：
	# data: [words, indexs]
	file = open(DATA_FILE, "rb")
	data = pickle.load(file)
	return data

def show_result(name, result, date):
	# 画线。
	plt.figure()
	plt.yscale('log')
	style = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'X']
	for i in range(len(result)):
		label_str = str(name[i])
		color = [1 / len(result) * (i + 1), 1 / len(result) * (i + 1), 0.2, 1]
		the_style = style[i % len(style)]
		plt.plot(result[i], color = color, linewidth = 2, label = label_str, \
		  marker = the_style, markevery = 0.05, markersize = 10)
	# plt.plot(result[0], color='red', linewidth = 5, label='random')
	# x_index = []
	# x_value = []
	# space = int(len(date) / 10)
	# for i in range(len(date)):
	# 	if i % space == 0:
	# 		x_index.append(i)
	# 		x_value.append(date[i])
	# plt.xticks(x_index, x_value)
	plt.legend()
	plt.show()

data = get_data()
result = []
# date = data[1][0].key().tolist()
date = []
for i in range(len(data[1])):
	result.append(data[1][i].iloc[:, 0].tolist())
# print(result)
print(date)
show_result(data[0], result, date)
# print(type(data[1][1]['date']))
