# people_run
试图通过统计的方法找出股票市场的某些共性。已经找到的共性有：
## 1. days_probability
![image](https://user-images.githubusercontent.com/32698786/123397576-275ba580-d5d5-11eb-8b94-a7b76edca9f0.png)  
在30~50个交易日的时间跨度中，追跌杀涨的策略胜率高了0.02。
## 2. the_big_down
![image](https://user-images.githubusercontent.com/32698786/123398954-a7ced600-d5d6-11eb-89d3-40e13855bc9f.png)  
在每次证券指数发生单日大幅度（超过2%）上涨下跌前，通常经过一段相对较长的平缓上升时期，再加一段相对较短的快速下跌时期。
## 3. image_analysis


https://user-images.githubusercontent.com/32698786/123452057-a0c4b980-d610-11eb-90e6-e54cbe773210.mp4

统计历史上和当前走势相似的数据，再通过其后续走势预测当前后续走势。成功概率0.483。  
## 4. the_support
历史上的高点和低点会不会影响股价明天的走势？当今天的股价达到了近历史上的一个高点，明天突破这个价位的概率会变大还是变小？  
这里给出一个统计上的答案：到达历史高点并向上突破的概率为0.518，到达历史低点并向下突破的概率为0.437。  
ps: 这里用到的数据量较小（到达历史高点27次，到达历史低点32次），且改变参数后结果差异较大。  


https://user-images.githubusercontent.com/32698786/123956686-8c503a80-d9dd-11eb-93aa-6fa06ef02574.mp4

