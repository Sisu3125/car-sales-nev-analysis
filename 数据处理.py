import sys
import subprocess
libs = ["pandas","numpy","matplotlib","seaborn"]
for lib in libs:
    try:
        __import__(lib)
        print(f"{lib} 装好能用")
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
print("所有库准备好了")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei",]
plt.rcParams["axes.unicode_minus"] = False


#数据检查
df = pd.read_csv(r"D:\PythonProject2\car_sale_long_format.csv",  #跳过空行、注释行，兼容中文编码
                 skip_blank_lines=True,
                 comment="#",
                 encoding="utf-8-sig")
print(df.head())#前五行检查数据
print(df.info())#看类型,缺失值
print(df.describe())#基础统计量（均值、最值等)
print(df.columns)#查看列名
df.rename(columns={},inplace=True)#重命名列


#数据清洗
 #缺失值处理
print(df.isnull().sum())#查看缺失值数量
df["fuel_sale"] = df["fuel_sale"].interpolate(method="linear") #对燃油销量做线性插值(少量的缺失用
df["ev_sale"] = df["ev_sale"].interpolate(method="linear") #新能源车销量线性插值(线性保留时间连续性
print(df.isnull().sum()) #检查是否还有缺失值

 #异常值处理
sns.boxplot(data=df[["fuel_sale","ev_sale"]]) #生成箱线图来识别异常值
plt.show()
def remove_outlier(df_in, col_name): #IQR方法剔除异常值
    q1 = df_in[col_name].quantile(0.25) #看下四分数
    q3 = df_in[col_name].quantile(0.75) #看上四分数
    iqr = q3-q1 #看中间50%正常数据分布宽度
    low  = q1 - 1.5*iqr #划定安全下界
    high = q3 + 1.5*iqr #划定安全上界
    df_out = df_in.loc[(df_in[col_name] > low) & (df_in[col_name] < high)]
    return df_out
df = remove_outlier(df,"fuel_sale")
df = remove_outlier(df,"ev_sale")


#数据处理
 #时间列处理(转码，排序
df["month"] = pd.to_datetime(df["month"], format="%b-%y")
df.loc[df["month"].dt.year < 2000, "month"] += pd.DateOffset(years=2000)
df = df.sort_values("month").reset_index(drop=True)

 #构建衍生的指标
  #渗透率(描述替代关系变化
df["total_sale"] = df["ev_sale"] + df["fuel_sale"]
df = df[df["total_sale"] > 0] #过滤销量避免总销量为零算出异常
df["penetration"] = df["ev_sale"] / df["total_sale"]
df["penetration_pct"] = df["penetration"] * 100 #转成百分比方便看

 #构建分析渗透率的指标(环比变化:绝对变化，环比增长率:相对增长速度
df["penetration_diff"] = df["penetration_pct"].diff() #环比变化
df["penetration_growth"] = df["penetration"].pct_change() #环比增长率
df.loc[0, "penetration_diff"] = 0  #首行没有上月数据，填充为0避免留空值
df.loc[0, "penetration_growth"] = 0

 #用波动较小的年单位来看
df["year"] = df["month"].dt.year #提取年份
year_agg = df.groupby("year")["penetration_pct"].mean() #按年份分组，计算每年平均渗透率
year_agg = year_agg.reset_index() #转成DataFrame
year_agg["year_diff"] = year_agg["penetration_pct"].diff()#计算年环比变化
year_agg["year_growth"] = year_agg["penetration_pct"].pct_change() #计算环比增长率

 #空值填充
df["penetration_diff"] = df["penetration_pct"].diff()
df["penetration_growth"] = df["penetration_pct"].pct_change().fillna(0) #相对增长率，NaN填0

#描述性统计
 #输出月各销量，渗透率的基本统计指标情况(表格
desc_table = df[["fuel_sale","ev_sale","penetration"]].describe() #输出各销量渗透率的基本统计结果(最小值、最大值、平均值)形成表格
desc_table.to_csv("月各销量，渗透率的基本统计指标结果表.csv") #表格导出为本地文件
print(desc_table) #控制台输出检查
#输出年渗透率的基本统计指标情况(表格
year_desc_table = year_agg[["penetration_pct", "year_diff", "year_growth"]].describe()
year_desc_table.to_csv("渗透率的基本统计指标结果表.csv") #表格导出为本地文件
print(year_desc_table) #控制台输出检查


#用Matplotlib可视化

 #月销量，渗透率相关的情况
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True) #创建空多子图画布
  #第一张子图：燃油车+新能源车月度销量趋势
ax1.plot(df["month"], df["fuel_sale"], label="燃油车销量", color="gray") #创建折线燃油车销量图
ax1.plot(df["month"], df["ev_sale"], label="新能源车销量", color="blue") #创建折线新能源车销量图
ax1.set_title("国内汽车月度销量变化趋势")
ax1.set_ylabel("销量（辆）")
ax1.legend()
ax1.grid(alpha=0.3)
  #第二张子图：新能源渗透率月度变化趋势
ax2.plot(df["month"], df["penetration_pct"], label="新能源渗透率", color="red") #创建新能源渗透率折线图
ax2.set_title("新能源汽车月度渗透率变化趋势")
ax2.set_xlabel("月份")
plt.xticks(rotation=45)
ax2.set_ylabel("渗透率（%）")
ax2.legend()
ax2.grid(alpha=0.3)
plt.tight_layout() #防止标题重叠
plt.savefig("新能源汽车月度渗透率趋势图.png", dpi=300)
plt.show()

 #月渗透率相关指标变化趋势(渗透率即替代关系的具体分析

fg, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(12, 10), sharex=True)
ax1.plot(df["month"], df["penetration_pct"], marker='.', color='gold', linewidth=2, label="月度渗透率(%)")#子图1：月度渗透率黄色折线
ax1.set_ylabel("渗透率(%)")
ax1.set_title("新能源汽车月度渗透率及环比指标时序图")
ax1.legend()
ax1.grid(alpha=0.3)
bar_width = pd.Timedelta(days=14)

ax2.bar(df["month"], df["penetration_diff"], width=bar_width, alpha=0.7, color='blue', label="当月环比提升百分点")#子图2：环比提升百分点蓝色柱子
ax2.set_ylabel("环比提升百分点")
ax2.legend()
ax2.grid(alpha=0.3)

ax3.plot(df["month"], df["penetration_growth"], marker='.', color='green', linewidth=2, label="当月环比增长率")#子图3：环比增长率绿色折线
ax3.set_xlabel("月份")
ax3.set_ylabel("环比增长率")
ax3.legend()
ax3.grid(alpha=0.3)
ax2.axhline(y=0, color='black', linestyle='--', alpha=0.6)
ax3.axhline(y=0, color='black', linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("月度渗透率趋势图.png", dpi=300)
plt.show()

 #年渗透率标化趋势
plt.figure(figsize=(10, 6)) #创建空白单画布绘图
plt.plot(year_agg["year"], year_agg["penetration_pct"], marker='o', color='red', label="年度平均渗透率") #创建年度平均渗透率折线图
plt.bar(year_agg["year"], year_agg["year_diff"],width=0.3, alpha=0.8 , color='blue', label="当年环比提升百分点") #叠加画年环比变化柱状图
plt.title("新能源汽车渗透率年度变化趋势")
plt.xlabel("年份")
plt.xticks(rotation=45)
plt.ylabel("渗透率")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("年度渗透率趋势图.png", dpi=300)
plt.show()


fgg, ax1 = plt.subplots(figsize=(10,6))

# 左Y轴：年度平均渗透率 红色折线
ax1.plot(year_agg["year"], year_agg["penetration_pct"], marker='o', color='red', linewidth=2, label="年度平均渗透率")
ax1.set_xlabel("年份")
ax1.set_ylabel("渗透率(%)", color="red")
ax1.tick_params(axis='y', labelcolor="red")
ax1.grid(alpha=0.3)

# 右Y轴：当年环比提升百分点，蓝色柱子，width=0.2 收窄柱子，不会横向拉长
ax2 = ax1.twinx()
bar = ax2.bar(year_agg["year"], year_agg["year_diff"], width=0.2, alpha=0.7, color="blue", label="当年环比提升百分点")
ax2.set_ylabel("环比提升百分点", color="blue")
ax2.tick_params(axis='y', labelcolor="blue")

# 合并图例
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

plt.title("新能源汽车渗透率年度变化趋势")
plt.tight_layout()
plt.savefig("年度渗透率趋势图.png", dpi=300)
plt.show()


