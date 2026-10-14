import pandas as pd

def warning_demo(df):
    #设置预警阈值（业务自定义)
    upper_threshold = 0.40  # 渗透率上限阈值
    lower_threshold = 0.25  # 渗透率下限阈值：25%
    #异常标记
    def check_warning(value):
        if value > upper_threshold:
            return "渗透率过高"
        elif value < lower_threshold:
            return "渗透率过低"
        else:
            return "正常"

    # 新增预警状态列
    print(df.columns.tolist())
    print(df.columns.tolist()[0].encode('unicode_escape'))
    df["warning_status"] = df["charttype_nev"].apply(check_warning)

    #筛选异常数据并输出预警信息
    abnormal_df = df[df["warning_status"] != "正常"]
    print("===== 指标预警结果 =====")
    if len(abnormal_df) > 0:
        print("检测到异常月份：")
        print(abnormal_df[["月份", "charttype_nev", "warning_status"]])
    else:
        print("所有月份指标均在正常阈值区间内")

    return df, abnormal_df


#测试
if __name__ == "__main__":
    df_final = pd.read_csv("car_sales_final.csv")
    df_result, abnormal_data = warning_demo(df_final)
    df_result.to_csv("car_sales_warning_result.csv", index=False, encoding="utf-8-sig")
    print(df_result)
