import pickle
import matplotlib.pyplot as plt

file = open(r"./all_stock.data","rb")
data = pickle.load(file)
file.close()

TEST_RANGE = 900
TEST_STEP = 1
SCORE = []
ALL_DOWN_AND_UP = []
ALL_UP_AND_DOWN = []
for k in range(1, TEST_RANGE, TEST_STEP):
	DOWN = 0
	UP = 0
	DOWN_AND_UP = 0
	UP_AND_DOWN = 0
	NEXT_UP = 0
	NEXT_DOWN = 0
	for i in range(len(data)): # For all stock.
		for j in range(TEST_RANGE, len(data[i]) - TEST_RANGE): # For every day.
			if data[i][j + k]['close'] < data[i][j + 0]['close']:
				NEXT_DOWN += 1
			if data[i][j + k]['close'] > data[i][j + 0]['close']:
				NEXT_UP += 1
			# The trend is up.
			if data[i][j - 0]['close'] > data[i][j - k]['close']:
				UP += 1
				# Sucessfully reversal.
				if data[i][j + k]['close'] < data[i][j + 0]['close']:
					UP_AND_DOWN += 1
			# The trend is down.
			if data[i][j - 0]['close'] < data[i][j - k]['close']:
				DOWN += 1
				# Sucessfully reversal.
				if data[i][j + k]['close'] > data[i][j + 0]['close']:
					DOWN_AND_UP += 1

	DOWN_AND_DOWN = DOWN - DOWN_AND_UP
	UP_AND_UP = UP - UP_AND_DOWN
	ONE_SCORE = 0
	ONE_SCORE += abs(DOWN_AND_UP / DOWN - NEXT_UP / (NEXT_UP + NEXT_DOWN))
	ONE_SCORE += abs(UP_AND_UP / UP - NEXT_UP / (NEXT_UP + NEXT_DOWN))
	ONE_SCORE += abs(DOWN_AND_DOWN / DOWN - NEXT_DOWN / (NEXT_UP + NEXT_DOWN))
	ONE_SCORE += abs(UP_AND_DOWN / UP - NEXT_DOWN / (NEXT_UP + NEXT_DOWN))
	ALL_DOWN_AND_UP.append(DOWN_AND_UP / DOWN - NEXT_UP / (NEXT_UP + NEXT_DOWN))
	ALL_UP_AND_DOWN.append(UP_AND_DOWN / UP - NEXT_DOWN / (NEXT_UP + NEXT_DOWN))
	SCORE.append(ONE_SCORE)

	print('TIME_SPAN:', k)
	print('-----------')
	print('UP:', UP, 'Days')
	print('DOWN:', DOWN, 'Days')
	print('Totally UP Expectation:', UP / (UP + DOWN))
	print('Totally DOWN Expectation:', DOWN / (UP + DOWN))
	print('NEXT_UP:', NEXT_UP, 'Days')
	print('NEXT_DOWN:', NEXT_DOWN, 'Days')
	print('Totally NEXT_UP Expectation:', NEXT_UP / (NEXT_UP + NEXT_DOWN))
	print('Totally NEXT_DOWN Expectation:', NEXT_DOWN / (NEXT_UP + NEXT_DOWN))
	print('-----------')
	print('DOWN_AND_UP:', DOWN_AND_UP, 'Days')
	print('DOWN_AND_DOWN:', DOWN_AND_DOWN, 'Days')
	print('UP_AND_DOWN:', UP_AND_DOWN, 'Days')
	print('UP_AND_UP:',UP_AND_UP , 'Days')
	print('DOWN_AND_UP Sucessfully Expectation:', DOWN_AND_UP / DOWN)
	print('UP_AND_UP Sucessfully Expectation:', UP_AND_UP / UP)
	print('DOWN_AND_DOWN Sucessfully Expectation:', DOWN_AND_DOWN / DOWN)
	print('UP_AND_DOWN Sucessfully Expectation:', UP_AND_DOWN / UP)
	print('-----------')
	print('SCORE:', ONE_SCORE)
	print('=====================')

print(SCORE)
plt.plot(SCORE, color='blue')
plt.plot(ALL_DOWN_AND_UP, color='red')
plt.plot(ALL_UP_AND_DOWN, color='green')
plt.show()
