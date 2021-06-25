import pickle

file = open(r"./all_stock.data","rb")
data = pickle.load(file)
file.close()

DOWN = 0
UP = 0
DOWN_AND_UP = 0
UP_AND_DOWN = 0
for i in range(len(data)): # For all stock.
	for j in range(10, len(data[i]) - 10): # For every data.
		# The trend is up.
		if data[i][j - 0]['close'] > data[i][j - 1]['close']:
			UP += 1
			# Sucessfully reversal.
			if data[i][j + 2]['close'] < data[i][j + 1]['close']:
				UP_AND_DOWN += 1
		# The trend is down.
		if data[i][j - 0]['close'] < data[i][j - 1]['close']:
			DOWN += 1
			# Sucessfully reversal.
			if data[i][j + 2]['close'] > data[i][j + 1]['close']:
				DOWN_AND_UP += 1

print('UP:', UP, 'Days')
print('DOWN:', DOWN, 'Days')
print('Totally UP Expectation:', UP / (UP + DOWN))
print('Totally DOWN Expectation:', DOWN / (UP + DOWN))
print('-----------')
print('DOWN_AND_UP:', DOWN_AND_UP, 'Days')
print('UP_AND_DOWN:', UP_AND_DOWN, 'Days')
print('DOWN_AND_UP Sucessfully Expectation:', DOWN_AND_UP / DOWN)
print('UP_AND_DOWN Sucessfully Expectation:', UP_AND_DOWN / UP)

# Result:
# 
# UP: 2663256 Days
# DOWN: 2521126 Days
# Totally UP Expectation: 0.5137075161513948
# Totally DOWN Expectation: 0.4862924838486053
# -----------
# DOWN_AND_UP: 1296908 Days
# UP_AND_DOWN: 1295469 Days
# DOWN_AND_UP Sucessfully Expectation: 0.514416177533372
# UP_AND_DOWN Sucessfully Expectation: 0.48642301002982813
