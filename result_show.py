import pickle
import matplotlib.pyplot as plt
import numpy as np
import copy
import random

POOL_SIZE = 20        # How many strategy in the pool.
PEOPLE_NUM = 50       # How many people in this stock world.
TRAIN_TIME = 10000    # How many time the training repeat.
TRAIN_DATA = 4000     # How many data the training use.
ALL_DATA = 5000       # The data including training and testing.

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
pool = []

# Calculate the will for each people to buy and sell on the day.
def get_the_will(people, date):
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
def fit_the_will(people, date, buy_will, sell_will):
	fit_will = min(buy_will, sell_will)
	remain_buy_will = fit_will
	remain_sell_will = fit_will
	# Fit people's will
	for k in range(PEOPLE_NUM):
		# If this people want to buy and still have money, and other people want sell, fit the deal.
		if people[k][WILL] == I_WANT_BUY and people[k][MONEY] > 0 and remain_sell_will > 0: 
			# Still have enough people want to sell, fit all this people's will.
			if remain_sell_will > people[k][MONEY] / std_price[date]: 
				people[k][STOCK] = people[k][MONEY] / std_price[date]
				remain_sell_will -= people[k][MONEY] / std_price[date]
				people[k][MONEY] = 0
			# Still have people want to sell but not enough, fit all remain_sell_will.
			if remain_sell_will <= people[k][MONEY] / std_price[date]: 
				people[k][STOCK] = remain_sell_will
				people[k][MONEY] -= remain_sell_will * std_price[date]
				remain_sell_will = 0
		# If this people want to sell and still have stock, and other people want buy, fit the deal.
		if people[k][WILL] == I_WANT_SELL and people[k][STOCK] > 0 and remain_buy_will > 0:
			# Still have enough people want to buy, fit all this people's will.
			if remain_buy_will > people[k][STOCK]: 
				people[k][MONEY] = people[k][STOCK] * std_price[date]
				remain_buy_will -= people[k][STOCK]
				people[k][STOCK] = 0
			# Still have people want to buy but not enough, fit all remain_sell_will.
			if remain_buy_will <= people[k][STOCK]: 
				people[k][MONEY] = remain_buy_will * std_price[date]
				people[k][STOCK] -= remain_buy_will
				remain_buy_will = 0

# Get the will for each people to buy and sell on tomorrow.
def move_the_will(people, date):
	for k in range(PEOPLE_NUM):
		# If the will has been satisfied, they think about what tomorrow they want to do.
		if people[k][WILL] == I_WANT_BUY and people[k][MONEY] == 0: # The people all in stock.
			# When the current price touch the out price in people, they want sell.
			if (people[k][OUT_MOVE] > 1 and std_price[date] > people[k][INIT_PRICE] * people[k][OUT_MOVE]) or \
			   (people[k][OUT_MOVE] < 1 and std_price[date] < people[k][INIT_PRICE] * people[k][OUT_MOVE]):
				people[k][WILL] = I_WANT_SELL
				people[k][INIT_PRICE] = std_price[date]
		if people[k][WILL] == I_WANT_SELL and people[k][STOCK] == 0: # The people all in money.
			# When the current price touch the in price in people, they want buy.
			if (people[k][IN_MOVE] > 1 and std_price[date] > people[k][INIT_PRICE] * people[k][IN_MOVE]) or \
			   (people[k][IN_MOVE] < 1 and std_price[date] < people[k][INIT_PRICE] * people[k][IN_MOVE]):
				people[k][WILL] = I_WANT_BUY
				people[k][INIT_PRICE] = std_price[date]

def take_score(strategy):
    return strategy[1]

def load_pool():
	global pool # This function need to change the value of pool
	file = open(r"./pool.data","rb")
	pool = pickle.load(file)
	file.close()

def show_result():
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


load_pool()
show_result()

predicted = []
people = copy.deepcopy(pool[0][0]) # Copy the best strategy init state.
# For each day, calculate the diff between predicted volume and real volume.
for j in range(0, ALL_DATA): 
	# For each people, calculate the trading volume cause by him.
	# First calculate the will for each people to buy and sell.
	buy_will, sell_will = get_the_will(people, j)
	# Second enable the possible deal, calculate the predicted_volume
	# Do not care about the wrong volume go to anywhere.
	fit_the_will(people, j, buy_will, sell_will)
	predicted_volume = min(buy_will, sell_will)
	predicted.append(predicted_volume)
	# At last get the will for each people to buy and sell on tomorrow.
	move_the_will(people, j)

# x = []
# for i in range(len(std_price)):
# 	x.append(i)

# plt.bar(x, std_price, color='blue')
plt.plot(std_price, color='blue')
plt.plot(std_volume, color='red')
plt.plot(predicted, color='green')
plt.plot([4000, 4000], [0, 1], color='yellow')
plt.show()
