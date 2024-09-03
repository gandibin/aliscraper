import json


import sqlite3
import json

# 连接到 SQLite 数据库
conn = sqlite3.connect('aliswitch.db')
cursor = conn.cursor()

# 读取文件内容
with open('product_search.json', 'r', encoding='utf-8') as file:
    content = file.read()
    data = json.loads(content)

# 遍历字典列表
for entry in data:
    keyword = entry.get('keyword')
    contents = entry.get('content', [])
    
    for url_list in contents:
        if isinstance(url_list, list):
            for url in url_list:
                if url:  # 检查 URL 是否为空
                    try:
                        cursor.execute(
                            'INSERT OR IGNORE INTO aliswitch (keyword, url) VALUES (?, ?)',
                            (keyword, url)
                        )
                    except sqlite3.IntegrityError:
                        print(f"URL already exists in the database: {url}")

# 提交事务并关闭连接
conn.commit()
conn.close()



# # File path to your input text file
# input_file = 'E:/eclipse-workspace/Aliscraper/product_search.txt'
# # File path for the output JSON file
# output_file = 'E:/eclipse-workspace/Aliscraper/product_search.json'
#
# def convert_to_json(input_file, output_file):
#     try:
#         with open(input_file, 'r', encoding='utf-8') as file:
#             # Initialize an empty list to hold all the URL arrays
#             content_list = []
#
#             # Read through each line
#             for line in file:
#                 # Clean the line and ensure it uses double quotes and valid JSON format
#                 clean_line = line.strip().replace("'", '"')
#
#                 # Check if the line starts with "[" and ends with "]" indicating it's an array
#                 if clean_line.startswith('[') and clean_line.endswith(']'):
#                     # Convert the string to a list (JSON array)
#                     try:
#                         url_list = json.loads(clean_line)
#                         content_list.append(url_list)
#                     except json.JSONDecodeError as e:
#                         print(f"Error decoding JSON on this line: {clean_line}")
#                         print(f"Error: {e}")
#                         continue
#
#             # Construct the final JSON structure
#             final_data = {
#                 "keyword": "network+switch",
#                 "content": content_list
#             }
#
#             # Write the final JSON data to the output file
#             with open(output_file, 'w', encoding='utf-8') as json_file:
#                 json.dump(final_data, json_file, indent=4, ensure_ascii=False)
#
#             print(f"Data successfully converted to JSON and saved to {output_file}")
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
# # Call the function to convert and save the JSON
# convert_to_json(input_file, output_file)
