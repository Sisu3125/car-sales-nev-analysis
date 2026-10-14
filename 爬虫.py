import sys
import subprocess

import pd

libs = ["pandas","numpy","matplotlib","seaborn","requests"]
for lib in libs:
    try:
        __import__(lib)
        print(f"{lib} 装好能用")
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
print("所有库准备好了")

import pandas as pd

import requests
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
session=requests.Session()
session.headers.update(headers)
url="https://data.cpcadata.com/api/chartlist?charttype=6"
try:
    resp=session.head(url,timeout=10)
    if resp.status_code == 200:
        print("链接可用可以继续")
    else:
        print(f"链接异常，{resp.status_code}")
except Exception as e:
    print("访问失败",e)
    exit()
resp_get = session.get(url, timeout=5)
if resp_get.status_code == 200:
    html = resp_get.text
    try:
        json_data = resp_get.json()
    except Exception as e:
        print("接口返回不是合法JSON", e)
        json_data = None
    binary_data = resp_get.content
    status = resp_get.status_code
else:
    print(f"GET请求失败，状态码：{resp_get.status_code}")
print(type(json_data))
if isinstance(json_data, list):
    print("接口返回外层是列表，取第一个元素")
    root = json_data[0]
    root = json_data[0]
    print("root里面所有key：", root.keys())
    print("root完整内容：", root)
else:
    root = json_data

data_list = root["dataList"]
rows = []
for item in data_list:
    row = {
        "month": item['month'],
        "sale_2026": item.get("2026年", [None])[0],
        "sale_2025": item.get("2025年", [None])[0]

    }
    rows.append(row)

def fetch_cpc_data(charttype):
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.3.3"}
    session=requests.Session()
    session.headers.update(headers)
    url = f"https://data.cpcadata.com/api/chartlist?charttype={charttype}"
    resp_get = session.get(url, timeout=5)
    json_data = None
    if resp_get.status_code == 200:
        json_data = resp_get.json()
    else:
        print(f"charttype={charttype} 请求失败")
        return pd.DataFrame()
    print(type(json_data))
    if isinstance(json_data, list):
        print(f"charttype={charttype}: 接口外层是列表，取第一个元素")
        root = json_data[0]
    else:
        root = json_data

    data_list = root["dataList"]
    rows = []
    for item in data_list:
        row = {
            "月份": item["month"],
            "2026销量": item.get("2026年", [None])[0],
            "2025销量": item.get("2025年", [None])[0]
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df["charttype"] = charttype
    return df
df_total = fetch_cpc_data(1)
df_nev = fetch_cpc_data(6)
df_merge = pd.merge(df_total, df_nev, on="月份", suffixes=["_total","_nev"])
df_merge["2026燃油销量"] = df_merge["2026销量_total"] - df_merge["2026销量_nev"]
df_merge["2025燃油销量"] = df_merge["2025销量_total"] - df_merge["2025销量_nev"]

df_merge["2026燃油销量"] = df_merge["2026销量_total"] - df_merge["2026销量_nev"]
df_merge["2025燃油销量"] = df_merge["2025销量_total"] - df_merge["2025销量_nev"]

df_merge.to_csv("car_sales_final.csv", index=False, encoding="utf-8-sig")
print(df_merge.head())

df_raw = pd.read_csv(r"car_sales_final.csv", encoding="utf-8-sig")

# 提取数字月份
df_raw["m_num"] = df_raw["月份"].str.extract(r"(\d+)").astype(int)

#构造 2025 年的子表
df_2025 = df_raw[["m_num", "月份", "2025燃油销量", "2025销量_nev"]].copy()
df_2025["year"] = 2025
df_2025.rename(columns={
    "2025燃油销量":"fuel_sale",
    "2025销量_nev":"ev_sale"
}, inplace=True)

#构造 2026 年的子表
df_2026 = df_raw[["m_num", "月份", "2026燃油销量", "2026销量_nev"]].copy()
df_2026["year"] = 2026
df_2026.rename(columns={
    "2026燃油销量":"fuel_sale",
    "2026销量_nev":"ev_sale"
}, inplace=True)

df_long = pd.concat([df_2025, df_2026], ignore_index=True) #上下合并2025、2026两年

month_map = {
    1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun", #生成英文月份缩写
    7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"
}
df_long["month_en"] = df_long["m_num"].map(month_map)

df_long["month"] = df_long["month_en"] + "-" + (df_long["year"]%100).astype(str) #拼接成格式

df_final = df_long[["month","fuel_sale","ev_sale"]].copy() #保留需要的列数并调整顺序

df_final["dt"] = pd.to_datetime(df_final["month"], format="%b-%y") #按时间排序
df_final = df_final.sort_values("dt").reset_index(drop=True)
df_final.drop(columns=["dt"], inplace=True)

df_final.to_csv("car_sale_long_format.csv", index=False, encoding="utf-8-sig") #输出csv
print(df_final.head(10))




































