import matplotlib.pyplot as plt
import numpy as np
import copy
from common import * 

std_price, std_volume = load_data()
arg = load_arg()
pool = arg[0]
glob_arg = arg[1]

predicted = []
stock_as_stock_list = []
money_as_stock_list = []
money_as_money_list = []
money_all_list = []
deal_day = []
people = copy.deepcopy(pool[0][0]) # Copy the best strategy init state.

# Show the data.
print('=============')
print('The best score.')
# print(pool)
for i in range(5):
	print(pool[i][1])
print('------------------------')
print('The best strategy.')
luck_people_num = int(PEOPLE_NUM / 4)
print('-----------------------------------------')
print('Money Printer:')
for k in range(0, luck_people_num):
	print(pool[0][0][k])
print('-----------------------------------------')
print('Stock Builder:')
for k in range(luck_people_num, luck_people_num * 2):
	print(pool[0][0][k])
print('-----------------------------------------')
print('Green Keeper:')
for k in range(luck_people_num * 2, PEOPLE_NUM):
	print(pool[0][0][k])
print('=============')

# For each day, calculate the diff between predicted volume and real volume.
for j in range(0, ALL_DATA): 
	old_people = copy.deepcopy(people)

	# For each people, calculate the trading volume cause by him.
	# First calculate the will for each people to buy and sell.
	buy_will, sell_will = get_the_will(people, j, std_price)
	# Second enable the possible deal, calculate the predicted_volume
	# Do not care about the wrong volume go to anywhere.
	fit_the_will(people, j, buy_will, sell_will, std_price)
	predicted_volume = min(buy_will, sell_will)
	predicted.append(predicted_volume)
	# At last get the will for each people to buy and sell on tomorrow.
	move_the_will(people, j, std_price)
	# Adjust the total money and total stock with time.
	adjust_the_world(people, glob_arg)

	# Count all the money and money in the market.
	money_as_money = 0
	money_as_stock = 0
	stock_as_stock = 0
	for k in range(PEOPLE_NUM):
		money_as_money += people[k][MONEY]
		money_as_stock += people[k][STOCK] * std_price[j]
		stock_as_stock += people[k][STOCK]
	money_all = money_as_money + money_as_stock
	money_as_stock_list.append(money_as_stock)
	money_as_money_list.append(money_as_money)
	stock_as_stock_list.append(stock_as_stock)
	money_all_list.append(money_all)

	# Show the deal day.
	if(min(buy_will,sell_will) != 0):
		deal_day.append(j)

	# Show the diff between people.
	if j != 100:
		continue
	for k in range(PEOPLE_NUM):
		for l in range(8):
			if old_people[k][l] != people[k][l]:
				print('people[', k, '][', l, '] ', old_people[k][l], '->', people[k][l])


# Show the total money and total stock.
print('=============')
print('The init total money and total stock.')
print('The init total money:', money_as_money_list[0])
print('The init total stock:', stock_as_stock_list[0])
print('=============')

# Show the money slope and stock slope.
print('=============')
print('The money slope and stock slope (the total change through the test).')
print('The money change:', glob_arg[MONEY_SLOPE] * ALL_DATA)
print('The stock change:', glob_arg[STOCK_SLOPE] * ALL_DATA)
print('=============')


plt.plot(std_price, color='blue')
plt.plot(std_volume, color='red')
plt.plot(predicted, color='green')
# plt.plot(money_all_list, color='yellow', linestyle='-.')
# plt.plot(money_as_money_list, color='cyan', linestyle='-.')
plt.plot(money_as_stock_list, color='darkslategray', linestyle='-.')
plt.plot(stock_as_stock_list, color='magenta', linestyle='-.')

for i in range(len(deal_day)):
	plt.plot([deal_day[i], deal_day[i]], [1.0, 1.1], color='black')
plt.plot([TRAIN_DATA, TRAIN_DATA], [0, 1], color='black')
plt.show()
