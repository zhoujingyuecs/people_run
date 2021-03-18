import pickle
import copy
import random

POOL_SIZE = 20        # How many strategy in the pool.
PEOPLE_NUM = 40       # How many people in this stock world.
TRAIN_TIME = 10000    # How many time the training repeat.
TRAIN_DATA = 4000     # How many data the training use.
ALL_DATA = 5000       # The data including training and testing.

# Init the people
# The type of will
I_WANT_BUY = 1
I_WANT_SELL = 0
# The structure of people
WILL = 0
MONEY = 1
STOCK = 2
INIT_PRICE = 3
IN_MOVE = 4
OUT_MOVE = 5

def init_pool():
	init_people = [] # [will, money, stock, init_price, in_move, out_move], will: 1 mean buy, 0 means sell.
	# Need a small number of money and stock to avoid zero deal trap.
	for i in range(0, int(PEOPLE_NUM / 2)):
		init_people.append([0, 0.02, 0.02, 0.2, 1.0, 1.0]) # [0.0, 0.5, 0.2, 1.2, 0.8]
	for i in range(int(PEOPLE_NUM / 2), PEOPLE_NUM):
		init_people.append([1, 0.02, 0.02, 0.2, 1.0, 1.0]) # [0.0, 0.5, 0.2, 1.2, 0.8]
	# Init the pool
	# The people in the pool means the init state of people and the strategy of people.
	pool = []
	for i in range(POOL_SIZE):
		pool.append([copy.deepcopy(init_people), -1]) # [people, score]
	return pool

def save_pool(pool):
	file = open(r"./pool.data","wb")
	pickle.dump(pool, file)
	file.close()

def load_pool():
	file = open(r"./pool.data","rb")
	pool = pickle.load(file)
	file.close()
	return pool

def magic_load_pool():
	file = open(r"./pool.data","rb")
	old_pool = pickle.load(file)
	file.close()
	pool = []
	for i in range(POOL_SIZE):
		people = []
		lucky_strategy = random.randint(0, len(old_pool) - 1)
		for j in range(PEOPLE_NUM):
			lucky_person = random.randint(0, len(old_pool[lucky_strategy][0]) - 1)
			people.append(old_pool[lucky_strategy][0][lucky_person])
		pool.append([copy.deepcopy(people), -1])
	return pool

def load_data():
	file = open(r"./SHSE000001.data","rb")
	shse = pickle.load(file)
	file.close()
	print('Data len:', len(shse))
	# print(shse) # close,volume,eob
	# Read the data.
	price = []
	volume = []
	max_price = 0
	max_volume = 0
	for i in range(len(shse)):
		price.append(shse[i]['close'])
		volume.append(shse[i]['volume'])
		if shse[i]['volume'] > max_volume:
			max_volume = shse[i]['volume']
		if shse[i]['close'] > max_price:
			max_price = shse[i]['close']
	print('max_volume:', max_volume)
	print('max_price:', max_price)
	std_price = []
	std_volume = []
	for i in range(len(shse)):
		std_price.append(price[i] / max_price)
		std_volume.append(volume[i] / max_volume)
	print('Start at price:', std_price[0])
	print('Start at volume:', std_volume[0])
	return std_price, std_volume

# Calculate the will for each people to buy and sell on the day.
def get_the_will(people, date, std_price):
	buy_will = 0 # The volume people want buy.
	sell_will = 0 # The volume people want sell.
	for k in range(PEOPLE_NUM):
		# If the will is not satisfied, they want the same thing.
		if people[k][WILL] == I_WANT_BUY and people[k][MONEY] > 0: # Want buy but still have money.
			buy_will += people[k][MONEY] / std_price[date] # They want all their money be the stock.
		if people[k][WILL] == I_WANT_SELL and people[k][STOCK] > 0: # Want sell but still have stock.
			sell_will += people[k][STOCK] # They want all their stock be the money.
	return buy_will, sell_will

# # Enable the possible deal.
# def fit_the_will(people, date, buy_will, sell_will, std_price):
# 	# print(buy_will, sell_will)
# 	# for i in range(len(people)):
# 	# 	print(people[i])
# 	fit_will = min(buy_will, sell_will)
# 	remain_buy_will = fit_will
# 	remain_sell_will = fit_will
# 	# Fit people's will
# 	for k in range(PEOPLE_NUM):
# 		# If this people want to buy and still have money, and other people want sell, fit the deal.
# 		if people[k][WILL] == I_WANT_BUY and people[k][MONEY] > 0 and remain_sell_will > 0: 
# 			# Still have enough people want to sell, fit all this people's will.
# 			if remain_sell_will > people[k][MONEY] / std_price[date]: 
# 				people[k][STOCK] = people[k][MONEY] / std_price[date]
# 				remain_sell_will -= people[k][MONEY] / std_price[date]
# 				people[k][MONEY] = 0
# 			# Still have people want to sell but not enough, fit all remain_sell_will.
# 			if remain_sell_will <= people[k][MONEY] / std_price[date]: 
# 				people[k][STOCK] = remain_sell_will
# 				people[k][MONEY] -= remain_sell_will * std_price[date]
# 				remain_sell_will = 0
# 		# If this people want to sell and still have stock, and other people want buy, fit the deal.
# 		if people[k][WILL] == I_WANT_SELL and people[k][STOCK] > 0 and remain_buy_will > 0:
# 			# Still have enough people want to buy, fit all this people's will.
# 			if remain_buy_will > people[k][STOCK]: 
# 				people[k][MONEY] = people[k][STOCK] * std_price[date]
# 				remain_buy_will -= people[k][STOCK]
# 				people[k][STOCK] = 0
# 			# Still have people want to buy but not enough, fit all remain_sell_will.
# 			if remain_buy_will <= people[k][STOCK]: 
# 				people[k][MONEY] = remain_buy_will * std_price[date]
# 				people[k][STOCK] -= remain_buy_will
# 				remain_buy_will = 0

# Enable the possible deal.
def fit_the_will(people, date, buy_will, sell_will, std_price):
	# print(buy_will, sell_will)
	# for i in range(len(people)):
	# 	print(people[i])
	fit_will = min(buy_will, sell_will)
	if fit_will == 0:
		return
	# Fit all less will.
	if buy_will >= sell_will:
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_SELL:
				people[k][MONEY] = people[k][STOCK] * std_price[date]
				people[k][STOCK] = 0
	if sell_will >= buy_will:
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_BUY:
				people[k][STOCK] = people[k][MONEY] / std_price[date]
				people[k][MONEY] = 0
	# The oppotunity of the great will should be dicide equally.
	if buy_will >= sell_will:
		ratio = sell_will / buy_will
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_BUY:
				people[k][STOCK] = ratio * people[k][MONEY] / std_price[date]
				people[k][MONEY] -= ratio * people[k][MONEY]
	if sell_will >= buy_will:
		ratio = buy_will / sell_will
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_SELL:
				people[k][MONEY] = ratio * people[k][STOCK] * std_price[date]
				people[k][STOCK] -= ratio * people[k][STOCK]

# Get the will for each people to buy and sell on tomorrow.
def move_the_will(people, date, std_price):
	for k in range(PEOPLE_NUM):
		# People think about what tomorrow they want to do.
		if people[k][WILL] == I_WANT_BUY: # The people want to buy.
			# When the current price touch the out price in people, they want sell.
			if (people[k][OUT_MOVE] >= 1 and std_price[date] > people[k][INIT_PRICE] * people[k][OUT_MOVE]) or \
			   (people[k][OUT_MOVE] <= 1 and std_price[date] < people[k][INIT_PRICE] * people[k][OUT_MOVE]):
				people[k][WILL] = I_WANT_SELL
				people[k][INIT_PRICE] = std_price[date]
		if people[k][WILL] == I_WANT_SELL: # The people want to sell.
			# When the current price touch the in price in people, they want buy.
			if (people[k][IN_MOVE] >= 1 and std_price[date] > people[k][INIT_PRICE] * people[k][IN_MOVE]) or \
			   (people[k][IN_MOVE] <= 1 and std_price[date] < people[k][INIT_PRICE] * people[k][IN_MOVE]):
				people[k][WILL] = I_WANT_BUY
				people[k][INIT_PRICE] = std_price[date]

def show_result(pool):
	# Show the data.
	print('=============')
	print('The old score')
	# print(pool)
	for i in range(5):
		print(pool[i][1])
	for i in range(1):
		print('The strategy', i)
		for j in range(PEOPLE_NUM):
			print(pool[i][0][j])
	print('=============')