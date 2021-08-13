from gm.api import *
import pickle

set_token('73a0d001a70b39cb71b16bb0eeea56ab0ca38211')

# SEC_TYPE_STOCK = 1                          # 股票
# SEC_TYPE_FUND = 2                           # 基金
# SEC_TYPE_INDEX = 3                          # 指数
# SEC_TYPE_FUTURE = 4                         # 期货
# SEC_TYPE_OPTION = 5                         # 期权
# SEC_TYPE_CREDIT = 6                         # 信用交易
# SEC_TYPE_BOND = 7                           # 债券
# SEC_TYPE_BOND_CONVERTIBLE = 8               # 可转债
# SEC_TYPE_CONFUTURE = 10                     # 虚拟合约
# Take all symbols.
tmp = get_instruments(sec_types = 2, fields='symbol')
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

file = open(r"./all_fund.data","wb")
pickle.dump(instruments, file)
file.close()