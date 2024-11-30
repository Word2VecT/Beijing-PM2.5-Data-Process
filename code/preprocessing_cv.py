import pandas as pd
import numpy as np

# 读取 CSV 文件
input_file = "../BeijingPM20100101_20151231.csv"
output_file = "../BeijingPM20100101_20151231_processed_cv.csv"

try:
    df = pd.read_csv(input_file)
    print(f"成功读取文件: {input_file}")
except FileNotFoundError:
    print(f"文件未找到: {input_file}")
    exit(1)

# 检查 'cbwd' 列是否存在
if "cbwd" not in df.columns:
    print("错误: 列 'cbwd' 不存在于数据中。")
    exit(1)

# 识别 'cbwd' 列中值为 'cv' 的单元格
cv_mask = df["cbwd"] == "cv"
num_cv = cv_mask.sum()
print(f"列 'cbwd' 中发现 {num_cv} 个值为 'cv' 的单元格。")

if num_cv == 0:
    print("没有需要替换的 'cv' 值。")
else:
    # 使用后项数据填充 'cv' 值
    # 首先，使用后项（下一个有效值）进行填充
    df["cbwd"] = df["cbwd"].replace("cv", np.nan)
    df["cbwd"] = df["cbwd"].bfill()

    # 再次识别哪些 'cv' 值未被填充（例如，'cv' 在最后一行）
    remaining_cv = df["cbwd"] == "cv"
    num_remaining_cv = remaining_cv.sum()
    if num_remaining_cv > 0:
        print(
            f"警告: 仍有 {num_remaining_cv} 个 'cv' 值未被替换（可能位于数据末尾）。这些值将保留为 'cv' 或可根据需要进一步处理。"
        )
    else:
        print("所有 'cv' 值已成功替换。")

# 将处理后的数据保存到新的 CSV 文件
df.to_csv(output_file, index=False)
print(f"处理后的数据已保存到: {output_file}")
