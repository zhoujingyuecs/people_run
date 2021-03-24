from gm.api import *
import pickle

set_token('73a0d001a70b39cb71b16bb0eeea56ab0ca38211')

# Take all symbols.
tmp = get_instruments(sec_types=1, fields='symbol')
instruments_name = []
for i in range(0, len(tmp)):
    instruments_name.append(tmp[i]['symbol'])
print(len(instruments_name))
# Take all stock infomation.
instruments = []
for i in range(0, len(instruments_name)):
    print(i)
    tmp = history(symbol=instruments_name[i], frequency='1d', adjust=2, start_time='2012-10-01 08:00:00',
             end_time='2020-10-01 08:00:00', fields='symbol,open,close,high,low,amount,volume,eob', skip_suspended=False)
    # print(tmp)
    instruments.append(tmp)

file = open(r"./all_stock.data","wb")
pickle.dump(instruments, file)
file.close()