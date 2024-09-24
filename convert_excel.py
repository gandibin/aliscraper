import pandas as pd
import sqlite3

# 读取 Excel 文件
excel_file = 'switch_attributes.xlsx'  # 替换为你的 Excel 文件路径
sheet_name = 'sheet1'  # 替换为你要转换的工作表名称

df = pd.read_excel(excel_file, sheet_name=sheet_name)


# 检查是否有重复的列名
if df.columns.duplicated().any():
    duplicated_columns = df.columns[df.columns.duplicated()].unique()
    print(f"错误：Excel 表格中存在重复的列名: {duplicated_columns}")
else:
    try:
        # 连接到 SQLite 数据库（如果数据库不存在，会自动创建）
        conn = sqlite3.connect('aliswitch.db')  # 替换为你的 SQLite 数据库文件名
        cursor = conn.cursor()

        # 检查表是否存在
        table_name = 'switch_attribute_en'  # 替换为你的目标表名称
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        table_exists = cursor.fetchone()

        # 如果表不存在，则创建表并插入数据；如果存在，选择覆盖或跳过
        if not table_exists:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"表 '{table_name}' 不存在，已新建并插入数据。")
        else:
            # 表已存在的处理方式：覆盖、追加或跳过
            overwrite = input(f"表 '{table_name}' 已存在。是否要覆盖它？(y/n): ")
            if overwrite.lower() == 'y':
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"表 '{table_name}' 已存在，但已被覆盖并插入新数据。")
            else:
                print(f"表 '{table_name}' 已存在，操作被跳过。")

    except sqlite3.OperationalError as e:
        print(f"发生错误：{e}")
        print("可能的原因是数据库字段创建失败，请检查表格的列名是否有冲突或不合法。")

    finally:
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
