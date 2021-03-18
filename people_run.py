import pickle
import matplotlib.pyplot as plt
import numpy as np
import copy
import random
from common import * 

def calculate(pool, std_price, std_volume):
	# For each strategy, calculate the score.
	for i in range(POOL_SIZE): 
		# If this strategy already got the score, no need to calculate again.
		if pool[i][1] != -1:
			continue
		score = 0 # Score is the difference between real_volume and predicted_volume
		people = copy.deepcopy(pool[i][0]) # Copy the people to avoid breaking the strategy state.
		# For each day, calculate the diff between predicted volume and real volume.
		for j in range(0, TRAIN_DATA): 
			real_volume = std_volume[j]
			# For each people, calculate the trading volume cause by him.
			# First calculate the will for each people to buy and sell.
			buy_will, sell_will = get_the_will(people, j, std_price)
			# Second enable the possible deal, calculate the predicted_volume, add the score.
			# Do not care about the wrong volume go to anywhere.
			fit_the_will(people, j, buy_will, sell_will, std_price)
			predicted_volume = min(buy_will, sell_will)
			score += (predicted_volume - real_volume) * (predicted_volume - real_volume)
			# At last get the will for each people to buy and sell on tomorrow.
			move_the_will(people, j, std_price)
		pool[i][1] = score

def take_score(strategy):
    return strategy[1]

def pool_update(pool):
	# Sort the pool by score.
	pool.sort(key=take_score)
	# Replace the last half by top half strategy.
	half_pool = int(POOL_SIZE / 2)
	for i in range(half_pool):
		pool[i + half_pool][0] = copy.deepcopy(pool[i][0])
		pool[i + half_pool][1] = -1
	# Slightly change the new strategy.
	for i in range(half_pool):
		# print('strategy ', i, ':', pool[i][1])
		people = pool[i + half_pool][0]
		for k in range(PEOPLE_NUM):
			# The probability change one person.
			if random.random() < 0:
				continue
			# The probability change his init will.
			if random.random() < 0.3:
				if people[k][WILL] == 1:
					people[k][WILL] = 0
				if people[k][WILL] == 0:
					people[k][WILL] = 1
			# The probability change his init money.
			if random.random() < 0.2:
				people[k][MONEY] *= 1 + (random.random() - 0.5) / 500
			# The probability change his init stock.
			if random.random() < 0.2:
				people[k][STOCK] *= 1 + (random.random() - 0.5) / 500
			# The probability change his init price.
			if random.random() < 0.2:
				people[k][INIT_PRICE] *= 1 + (random.random() - 0.5) / 500
			# The probability change his favor to buy.
			if random.random() < 0.2:
				people[k][IN_MOVE] *= 1 + (random.random() - 0.5) / 500
			# The probability change his favor to sell.
			if random.random() < 0.2:
				people[k][OUT_MOVE] *= 1 + (random.random() - 0.5) / 500
			# The probability he be another person.
			if random.random() < 0.2:
				pool_num = random.randint(0, half_pool - 1)
				person_num = random.randint(0, PEOPLE_NUM - 1)
				while random.random() > 0.5:
					num = random.randint(0, 5)
					people[k][num] = pool[pool_num][0][person_num][num]

std_price, std_volume = load_data()
pool = load_pool()
# pool = magic_load_pool()
# pool = init_pool()
# show_result(pool)
# The main training function
for time in range(TRAIN_TIME):
	if time % 20 == 0:
		print('Best score in', time, 'time:', pool[0][1])
		save_pool(pool)
	calculate(pool, std_price, std_volume)
	pool_update(pool)