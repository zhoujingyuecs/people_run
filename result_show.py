import matplotlib.pyplot as plt
import numpy as np
import copy
from common import * 

std_price, std_volume = load_data()
pool = load_pool()
show_result(pool)

predicted = []
people = copy.deepcopy(pool[0][0]) # Copy the best strategy init state.
# For each day, calculate the diff between predicted volume and real volume.
for j in range(0, ALL_DATA): 
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

plt.plot(std_price, color='blue')
plt.plot(std_volume, color='red')
plt.plot(predicted, color='green')
plt.plot([4000, 4000], [0, 1], color='yellow')
plt.show()
