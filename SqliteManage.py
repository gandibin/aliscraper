import sqlite3
import openai
import config
import traceback
import ast
import re

def get_new_brand(sub_row):
    openai.api_key = config.api_key
    openai.base_url = config.base_url
    openai.default_headers = {"x-foo": "true"}


    # Prepare prompt for OpenAI API
    prompt = f'''The following is company and product of  switch product data. Please find brand name from those data, Brand usually only one words. 
    please don't pick up brand by address. 
    when return data, and do not reponse anything else, just brand name.
    
        \n\n product title is : {sub_row[0]}
        company name is :{sub_row[1]}
        
        '''
    
    # Call the OpenAI API
    completion = openai.chat.completions.create(
        model="gpt-4o",  # You can use 'gpt-3.5-turbo' or 'gpt-4'
        messages=[
            {"role": "system", "content": "You are a data organization assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0
    )
    json_string = completion.choices[0].message.content
    return json_string

if __name__ == "__main__":
    db_path = "aliswitch.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "select id, sku_data, title from switch"
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        pid = row[0]
        title = row[2]

        data_dicts = ast.literal_eval(row[1])
        for data_dict in data_dicts:
            if 'product_name' in data_dict and data_dict['price']:
                sku = data_dict['product_name']
                price = data_dict['price']
                query2 = f"insert into switch_price(pid, title, sku, price) values({pid},'{title}','{sku}','{price}'); "
            elif '价格\n(元)' in data_dict and data_dict['价格\n(元)']:
                price = data_dict['价格\n(元)']
                del data_dict['价格\n(元)']
                sku = str( data_dict)
                query2 = f'insert into switch_price(pid, title, sku, price) values({pid},"{title}","{sku}","{price}"); '
            cursor.execute(query2)
            
        print("-----------------------------------------------------")
    
    conn.commit()
    conn.close()
    #     data_dict = data_dict[0]
    #     for key in data_dict:
    #         price =  data_dict[key]
    #         query2  = f"insert into switch_price(pid, title, sku, price) values({row[0]},'{row[2]}','{key}','{price}'); "
    #         cursor.execute(query2)
    # conn.commit()
        


    


    #把属性单元格里的内容单独形成一个表格
    # query = "select id, attributes from switch"
    # attributes_set = set()
    # cursor.execute(query)
    # rows = cursor.fetchall()
    # for row in rows:
    #     data_dict = ast.literal_eval(row[1])
    #     for key in data_dict:
    #         tag_key = re.sub(r'[^\w]', '_', key)
    #         if key:
    #             query2 =f"update switch_attributes set {tag_key} = '{data_dict[key]}' where pid = {row[0]};"
    #             try:
    #                 cursor.execute(query2)
    #                 conn.commit()
    #             except:
    #                 print(query2)
    #                 traceback.print_exc()





#根据数据的字段生成创建表的SQL语句
    # fields = attributes_set
    # # 清理字段名，将不符合SQL命名规则的字符替换
    # cleaned_fields = []
    # for field in fields:
    #     clean_field = re.sub(r'[^\w]', '_', field)  # 将非字母数字字符替换为下划线
    #     cleaned_fields.append(clean_field.lower())

    # # 生成 SQL 语句的字段部分
    # sql_fields = ',\n'.join([f"`{field}` TEXT" for field in cleaned_fields])

    # # 打印出创建表的SQL语句
    # sql_create_table = f"""
    # CREATE TABLE my_table (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     {sql_fields}
    # );
    # """

    # print(sql_create_table)



    #以下这部分代码是为了将aliswitch_sub 中品牌有问题的部分更新
    # query = "select pid from aliswitch_sub where Brand=''"
    # cursor.execute(query)
    # rows = cursor.fetchall()
    # for row in rows:
    #     query2 = f"select title, company_name from aliswitch where id = {row[0]}"
    #     cursor.execute(query2)
    #     sub_row = cursor.fetchone()
    #     new_brand = get_new_brand(sub_row)
    #     print(new_brand)
    #     query3 = f"update aliswitch_sub set Brand = '{new_brand}' where pid = {row[0]}"
    #     print(query3)
    #     cursor.execute(query3)
    #     conn.commit()
    # conn.close()





    #以下这部分代码是为了将aliswitch_sub表中的空值填充到aliswitch_sub_2表中
    #table_tag=["id","pid","Brand","Model","Communication_Mode","LACP","POE","QoS","SNMP","Stackable","VLAN","IP_routing","Switching_Capacity","speed"]
	# 获取列名
    # cursor.execute("PRAGMA table_info(aliswitch_sub)")
    # columns = cursor.fetchall()	


    # query = "select * from aliswitch_sub"
    # cursor.execute(query)
    # rows = cursor.fetchall()
    # for row in rows:
    #     for i in range(len(row)):
    #         if len(str(row[i]))<1:
    #             sub_2_query = f"select * from aliswitch_sub_2 where pid = {row[1]}"
    #             cursor.execute(sub_2_query)
    #             sub_2_row = cursor.fetchone()
    #             if sub_2_row[i] != "":
    #                 update_query = f"update aliswitch_sub set {columns[i][1]} = '{sub_2_row[i]}' where pid = {row[1]}"
    #             if sub_2_row[i] == "":
    #                 sub_1_query = f"select * from aliswitch_sub_1 where pid = {row[1]}"
    #                 cursor.execute(sub_1_query)
    #                 sub_1_row = cursor.fetchone()
    #                 if sub_1_row[i] != "":
    #                     update_query = f"update aliswitch_sub set {columns[i][1]} = '{sub_1_row[i]}' where pid = {row[1]}"
    #             if update_query:
    #                 print(f"i number is: {i}")
    #                 print(update_query)
    #                 cursor.execute(update_query)
    #                 conn.commit()

            