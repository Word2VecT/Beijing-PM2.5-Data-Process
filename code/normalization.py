import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 读取 CSV 文件
input_file = "../BeijingPM20100101_20151231.csv"


try:
    df = pd.read_csv(input_file)
    print(f"成功读取文件: {input_file}")
except FileNotFoundError:
    print(f"文件未找到: {input_file}")
    exit(1)

# 检查 'DEWP' 和 'TEMP' 列是否存在
required_columns = ["DEWP", "TEMP"]
for col in required_columns:
    if col not in df.columns:
        print(f"错误: 列 '{col}' 不存在于数据中。")
        exit(1)

# 将 'DEWP' 和 'TEMP' 列转换为数值类型，非数值将被设置为 NaN
for col in required_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 线性插值，填补缺失值
df[required_columns] = df[required_columns].interpolate(method="linear", limit_direction="both")

# 检查是否仍有缺失值
if df[required_columns].isnull().any().any():
    print("警告: 存在无法通过插值填补的缺失值。考虑使用其他填补方法或删除这些数据点。")
    # 可以选择删除这些行
    df.dropna(subset=required_columns, inplace=True)


# 0-1 归一化（Min-Max 归一化）
def min_max_normalize(series):
    return (series - series.min()) / (series.max() - series.min())


df_minmax = df.copy()
df_minmax["DEWP_MinMax"] = min_max_normalize(df_minmax["DEWP"])
df_minmax["TEMP_MinMax"] = min_max_normalize(df_minmax["TEMP"])


# Z-Score 归一化（标准化）
def z_score_normalize(series):
    return (series - series.mean()) / series.std()


df_zscore = df.copy()
df_zscore["DEWP_ZScore"] = z_score_normalize(df_zscore["DEWP"])
df_zscore["TEMP_ZScore"] = z_score_normalize(df_zscore["TEMP"])

output_dir = "../"

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 1. 散点图：0-1 归一化后的 DEWP 和 TEMP
plt.figure(figsize=(10, 6))
plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 黑体
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
sns.scatterplot(x="DEWP_MinMax", y="TEMP_MinMax", data=df_minmax, alpha=0.5)
plt.title("DEWP 和 TEMP 的 0-1 归一化散点图")
plt.xlabel("DEWP (0-1 归一化)")
plt.ylabel("TEMP (0-1 归一化)")
plt.tight_layout()
plot_minmax_path = os.path.join(output_dir, "DEWP_TEMP_MinMax_Normalized_Scatter.png")
plt.savefig(plot_minmax_path, dpi=300)
plt.close()
print(f"0-1 归一化的散点图已保存到: {plot_minmax_path}")

# 2. 散点图：Z-Score 归一化后的 DEWP 和 TEMP
plt.figure(figsize=(10, 6))
sns.scatterplot(x="DEWP_ZScore", y="TEMP_ZScore", data=df_zscore, alpha=0.5, color="orange")
plt.title("DEWP 和 TEMP 的 Z-Score 归一化散点图")
plt.xlabel("DEWP (Z-Score 归一化)")
plt.ylabel("TEMP (Z-Score 归一化)")
plt.tight_layout()
plot_zscore_path = os.path.join(output_dir, "DEWP_TEMP_ZScore_Normalized_Scatter.png")
plt.savefig(plot_zscore_path, dpi=300)
plt.close()
print(f"Z-Score 归一化的散点图已保存到: {plot_zscore_path}")

# 可选：将归一化后的数据保存到新的 CSV 文件
# 合并归一化后的列到原始 DataFrame
df_combined = pd.concat(
    [df, df_minmax[["DEWP_MinMax", "TEMP_MinMax"]], df_zscore[["DEWP_ZScore", "TEMP_ZScore"]]], axis=1
)
df_combined.to_csv("../BeijingPM20100101_20151231_DEWP_TEMP_Normalized.csv", index=False)
print("归一化后的数据已保存到: BeijingPM20100101_20151231_DEWP_TEMP_Normalized.csv")
