import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 设置文件路径
input_file = "../BeijingPM20100101_20151231.csv"
output_file = "../AQI_levels_counts.csv"

# 检查输入文件是否存在
if not os.path.exists(input_file):
    print(f"错误: 文件 '{input_file}' 未找到。请确保文件存在于指定路径。")
    exit(1)

# 读取 CSV 文件
df = pd.read_csv(input_file)

# 检查必要的列是否存在
required_columns = ["year", "month", "day", "PM_Dongsi", "PM_Dongsihuan", "PM_Nongzhanguan", "PM_US Post"]
for col in required_columns:
    if col not in df.columns:
        print(f"错误: 列 '{col}' 不存在于数据中。请检查 CSV 文件。")
        exit(1)

# 将 PM 列转换为数值类型，非数值将被设置为 NaN
pm_columns = ["PM_Dongsi", "PM_Dongsihuan", "PM_Nongzhanguan", "PM_US Post"]
for col in pm_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 处理缺失值：按 PM 列进行线性插值
df[pm_columns] = df[pm_columns].interpolate(method="linear", limit_direction="both")

# 汇总为每日数据
df["date"] = pd.to_datetime(df[["year", "month", "day"]])
daily_aqi = df.groupby("date")[pm_columns].mean().reset_index()

# 计算每日 AQI（这里采用 PM 数据的平均值作为 AQI 的代表）
daily_aqi["AQI"] = daily_aqi[pm_columns].mean(axis=1)

# 对 AQI 进行上限裁剪，确保 AQI 不超过 500
daily_aqi["AQI"] = daily_aqi["AQI"].clip(upper=500)

# 定义 AQI 分级标准，严重污染没有上限
aqi_levels = [
    {"min": 0, "max": 50, "level": "优", "color": "绿色"},
    {"min": 51, "max": 100, "level": "良", "color": "黄色"},
    {"min": 101, "max": 150, "level": "轻度污染", "color": "橙色"},
    {"min": 151, "max": 200, "level": "中度污染", "color": "红色"},
    {"min": 201, "max": 300, "level": "重度污染", "color": "紫色"},
    {"min": 301, "max": np.inf, "level": "严重污染", "color": "棕红色"},
]


# 函数：根据 AQI 值获取对应的级别和颜色
def get_aqi_level(aqi):
    for level in aqi_levels:
        if level["min"] <= aqi <= level["max"]:
            return pd.Series([level["level"], level["color"]])
    # 由于 AQI 已被裁剪至 <=500，无需返回“超出范围”
    return pd.Series(["严重污染", "棕红色"])  # 默认归为“严重污染”


# 应用函数获取 AQI 级别和颜色
daily_aqi[["AQI_Level", "AQI_Color"]] = daily_aqi["AQI"].apply(get_aqi_level)

# 统计每个 AQI 级别对应的天数
aqi_counts = daily_aqi["AQI_Level"].value_counts().reset_index()
aqi_counts.columns = ["AQI_Level", "Number_of_Days"]

# 创建仅包含 'level' 和 'color' 的 DataFrame
aqi_levels_df = pd.DataFrame(aqi_levels)[["level", "color"]]

# 合并颜色信息
aqi_counts = aqi_counts.merge(aqi_levels_df, left_on="AQI_Level", right_on="level", how="left").drop("level", axis=1)

# 不需要处理“未知颜色”，因为所有 AQI 都被覆盖
# aqi_counts["color"] = aqi_counts["color"].fillna("未知颜色")  # 已移除

# 保存结果到 CSV 文件
aqi_counts.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"AQI 级别对应的天数统计已保存到: {output_file}")

# 可选：显示结果
print(aqi_counts)

# 可选：生成 AQI 级别的柱状图

# 创建颜色映射字典（中文颜色名映射到 matplotlib 颜色代码）
color_map = {"绿色": "green", "黄色": "yellow", "橙色": "orange", "红色": "red", "紫色": "purple", "棕红色": "maroon"}

# 根据 AQI_Level 的顺序排序（从优到严重污染）
aqi_order = ["优", "良", "轻度污染", "中度污染", "重度污染", "严重污染"]
aqi_counts["AQI_Level"] = pd.Categorical(aqi_counts["AQI_Level"], categories=aqi_order, ordered=True)
aqi_counts = aqi_counts.sort_values("AQI_Level")

# 获取对应的颜色列表
aqi_counts["Matplotlib_Color"] = aqi_counts["color"].map(color_map)

# 设置绘图风格
sns.set_theme(style="whitegrid")

plt.figure(figsize=(10, 6))
plt.rcParams["font.sans-serif"] = ["STHeiti"]
sns.barplot(
    x="AQI_Level",
    y="Number_of_Days",
    hue="AQI_Level",
    data=aqi_counts,
    palette=aqi_counts["Matplotlib_Color"].tolist(),
    dodge=False,
    legend=False,
    edgecolor=".6",
)

# 添加标题和标签
plt.title("各 AQI 级别对应的天数分布")
plt.xlabel("AQI 级别")
plt.ylabel("天数")

# 显示数值 - 修改为动态调整位置
for index, row in enumerate(aqi_counts.itertuples(index=False)):
    plt.text(
        x=index,
        y=row.Number_of_Days + max(aqi_counts["Number_of_Days"]) * 0.02,  # 调整间距
        s=row.Number_of_Days,
        color="black",
        ha="center",
        fontsize=10,  # 可根据需要调整字体大小
    )

# 保存图表
plt.tight_layout()
plot_file = "../AQI_Level_Days_Distribution.png"
plt.savefig(plot_file, dpi=300)
plt.close()
print(f"AQI 级别的柱状图已保存到: {plot_file}")
