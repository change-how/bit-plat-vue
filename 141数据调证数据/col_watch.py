import pandas as pd

def get_excel_sheet_and_column_info(file_path):
    """
    读取Excel文件，并打印每个工作表及其所有列的层级关系。

    参数:
    file_path (str): Excel文件的完整路径。
    """
    try:
        # 使用pandas的ExcelFile类来读取整个Excel文件
        excel_file = pd.ExcelFile(file_path)

        # 获取所有工作表的名称
        sheet_names = excel_file.sheet_names
        print(f"成功读取文件: {file_path}")
        print("----------------------------------------")
        print(f"该Excel文件包含 {len(sheet_names)} 个工作表。")
        print("----------------------------------------")

        # 遍历每个工作表
        for sheet_name in sheet_names:
            print(f"工作表: '{sheet_name}'")

            # 读取当前工作表的数据，只取第一行（列名）
            # header=0 表示第一行作为列名
            df = excel_file.parse(sheet_name, header=1)

            # 获取并打印所有列的名称
            column_names = df.columns.tolist()
            print("  - 列名:", column_names)
            print("-" * 40)

    except FileNotFoundError:
        print(f"错误：文件未找到。请检查路径是否正确: {file_path}")
    except Exception as e:
        print(f"发生错误: {e}")

# --- 如何使用 ---
# 将下面的 'your_excel_file.xlsx' 替换为您自己的文件路径
# 如果文件在当前目录下，可以直接写文件名，例如: 'data.xlsx'
# 如果文件在其他位置，需要提供完整路径，例如: 'C:/Users/YourName/Documents/data.xlsx'

excel_file_path = './141数据调证数据/Bitpie/Bitpie数据.xlsx'
get_excel_sheet_and_column_info(excel_file_path)