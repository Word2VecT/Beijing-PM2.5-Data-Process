import pandas as pd

# 读取 CSV 文件
input_file = "../BeijingPM20100101_20151231.csv"
output_file = "../BeijingPM20100101_20151231_processed_3SD.csv"

try:
    df = pd.read_csv(input_file)
    print(f"成功读取文件: {input_file}")
except FileNotFoundError:
    print(f"文件未找到: {input_file}")
    exit(1)

# 需要处理的列
columns_to_process = ["HUMI", "PRES", "TEMP"]

for col in columns_to_process:
    if col not in df.columns:
        print(f"警告: 列 '{col}' 不存在于数据中。跳过此列。")
        continue

    # 将列转换为数值类型，非数值将被设置为 NaN
    df[col] = pd.to_numeric(df[col], errors="coerce")

    # 线性插值，填补缺失值
    df[col] = df[col].interpolate(method="linear", limit_direction="both")

    # 计算均值和标准差
    mean = df[col].mean()
    std = df[col].std()

    # 定义阈值
    upper_limit = mean + 3 * std
    lower_limit = mean - 3 * std

    # 识别异常值
    outliers_upper = df[col] > upper_limit
    outliers_lower = df[col] < lower_limit

    num_outliers = outliers_upper.sum() + outliers_lower.sum()
    print(f"列 '{col}': 发现 {num_outliers} 个异常值。")

    # 替换异常值为阈值
    df.loc[outliers_upper, col] = upper_limit
    df.loc[outliers_lower, col] = lower_limit

# 将处理后的数据保存到新的 CSV 文件
df.to_csv(output_file, index=False)
print(f"处理后的数据已保存到: {output_file}")
