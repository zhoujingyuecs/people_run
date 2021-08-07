import akshare as ak
import pickle
import os

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

FILE_NAME = r"./akshare_fund-11615.data"

fund_em_open_fund_daily_df = ak.fund_em_open_fund_daily()
print(fund_em_open_fund_daily_df)
# 总共数据量为11625

if os.path.exists(FILE_NAME):
	file = open(FILE_NAME, "rb")
	data = pickle.load(file)
else:
	data = []

for i in range(len(data), len(fund_em_open_fund_daily_df)):
	print(i)
	one_data = []
	fund_em_info_df = ak.fund_em_open_fund_info(fund=fund_em_open_fund_daily_df['基金代码'].iloc[i], indicator="累计净值走势")
	one_data.append(fund_em_open_fund_daily_df['基金代码'].iloc[i])
	one_data.append(fund_em_open_fund_daily_df['基金简称'].iloc[i])
	one_data.append(fund_em_info_df)
	data.append(one_data)
	if i % 100 == 0:
		file = open(FILE_NAME, "wb")
		pickle.dump(data, file)
		file.close()

file = open(FILE_NAME, "wb")
pickle.dump(data, file)
file.close()
