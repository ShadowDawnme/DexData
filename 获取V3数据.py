import os
import requests
import json
import datetime
from pathlib import Path

# 定义函数将时间戳转换为常规时间格式
def convert_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# 定义要查询的日期
date = '2023-05-05'

# 将日期转换为时间戳
timestamp = int(datetime.datetime.strptime(date, '%Y-%m-%d').timestamp())

# 定义每页查询的交易数量
page_size = 1000
# 定义存储所有交易的列表
all_swaps = []

url = "https://thegraph.com/hosted-service/subgraph/ianlapham/uniswap-v2-dev"

cursor = None
end_of_results = False

while not end_of_results:
    # 定义查询语句
    query = """
      {
        swaps(first: %d, where: {
          pool: "0x495b5f9b40684172cd3945a484e674967bac2ec6",
          timestamp_gte: %d,
          timestamp_lt: %d
        }, orderBy: timestamp, orderDirection: asc%s) {
          id
          token0 {
            symbol
          }
          token1 {
            symbol
          }
          pool {
            feeTier
          }
          tick
          transaction {
            blockNumber
          }
          timestamp
          sender
          recipient
          amount0
          amount1
          amountUSD
          logIndex
        }
      }
    """ % (page_size, timestamp, timestamp + 86400, ', after: "%s"' % cursor if cursor else "")

    # 发送请求并获取数据
    request = requests.post(url, json={'query': query})
    json_data = json.loads(request.text)

    if 'data' in json_data and 'swaps' in json_data['data']:
        swaps = json_data['data']['swaps']

        # 转换时间戳为常规时间格式，并将其添加到交易数据中
        for swap in swaps:
            timestamp = int(swap['timestamp'])
            swap['timestamp'] = convert_timestamp(timestamp)

        # 将当前页的交易数据添加到总列表中
        all_swaps.extend(swaps)

        # 检查是否有下一页数据
        end_of_results = len(swaps) < page_size
        if not end_of_results:
            cursor = swaps[-1]['id']


# 计算实际获取的交易总数
total_swaps = len(all_swaps)

# 打印交易总数
print("实际交易数：", total_swaps)

# 获取桌面路径
desktop_path = Path.home() / 'Desktop'

# 将数据保存到本地txt文件中
file_path = desktop_path / '20022_05_WETH_DAI.txt'

with open(file_path, 'a') as file:
    file.write(json.dumps(all_swaps, indent=4))

print("数据已保存到文件：", file_path)
print(date)

