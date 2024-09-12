import json
import openai
import sqlite3
import os

class SwitchDataFormatter:
    def __init__(self, db_path, api_key, base_url="https://reverse.onechats.top/v1/"):
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
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Retrieve switch data
        cursor.execute("SELECT id,attributes FROM aliswitch where check_status =1 Limit 10")  # Assuming 'switches' is your table name
        switch_data = cursor.fetchall()
        
        conn.close()
        return switch_data

    def format_switch_data(self, switch_data):
        # Prepare prompt for OpenAI API
        prompt = f"The following are some switch product data. Please help me organize them into structured information with brand, Communication Mode, Switch Capacity,Ports_quantity, LACP, POE, QoS, SNMP, Stackable, VLAN, tTransmission Rate, model . Output the data in JSON format.\n\n{switch_data[1]}"
        
        # Call the OpenAI API
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # You can use 'gpt-3.5-turbo' or 'gpt-4'
            messages=[
                {"role": "system", "content": "You are a data organization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        return completion.choices[0].message.content

    def update_switch_data_in_db(self, formatted_data):
        # Connect to SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parse the JSON formatted data
        data = json.loads(formatted_data)
        
        # Iterate through the data and update the database
        for item in data:
            brand = item.get("brand")
            speed = item.get("speed")
            model = item.get("model")
            price = item.get("price")
            
            # Update the corresponding switch data in the database (modify query as per your schema)
            cursor.execute("""
                UPDATE switches
                SET brand = ?, speed = ?, price = ?
                WHERE model = ?
            """, (brand, speed, price, model))
        
        conn.commit()
        conn.close()
        

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    db_path = os.path.join(current_dir, "aliswitch.db")  # Database file path
    print(db_path)
    api_key = "sk-hXXlRUJFk0sjkcrYE6A00a37Be3a4c5aA1D592288a790eD8"

    formatter = SwitchDataFormatter(db_path, api_key)
    switch_datas = formatter.get_switch_data_from_db()  # Retrieve data from SQLite
    for switch_data in switch_datas:

        formatted_data = formatter.format_switch_data(switch_data)  # Format data using OpenAI
        print(formatted_data)
        #formatter.update_switch_data_in_db(formatted_data)  # Update the database with formatted data
