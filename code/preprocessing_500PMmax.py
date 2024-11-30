import pandas as pd

# 读取 CSV 文件
input_file = "../BeijingPM20100101_20151231.csv"
output_file = "../BeijingPM20100101_20151231_processed_500PMmax.csv"

try:
    df = pd.read_csv(input_file)
    print(f"成功读取文件: {input_file}")
except FileNotFoundError:
    print(f"文件未找到: {input_file}")
    exit(1)

# 需要处理的 PM 列
pm_columns = ["PM_Dongsi", "PM_Dongsihuan", "PM_Nongzhanguan"]
pm_max = 500

# 将 PM 列转换为数值类型，非数值将被设置为 NaN
for col in pm_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        print(f"警告: 列 '{col}' 不存在于数据中。")

# 线性插值，填补缺失值
df[pm_columns] = df[pm_columns].interpolate(method="linear", limit_direction="both")

# 处理 PM 列的异常值（最大值为 500）
for col in pm_columns:
    if col not in df.columns:
        continue

    # 识别超过 500 的值
    outliers = df[col] > pm_max
    num_outliers = outliers.sum()
    print(f"列 '{col}': 发现 {num_outliers} 个超过 {pm_max} 的异常值。")

    # 替换超过 500 的值为 500
    df.loc[outliers, col] = pm_max

# 将处理后的数据保存到新的 CSV 文件
df.to_csv(output_file, index=False)
print(f"处理后的数据已保存到: {output_file}")
