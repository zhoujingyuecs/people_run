import akshare as ak
import pickle
# import time

cookie = 'xxxxx'  # 此处请用单引号
words = ['贷款', '房贷', '利率']
FILE_NAME = r"./words_index.data"


indexs = []
for i in range(len(words)):
	baidu_search_index_df = ak.baidu_search_index(word=words[i],
	    start_date='2010-12-27', end_date='2021-08-17', cookie=cookie)
	print(i)
	# print(baidu_search_index_df)
	# time.sleep(10)
	indexs.append(baidu_search_index_df)

data = [words, indexs]
file = open(FILE_NAME, "wb")
pickle.dump(data, file)
file.close()