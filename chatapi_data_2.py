import json
import openai
import sqlite3
import os
import traceback
import ast
import config



class SwitchDataFormatter:
    def __init__(self, db_path, api_key, base_url):
        self.db_path = db_path
        self.api_key = api_key
        self.base_url = base_url
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        openai.default_headers = {"x-foo": "true"}
        
    def get_switch_data_from_db(self):
        # Connect to SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Query to retrieve all table names

        # Retrieve switch data
        cursor.execute("SELECT id,attributes FROM aliswitch where check_status =4;")  # Assuming 'switches' is your table name
        switch_data = cursor.fetchall()
        
        conn.close()
        return switch_data

    def format_switch_data(self, switch_data):
        # Prepare prompt for OpenAI API
        prompt = f'''The following are some switch product data. Please help me organize them into structured information with
        Output the data in JSON format.  We only  need the following key in json.
        BrandName, ModelNumber,Ports,Communication_Mode, LACP, POE, QoS, SNMP, Stackable, VLAN_Support, IP_routing,Switching_Capacity,speed. 
         please do not change key name as above when return data, and do not reponse anything else, just json data.
         \n\n{switch_data[1]}'''
        
        # Call the OpenAI API
        completion = openai.chat.completions.create(
            model="gpt-4",  # You can use 'gpt-3.5-turbo' or 'gpt-4'
            messages=[
                {"role": "system", "content": "You are a data organization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        json_string = completion.choices[0].message.content
        # 要替换的字符列表
        to_replace = ["'''json", "'''", "```json", "```", "\n"]

        # 循环替换
        cleaned_json_string = json_string
        for item in to_replace:
            cleaned_json_string = cleaned_json_string.replace(item, "")
        # Convert the cleaned JSON string to a Python dictionary
        try:        
            dict_data = json.loads(cleaned_json_string)
        except:
            try:
                # 使用 ast.literal_eval 将其转换为 Python 字典
                dict_data = ast.literal_eval(cleaned_json_string)
            except:
                print(json_string)
                dict_data = {}
                traceback.print_exc()

        # 如果返回的是列表，取第一个元素        
        if isinstance(dict_data,list):
            if dict_data:
                dict_data = dict_data[0]
            else:
                dict_data = dict(dict_data)
        
        
        # 需要检查的标准键
        required_keys = ['BrandName', 'ModelNumber', 'Ports', 'Communication_Mode', 'LACP', 'POE', 'QoS', 'SNMP', 'Stackable', 'VLAN_Support', 'IP_routing', 'Switching_Capacity', 'speed']
        # 检查并生成缺失的键
        try:
            for key in required_keys:
                if key not in dict_data:
                    dict_data[key] = ""  # 为缺失的键赋空值
        except:
            print(f"data type is ---- {dict_data}")
        
        return dict_data

    def update_switch_data_in_db(self, formatted_data,pid):
        # Connect to SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f'''INSERT INTO aliswitch_sub_3 (
                        pid,
                        Brand, 
                        Model, 
                        Communication_Mode, 
                        Ports_quantity, 
                        LACP, 
                        POE, 
                        QoS, 
                        SNMP, 
                        Stackable, 
                        VLAN, 
                        Switching_Capacity, 
                        IP_routing, 
                        speed
                    ) VALUES (
                        "{pid}",
                        "{formatted_data['BrandName']}", 
                        "{formatted_data['ModelNumber']}", 
                        "{formatted_data['Communication_Mode']}", 
                        "{formatted_data['Ports']}", 
                        "{formatted_data['LACP']}", 
                        "{formatted_data['POE']}", 
                        "{formatted_data['QoS']}", 
                        "{formatted_data['SNMP']}", 
                        "{formatted_data['Stackable']}", 
                        "{formatted_data['VLAN_Support']}", 
                        "{formatted_data['Switching_Capacity']}", 
                        "{formatted_data['IP_routing']}", 
                        "{formatted_data['speed']}"
                    );
        '''
        query2= f"update aliswitch set check_status = 5 where id = {pid}"
        try:
            cursor.execute(query)
            cursor.execute(query2)#更新状态为3,表示已经经过第一次的openai 3.5 处理, 4为已经过chapgpt 4o第二次处理,5 为4 处理完成第三次
            conn.commit()
            conn.close()
        except:
            print(query)
            traceback.print_exc()

        

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    db_path = os.path.join(current_dir, "aliswitch.db")  # Database file path
    api_key = config.api_key
    base_url= config.base_url
    formatter = SwitchDataFormatter(db_path, api_key)
    switch_datas = formatter.get_switch_data_from_db()  # Retrieve data from SQLite
    for switch_data in switch_datas:
        try:
            print("------------------------------------------------------------------------------------------------------------------------------------------------------")
            formatted_data = formatter.format_switch_data(switch_data)  # Format data using OpenAI
            print(f"type of data is : {type(formatted_data)}")
            if isinstance(formatted_data, list):
                print(formatted_data)
            formatter.update_switch_data_in_db(formatted_data,switch_data[0])  # Update the database with formatted data
        except:
            traceback.print_exc()
