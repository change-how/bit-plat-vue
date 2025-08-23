import pandas as pd

# 读取测试CSV文件
csv_path = 'test_header_search.csv'
print('=== 测试CSV标题查找功能 ===')
print(f'读取文件: {csv_path}')

# 读取原始CSV
raw_csv = pd.read_csv(csv_path, header=None)
print(f'CSV文件形状: {raw_csv.shape}')
print('\n前15行内容:')
for i in range(min(15, len(raw_csv))):
    row_content = [str(x) if pd.notna(x) else 'NaN' for x in raw_csv.iloc[i]]
    print(f'第{i+1}行: {row_content}')

print('\n=== 查找"交易记录"标题 ===')
target_aliases = ['交易记录', 'Transaction Records', '交易明细', '转账记录']

found_positions = []
for row_idx, row in raw_csv.iterrows():
    for col_idx, cell_value in enumerate(row):
        if pd.notna(cell_value):
            cell_str = str(cell_value).strip()
            for alias in target_aliases:
                if alias in cell_str:
                    found_positions.append((row_idx, col_idx, cell_str))
                    print(f'✅ 找到匹配: 第{row_idx+1}行, 第{col_idx+1}列, 内容="{cell_str}"')
                    
                    # 检查下一行是否是表头
                    if row_idx + 1 < len(raw_csv):
                        header_row = raw_csv.iloc[row_idx + 1]
                        header_content = [str(x) if pd.notna(x) else 'NaN' for x in header_row]
                        print(f'   下一行(应为表头): {header_content}')
                        
                        # 检查数据行
                        if row_idx + 2 < len(raw_csv):
                            data_start = row_idx + 2
                            print(f'   数据从第{data_start+1}行开始')
                            for data_row_idx in range(data_start, min(data_start + 3, len(raw_csv))):
                                data_row = raw_csv.iloc[data_row_idx]
                                data_content = [str(x) if pd.notna(x) else 'NaN' for x in data_row]
                                print(f'     第{data_row_idx+1}行数据: {data_content}')
                    break

print('\n=== 查找"设备登录记录"标题 ===')
login_aliases = ['设备登录记录', 'Device Login Records', '登录日志', '访问记录']

for row_idx, row in raw_csv.iterrows():
    for col_idx, cell_value in enumerate(row):
        if pd.notna(cell_value):
            cell_str = str(cell_value).strip()
            for alias in login_aliases:
                if alias in cell_str:
                    print(f'✅ 找到匹配: 第{row_idx+1}行, 第{col_idx+1}列, 内容="{cell_str}"')
                    
                    # 检查后续行
                    for offset in range(1, 4):
                        if row_idx + offset < len(raw_csv):
                            next_row = raw_csv.iloc[row_idx + offset]
                            next_content = [str(x) if pd.notna(x) else 'NaN' for x in next_row]
                            print(f'   第{row_idx+offset+1}行: {next_content}')
                    break

print('\n测试完成')
