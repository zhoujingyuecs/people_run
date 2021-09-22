import akshare as ak
import pickle
import os
import datetime

# 通过akshare获取所有基金的数据。
# 数据格式为：
# [基金代码, 基金简称, [累计净值走势]]
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

THE_FILE_NAME = r"./210922-akshare_fund"

def get_data():
	print('Get the data!')
	file_name = THE_FILE_NAME + r".data"

	fund_em_open_fund_daily_df = ak.fund_em_open_fund_daily()
	print(fund_em_open_fund_daily_df)
	# 总共数据量为11625

	if os.path.exists(file_name):
		file = open(file_name, "rb")
		data = pickle.load(file)
	else:
		data = []

	for i in range(len(data), len(fund_em_open_fund_daily_df)):
		print(i)
		one_data = []
		try:
			fund_em_info_df = ak.fund_em_open_fund_info(fund=fund_em_open_fund_daily_df['基金代码'].iloc[i], indicator="累计净值走势")
		except:
			print('Failed to get the data of', fund_em_open_fund_daily_df['基金代码'].iloc[i])
		one_data.append(fund_em_open_fund_daily_df['基金代码'].iloc[i])
		one_data.append(fund_em_open_fund_daily_df['基金简称'].iloc[i])
		one_data.append(fund_em_info_df)
		data.append(one_data)
		if i % 500 == 0:
			file = open(file_name, "wb")
			pickle.dump(data, file)
			file.close()

	file = open(file_name, "wb")
	pickle.dump(data, file)
	file.close()

def clean_data():
	print('CLean the data!')
	file_name = THE_FILE_NAME + r".data"
	clean_file_name = THE_FILE_NAME + r"-clean.data"

	file = open(file_name,"rb")
	data = pickle.load(file)
	print(len(data))

	# 清除有空值的基金。
	clean_data = []
	for i in range(len(data)):
		if(not data[i][2]['累计净值'].isnull().any()):
			clean_data.append(data[i])
	print(len(clean_data))
	# 清除有丢失记录的基金。
	data = clean_data
	clean_data = []
	for i in range(len(data)):
		flag = 1
		for j in range(len(data[i][2]) - 1):
			# today = datetime.datetime.strptime(data[i][2]['净值日期'].iloc[j], '%Y-%m-%d')
			today = data[i][2]['净值日期'].iloc[j]
			tomorrow = data[i][2]['净值日期'].iloc[j + 1]
			# tomorrow = datetime.datetime.strptime(data[i][2]['净值日期'].iloc[j + 1], '%Y-%m-%d')
			if tomorrow - today > datetime.timedelta(days = 15):
				flag = 0
				break
		if flag == 1:
			clean_data.append(data[i])
	print(len(clean_data))

	file = open(clean_file_name, "wb")
	pickle.dump(clean_data, file)
	file.close()

def dict_by_date():
	# 数据格式为：
	# dict_name: {基金代码: 基金简称, ...}
	# list_date: [2011-09-21, ..., 2021-08-05]
	# list_data: [{基金代码: 当日累计净值, ...}, ...]
	# data_dict: [dict_name, list_date, list_data]
	print('Dict the data!')

	clean_file_name = THE_FILE_NAME + r"-clean.data"
	dict_file_name = THE_FILE_NAME + r"-dict.data"

	file = open(clean_file_name, "rb")
	data = pickle.load(file)
	print(len(data))

	dict_name = {}
	for i in range(len(data)):
		dict_name[data[i][0]] = data[i][1]
	# print(dict_name)

	list_date = []
	for i in range(len(data)):
		for j in range(len(data[i][2])):
			if data[i][2]['净值日期'].iloc[j] not in list_date:
				list_date.append(data[i][2]['净值日期'].iloc[j])
	list_date.sort()
	# print(list_date)

	tmp_dict = {} # {净值日期: 净值日期在 list_date 中的下标, ...}
	for i in range(len(list_date)):
		tmp_dict[list_date[i]] = i
	list_data = []
	for i in range(len(list_date)):
		list_data.append({})
	for i in range(len(data)):
		for j in range(len(data[i][2])):
			list_data[ tmp_dict[data[i][2]['净值日期'].iloc[j]] ][data[i][0]] = data[i][2]['累计净值'].iloc[j]
	# print(list_data)

	data_dict = [dict_name, list_date, list_data]
	file = open(dict_file_name, "wb")
	pickle.dump(data_dict, file)
	file.close()

get_data()
clean_data()
dict_by_date()