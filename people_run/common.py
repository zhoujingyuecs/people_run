import pickle
import copy
import random

POOL_SIZE = 50         # How many strategy in the pool.
PEOPLE_NUM = 400        # How many people in this stock world.
TRAIN_TIME = 10000000  # How many time the training repeat.
TRAIN_DATA = 3000      # How many data the training use.
ALL_DATA = 5000        # The data including training and testing.

TRAIN_SPEED = 50000         # Adjust the para changing spped.

# Init the people
# The type of will
I_WANT_BUY = 1
I_WANT_SELL = 0
# The structure of people
WILL = 0
MONEY = 1
STOCK = 2
INIT_PRICE = 3
IN_MIN = 4
IN_MAX = 5
OUT_MIN = 6
OUT_MAX = 7
# The structure of glob_arg
MONEY_SLOPE = 0
STOCK_SLOPE = 1

def init_arg():
	init_people = [] # [will, money, stock, init_price, in_min, in_max, out_min, out_max], will: 1 mean buy, 0 means sell.
	glob_arg = [0.0, 0.0] # [money_slope, stock_slope]
	for i in range(0, int(PEOPLE_NUM / 2)):
		init_people.append([0, 0.002, 0.002, 0.2, 1.0, 1.0, 1.0, 1.0])
	for i in range(int(PEOPLE_NUM / 2), PEOPLE_NUM):
		init_people.append([1, 0.002, 0.002, 0.2, 1.0, 1.0, 1.0, 1.0])
	# Init the pool
	# The people in the pool means the init state of people and the strategy of people.
	pool = []
	for i in range(POOL_SIZE):
		pool.append([copy.deepcopy(init_people), -1]) # [people, score]
	arg = [pool, glob_arg]
	return arg

def random_init_arg():
	pool = [] # [will, money, stock, init_price, in_min, in_max, out_min, out_max], will: 1 mean buy, 0 means sell.
	glob_arg = [] # [money_slope, stock_slope]
	for i in range(POOL_SIZE):
		people = []
		for k in range(PEOPLE_NUM):
			one_person = []
			if random.random() > 0.5:
				one_person.append(I_WANT_BUY)
			else:
				one_person.append(I_WANT_SELL)
			for l in range(7):
				one_person.append(random.random() * 2)
			people.append(one_person)
		pool.append([people, -1])
	# glob_arg.append(random.random() * 2)
	# glob_arg.append(random.random() * 2)
	glob_arg = [0.0, 0.0]
	arg = [pool, glob_arg]
	return arg

def save_arg(arg):
	file = open(r"./arg.data","wb")
	pickle.dump(arg, file)
	file.close()

def load_arg():
	file = open(r"./arg.data","rb")
	arg = pickle.load(file)
	file.close()
	return arg

def magic_load_arg():
	file = open(r"./arg.data","rb")
	arg = pickle.load(file)
	old_pool = arg[0] 
	file.close()
	pool = []
	for i in range(POOL_SIZE):
		people = []
		lucky_strategy = random.randint(0, len(old_pool) - 1)
		for j in range(PEOPLE_NUM):
			lucky_person = random.randint(0, len(old_pool[lucky_strategy][0]) - 1)
			people.append(old_pool[lucky_strategy][0][lucky_person])
		pool.append([copy.deepcopy(people), -1])
	return [pool, arg[1]]

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
				people[k][MONEY] += people[k][STOCK] * std_price[date]
				people[k][STOCK] = 0
	if sell_will >= buy_will:
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_BUY:
				people[k][STOCK] += people[k][MONEY] / std_price[date]
				people[k][MONEY] = 0
	# The oppotunity of the great will should be dicide equally.
	if buy_will >= sell_will:
		ratio = sell_will / buy_will
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_BUY:
				people[k][STOCK] += ratio * people[k][MONEY] / std_price[date]
				people[k][MONEY] -= ratio * people[k][MONEY]
	if sell_will >= buy_will:
		ratio = buy_will / sell_will
		for k in range(PEOPLE_NUM):
			if people[k][WILL] == I_WANT_SELL:
				people[k][MONEY] += ratio * people[k][STOCK] * std_price[date]
				people[k][STOCK] -= ratio * people[k][STOCK]

# Get the will for each people to buy and sell on tomorrow.
def move_the_will(people, date, std_price):
	for k in range(PEOPLE_NUM):
		# People think about what tomorrow they want to do.
		if people[k][WILL] == I_WANT_BUY: # The people want to buy.
			# When the current price beyound the out price in people, they want sell.
			if std_price[date] >= people[k][OUT_MAX] * people[k][INIT_PRICE] or std_price[date] <= people[k][OUT_MIN] * people[k][INIT_PRICE]:
				people[k][WILL] = I_WANT_SELL
				people[k][INIT_PRICE] = std_price[date]
			continue
		if people[k][WILL] == I_WANT_SELL: # The people want to sell.
			# When the current price beyound the in price in people, they want buy.
			if std_price[date] >= people[k][IN_MAX] * people[k][INIT_PRICE] or std_price[date] <= people[k][IN_MIN] * people[k][INIT_PRICE]:
				people[k][WILL] = I_WANT_BUY
				people[k][INIT_PRICE] = std_price[date]
			continue

# Adjust the total money and total stock with time.
def adjust_the_world(people, glob_arg):
	luck_people_num = int(PEOPLE_NUM / 4)
	# Money printer.
	for k in range(0, luck_people_num):
		people[k][MONEY] += glob_arg[MONEY_SLOPE] / float(luck_people_num)
	# Stock builder.
	for k in range(luck_people_num, luck_people_num * 2):
		people[k][STOCK] += glob_arg[STOCK_SLOPE] / float(luck_people_num)