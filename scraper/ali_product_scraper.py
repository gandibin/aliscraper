import time
import os
import getpass
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import tkinter as tk
from urllib.parse import urlparse
import sqlite3
import traceback
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ProductScraper:
    def __init__(self):
        self.driver = None
        self.chrome_process =None
        self.chrome_process = None 
        self.driver = None
        #我能重新登录我自己的github 账号吗? 会不会冲突



    def safe_click(self, element):
        # 确保页面已完全加载
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # 确保元素可见并滚动到视图中
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

        # 1. 尝试普通点击
        try:
            element.click()
            print("普通点击成功")
            return
        except:
            print(f"普通点击失败")

        # 2. 尝试使用 JavaScript 点击
        try:
            self.driver.execute_script("arguments[0].click();", element)
            print("JavaScript 点击成功")
            return
        except:
            print(f"JavaScript 点击失败:")

        # 3. 尝试 ActionsChains 点击
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            print("ActionsChains 点击成功")
            return
        except:
            print("ActionsChains 点击失败:")

        # 4. 尝试发送 Enter 键进行点击
        try:
            element.send_keys(Keys.ENTER)
            print("发送 Enter 键点击成功")
            return
        except:
            print("发送 Enter 键点击失败:")

        # 5. 尝试点击父级元素
        try:
            parent_element = self.driver.find_element(By.XPATH, "..")
            parent_element.click()
            print("父级元素点击成功")
            return
        except:
            print("父级元素点击s失败:")

        # 6. 尝试完整的 JavaScript 鼠标事件点击
        try:
            self.driver.execute_script("""
                var event = new MouseEvent('click', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true
                });
                arguments[0].dispatchEvent(event);
            """, element)
            print("完整的 JavaScript 鼠标事件点击成功")
            return
        except:
            print(f"完整的 JavaScript 鼠标事件点击s失败:")

        print("所有点击方式均失败")

        

    def start_chrome_with_debugging(self):
        # 获取当前用户的用户名并构建Chrome的路径
        username = getpass.getuser()
        chrome_base_path = r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe"
        chrome_path = chrome_base_path.format(username)
    
        # 检查Chrome可执行文件是否存在
        if not os.path.exists(chrome_path):
            raise FileNotFoundError(f"未找到用户 {username} 的Chrome可执行文件，路径为 {chrome_path}")
        
        # 定义用户数据目录和远程调试端口
        user_data_dir = "C:/ChromeDevSession"
        remote_debugging_port = 9222
        
        # 启动带有远程调试功能的Chrome
        self.chrome_process = subprocess.Popen([
            chrome_path,
            f'--remote-debugging-port={remote_debugging_port}',
            f'--user-data-dir={user_data_dir}'
        ])
        
        # 给Chrome一些时间来启动
        start_time = time.time()
        max_wait_time = 4
        while self.chrome_process.poll() is None:
            if time.time() - start_time > max_wait_time:
                break
            time.sleep(0.5)
        
        # 设置Selenium连接到正在运行的调试模式下的Chrome实例
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{remote_debugging_port}"
        self.driver = webdriver.Chrome(options=options)
        

    def stop_chrome_debugging(self):
        if self.chrome_process is not None:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait()
                print("Chrome 调试进程已终止")
            except:
                print("终止 Chrome 调试进程s失败")
                

    def scroll_to_bottom(self):
        scroll_increment = "document.body.scrollHeight * 0.1"
        total_scroll_time = 10
        interval = 1
        for _ in range(int(total_scroll_time / interval)):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(interval)
        time.sleep(2)
        

    def wait_for_page_load_complete(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException:
            print("Page load timed out after waiting.")
                    



    #获取店铺的地址
    def get_shop_link(self):
        # 使用 Selenium 查找所有 class="primary-row-link" 的 a 标签
        links = self.driver.find_elements(By.CLASS_NAME, "primary-row-link") 
        # 使用集合来存储并去重域名
        domains = set()
        # 提取链接并获取域名部分
        for link in links:
            href = link.get_attribute('href')
            if href:
                parsed_url = urlparse(href)
                domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                domains.add(domain)
        return str(domains)  # 你可以根据需要返回或处理这个集合
            
    
    def get_product_details(self,cursor, url):
        retry = 0
        while True:  # 循环直到成功获取产品信息
            try:
                self.driver.get(url)
                time.sleep(3)
                self.wait_for_page_load_complete()
                self.driver.execute_script("window.scrollBy(0, 400);")

                # 产品标题
                title = str(self.driver.title)


                # 通过类名定位公司名称的元素并获取名称和链接
                company_element = self.driver.find_element(By.CLASS_NAME, 'company-name')

                # 获取公司名称
                company_name = company_element.text

                # store_links
                shop_link = company_element.find_element(By.TAG_NAME, 'a').get_attribute('href')

                # 产品的SKU价格信息
                sku_data = self.sku_details(url)

                attributes = self.get_product_attributes()
                print(f"title: ---- {title}")
                print(f"company_name ---- {company_name}")
                print(f"shop_link ---- {shop_link}")
                print(f"sku_data ----{sku_data}")
                print(f"attributes ----{attributes}")
                print("----------------------------------")

                update_query = f"""
                UPDATE aliswitch
                SET 
                    title = ?,
                    company_name = ?,
                    shop_link = ?,
                    sku_data = ?,
                    attributes = ?,
                    check_status = 1
                WHERE product_link = ?;
                """
                
                # 执行更新操作
                cursor.execute(update_query, (title,company_name,shop_link,sku_data,attributes,url))
                break  # 成功获取信息后跳出循环

            except:
                
                traceback.print_exc()
                
                # 在异常处理块中展开提示逻辑
                root = tk.Tk()
                root.title("操作提示")  # 设置窗口标题
                
                # 创建一个标签，提示用户手动操作
                label = tk.Label(root, text="检测到验证码，请手动解决问题后点击确定继续。")
                label.pack(padx=20, pady=20)

                # 创建倒计时标签
                countdown_label = tk.Label(root, text="剩余时间: 10秒")
                countdown_label.pack(padx=20, pady=10)
                
                # 标记用户的选择
                user_choice = tk.StringVar(value="repeat")  # 初始值为 "repeat"
            
                def on_repeat():
                    user_choice.set("repeat")
                    root.quit()
            
                def on_skip():
                    user_choice.set("skip")
                    root.quit()
            
                # 创建 "重复" 按钮
                repeat_button = tk.Button(root, text="重复", command=on_repeat)
                repeat_button.pack(side="left", padx=10, pady=10)
            
                # 创建 "跳过" 按钮
                skip_button = tk.Button(root, text="跳过", command=on_skip)
                skip_button.pack(side="right", padx=10, pady=10)
                # 设定10秒定时器，10秒后默认跳过
                def auto_skip():
                    user_choice.set("skip")
                    root.quit()

                root.after(10000, auto_skip)  # 10秒（10000毫秒）后执行 auto_skip
            
                # 进入事件循环，等待用户点击“重复”或“跳过”
                root.mainloop()
            
                # 根据用户选择执行不同的操作
                if user_choice.get() == "repeat":
                    # 当用户点击按钮后，销毁窗口
                    root.destroy()
                else:
                    # 当用户点击按钮后，销毁窗口
                    root.destroy()
                    update_query = f"""
                    UPDATE aliswitch
                    SET 
                        check_status = 2
                    WHERE product_link = ?;
                    """
                    
                    # 执行更新操作
                    cursor.execute(update_query, (url,))
                    break  # 用户选择跳过，跳出循环
                                      
    
    #获取产品的SKU价格
    def sku_details(self, url): 
        sku_data = []
        try:
            sku_element = self.driver.find_element(By.CLASS_NAME, 'product-price')
        except:
            pass

        if sku_element:
            sku_items = sku_element.find_elements(By.CLASS_NAME, 'price-item')
            row_dict  = {}
            for sku_item in sku_items:
                price = sku_item.find_element(By.CLASS_NAME,"price").text.strip()
                quality = sku_item.find_element(By.CLASS_NAME,"quality").text.strip()
                row_dict[quality] = price
            #设置了最低起订量的sku
            try:
                price_range = sku_element.find_element(By.CLASS_NAME,"price-range")
                if price_range:
                    price = price_range.find_element(By.CLASS_NAME,"price").text.strip()
                    min_moq =  price_range.find_element(By.CLASS_NAME,"min-moq").text.strip()
                    row_dict[min_moq] = price
            except:
                pass

            #设置促销价格的sku
            try:
                promotion_price = sku_element.find_element(By.CLASS_NAME,"promotion-price")
                if promotion_price:
                    price = promotion_price.find_element(By.CLASS_NAME,"normal").text.strip()
                    min_moq =  promotion_price.find_element(By.CLASS_NAME,"min-moq").text.strip()
                    row_dict[min_moq] = price
            except:
                pass

            #第二种设置促销价格的sku
            try:
                price_range = sku_element.find_element(By.CLASS_NAME,"price-range")
                promotion_element = sku_element.find_element(By.CLASS_NAME,"promotion")
                if promotion_element:
                    price = price_range.find_element(By.CLASS_NAME,"promotion").text.strip()
                    min_moq =  price_range.find_element(By.CLASS_NAME,"min-moq").text.strip()
                    row_dict[min_moq] = price
            except:
                pass

            #第三种设置促销价格的sku
            try:
                product_activity_element = sku_element.find_element(By.CLASS_NAME,"product-activity")
                if product_activity_element:
                    price = self.driver.find_element(By.CLASS_NAME,"promotion-price").text.strip()
                    promotion_moq = self.driver.find_element(By.CLASS_NAME,"promotion-moq").text.strip()
                    row_dict[promotion_moq] = price

            except:
                traceback.print_exc()
            sku_data.append(row_dict)

        return str(sku_data)

     

    
    def get_product_attributes(self):
        # 初始化一个空字典来存储属性
        product_attributes = {}

        try:
            # 最大尝试点击次数，防止无限循环
            max_clicks = 5
            click_count = 0

            while click_count < max_clicks:
                try:
                    # 查找 more_bg_element 元素
                    more_bg_element = self.driver.find_element(By.CSS_SELECTOR, ".more-bg a")
                    
                    #滚动页面到 more_元素
                    element_position = self.driver.execute_script("return arguments[0].getBoundingClientRect().top;", more_bg_element)
                    window_height = self.driver.execute_script("return window.innerHeight;")
                    scroll_position = element_position - (window_height / 2)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_position});")
                    
                    # 确保元素可见并且没有被其他元素遮挡
                    if more_bg_element.is_displayed():
                        self.safe_click(more_bg_element)
                        # 增加点击计数
                        click_count += 1

                        # 再次检查 more_bg_element 是否仍然存在
                        try:
                            more_bg_element = self.driver.find_element(By.CSS_SELECTOR, ".more-bg a")
                            print(f"more-bg 元素仍然存在，进行第 {click_count} 次点击")
                        except:
                            # 如果找不到元素，说明点击成功，跳出循环
                            print("元素已经消失，点击成功")
                            break
                    else:
                        print("元素不可见，无法点击")
                        break

                except:
                    # 如果找不到 more-bg 元素，跳出循环
                    print("找不到 more-bg 元素，可能已经消失")
                    traceback.print_exc()
                    break

        except:
            traceback.print_exc()

        

        attribute_info = self.driver.find_element(By.CLASS_NAME,'module_attribute')
        attribute_lists = attribute_info.find_elements(By.CLASS_NAME,"attribute-list")
        for attribute_list in attribute_lists:
            attribute_item_elements = attribute_list.find_elements(By.CLASS_NAME,"attribute-item")
            for attr_item in attribute_item_elements:
                name_element = attr_item.find_element(By.CLASS_NAME,"left")
                value_element = attr_item.find_element(By.CLASS_NAME,"right")
                # 获取属性名和值的文本
                attr_name = name_element.text.strip()
                attr_value = value_element.text.strip()
                # 将属性名和值存入字典
                product_attributes[attr_name] = attr_value
        
        
        return str(product_attributes)




if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(current_dir)
    db_path = os.path.join(root_dir, "aliswitch.db")  # Database file path
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 执行查询，提取 check = 0 的所有 url
    cursor.execute("SELECT product_link FROM aliswitch WHERE check_status = 0;")
    urls = cursor.fetchall()
    #urls = [["https://www.alibaba.com/product-detail/C9200L-48P-4X-A-Network-Switches_1600911697472.html"]]
       
    
    scraper = ProductScraper()
    scraper.start_chrome_with_debugging()
    for url in urls:
        print(url[0])
        scraper.get_product_details(cursor,url[0])
        conn.commit()
    print("All URLs checked, waiting 10 seconds before closing the browser...")
    time.sleep(10)
    #scraper.stop_chrome_debugging()
    conn.close()
    
