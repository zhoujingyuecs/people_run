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
		if (data[i][j - 0]['close'] > data[i][j - 1]['close'] and data[i][j - 1]['close'] > data[i][j - 2]['close']) or \
		   (data[i][j - 0]['close'] > data[i][j - 2]['close'] and data[i][j - 2]['close'] > data[i][j - 4]['close']) or \
		   (data[i][j - 0]['close'] > data[i][j - 3]['close'] and data[i][j - 3]['close'] > data[i][j - 6]['close']):
			# And have Ying Bao Yang.
			if data[i][j + 1]['open'] > data[i][j + 0]['close'] and data[i][j + 1]['close'] < data[i][j + 0]['open']:
				UP += 1
				# Sucessfully reversal.
				if data[i][j + 2]['close'] < data[i][j + 1]['close']:
					UP_AND_DOWN += 1
		# The trend is down.
		if (data[i][j - 0]['close'] < data[i][j - 1]['close'] and data[i][j - 1]['close'] < data[i][j - 2]['close']) or \
		   (data[i][j - 0]['close'] < data[i][j - 2]['close'] and data[i][j - 2]['close'] < data[i][j - 4]['close']) or \
		   (data[i][j - 0]['close'] < data[i][j - 3]['close'] and data[i][j - 3]['close'] < data[i][j - 6]['close']):
			# And have Yang Bao Ying.
			if data[i][j + 1]['open'] < data[i][j + 0]['close'] and data[i][j + 1]['close'] > data[i][j + 0]['open']:
				DOWN += 1
				# Sucessfully reversal.
				if data[i][j + 2]['close'] > data[i][j + 1]['close']:
					DOWN_AND_UP += 1

print('UP:', UP)
print('UP_AND_DOWN:', UP_AND_DOWN)
print('UP_AND_DOWN Sucessfully Expectation:', UP_AND_DOWN / UP)
print('DOWN:', DOWN)
print('DOWN_AND_UP:', DOWN_AND_UP)
print('DOWN_AND_UP Sucessfully Expectation:', DOWN_AND_UP / DOWN)