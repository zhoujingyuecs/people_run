import matplotlib.pyplot as plt
import numpy as np
import copy
from common import * 

std_price, std_volume = load_data()
pool = load_pool()
show_result(pool)

predicted = []
money_as_stock_list = []
money_all_list = []
deal_day = []
people = copy.deepcopy(pool[0][0]) # Copy the best strategy init state.

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

	# Count all the money and money in the market.
	money_as_money = 0
	money_as_stock = 0
	for k in range(PEOPLE_NUM):
		money_as_money += people[k][MONEY]
		money_as_stock += people[k][STOCK] * std_price[j]
	money_all = money_as_money + money_as_stock
	money_as_stock_list.append(money_as_stock)
	money_all_list.append(money_all)

	# Show the deal day.
	if(min(buy_will,sell_will) != 0):
		deal_day.append(j)

	# Show the diff between people.
	if j > 2:
		continue
	for k in range(PEOPLE_NUM):
		for l in range(8):
			if old_people[k][l] != people[k][l]:
				print('people[', k, '][', l, '] ', old_people[k][l], '->', people[k][l])

plt.plot(std_price, color='blue')
plt.plot(std_volume, color='red')
plt.plot(predicted, color='green')
plt.plot(money_as_stock_list, color='magenta')
plt.plot(money_all_list, color='yellow')
# for i in range(len(deal_day)):
# 	plt.plot([deal_day[i], deal_day[i]], [0, 0.2], color='black')
plt.plot([TRAIN_DATA, TRAIN_DATA], [0, 1], color='black')
plt.show()
