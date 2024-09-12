import json
import openai

def format_switch_data(switch_data):
    openai.api_key = "sk-hXXlRUJFk0sjkcrYE6A00a37Be3a4c5aA1D592288a790eD8"
    prompt = f"The following are some switch product data. Please help me organize them into structured information with brand, speed, model, and price. Output the data in JSON format.\n\n{switch_data}"
    openai.base_url = "https://reverse.onechats.top/v1/"
    openai.default_headers = {"x-foo": "true"}

    completion = openai.chat.completions.create(
        model="gpt-4",  # You can use 'gpt-3.5-turbo' or 'gpt-4'
        messages=[
            {"role": "system", "content": "You are a data organization assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0
    )
    return completion.choices[0].message.content



# Example messy switch data
switch_data = """
Brand: Huawei, Speed: 10Gbps, Model: S5720-28X-LI, Price: 4500 yuan
Brand: Cisco, Speed: 1Gbps, Model: C9200L-24P-4G-E, Price: 6500 yuan
Brand: TP-Link, Speed: 100Mbps, Model: TL-SG105E, Price: 200 yuan
"""

# Call the function to organize the data and return JSON output
formatted_data = format_switch_data(switch_data)

# Convert the JSON string response to a Python dictionary for easier manipulation
try:
    json_data = json.loads(formatted_data)
    print(json.dumps(json_data, indent=4))  # Pretty print the JSON data
except json.JSONDecodeError:
    print("Failed to parse JSON. The response was:")
    print(formatted_data)

dfd
