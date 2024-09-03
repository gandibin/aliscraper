import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import getpass
import os
import sqlite3

class SearchScraper:
    def __init__(self):
        self.username = getpass.getuser()
        self.chrome_base_path = r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe"
        self.user_data_dir = "C:/ChromeDevSession"
        self.chrome_path = self.chrome_base_path.format(self.username)
    
        # 检查Chrome可执行文件是否存在
        if not os.path.exists(self.chrome_path):
            raise FileNotFoundError(f"未找到用户 {self.username} 的Chrome可执行文件，路径为 {self.chrome_path}")
        self.remote_debugging_port = 9222
        self.driver = None

    def start_chrome_with_debugging(self):
        self.chrome_process = subprocess.Popen([
            self.chrome_path,
            f'--remote-debugging-port={self.remote_debugging_port}',
            f'--user-data-dir={self.user_data_dir}'
        ])

        max_wait_time = 4  # 最大等待时间 4 秒
        start_time = time.time()
        
        while self.chrome_process.poll() is None:
            if time.time() - start_time > max_wait_time:
                print("Chrome 启动超时")
                break
            time.sleep(0.5)  # 每 0.5 秒检查一次

        print("Chrome 已启动")

    def stop_chrome_debugging(self):
        if self.chrome_process is not None:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait()
                print("Chrome 调试进程已终止")
            except Exception as e:
                print(f"终止 Chrome 调试进程失败: {e}")
        else:
            print("没有正在运行的 Chrome 调试进程")

    def generate_search_url(self, keyword):
        base_url = "https://www.alibaba.com/trade/search?spm=a2700.product_home_l0.home_login_first_screen_fy23_pc_search_bar.keydown__Enter&tab=all&SearchText="
        encoded_keyword = keyword.replace(" ", "+")
        search_url = f"{base_url}{encoded_keyword}"
        return search_url

    def scroll_to_bottom(self):
        scroll_increment = "document.body.scrollHeight * 0.1"
        total_scroll_time = 10  # 总滚动时间10秒
        interval = 1  # 每0.6秒滚动一次
        
        for _ in range(int(total_scroll_time / interval)):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(interval)
        time.sleep(2)
        
        
    def get_urls(self,product_page,urls):
        #打开新的页面
        self.driver.get(product_page)
        # 滚动到页面底部
        self.scroll_to_bottom()
        # 获取 div data-content="abox-ProductNormalList 西面的
        productNormalList = self.driver.find_element(By.CSS_SELECTOR, 'div[data-content="abox-ProductNormalList"]')
        links = productNormalList.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            url = link.get_attribute("href")
            if url and url.startswith("https://www.alibaba.com"):
                print(url)                
                urls.add(url)
        return urls

    def search_keyword(self, keyword):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{self.remote_debugging_port}"
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.alibba.com")
        url = self.generate_search_url(keyword)
        self.driver.get(url)
        
        print(f"已导航至: {url}")
        
        # 滚动到页面底部
        self.scroll_to_bottom()

        # data-content="abox-ProductNormalList
        productNormalList = self.driver.find_element(By.CSS_SELECTOR, 'div[data-content="abox-ProductNormalList"]')
        links = productNormalList.find_elements(By.TAG_NAME, "a")
        
        # 获取以 https://www.alibaba.com 开头的链接
        urls =set()
        for link in links:
            url = link.get_attribute("href")
            if url and url.startswith("https://www.alibaba.com"):
                print(url) 
                urls.add(url)      
        
        # 查找包含 class 为 'searchx-pagination-list' 的 div 元素
        div_element = self.driver.find_element(By.CSS_SELECTOR, 'div.searchx-pagination-list')
        
        # 在该 div 元素内查找所有的 a 链接
        a_elements = div_element.find_elements(By.TAG_NAME, 'a')
        
        # 排除第一个 a 链接，获取其余的 href 属性值
        links = [a.get_attribute('href') for a in a_elements[1:]]   
        for link in links:
            time.sleep(5)
            urls =self.get_urls(link,urls)
     
        return  urls
        

    def execute_search(self, keyword):
        
        conn = sqlite3.connect('aliswitch.db')
        cursor = conn.cursor()
        self.start_chrome_with_debugging()
        urls = self.search_keyword(keyword)
        return urls
            
if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(current_dir)
    db_file = os.path.join(root_dir,"aliswitch.db")
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    keyword_list =['network switch','poe network switch','managed network switch',' business network switches','enterprise network switch']
    SearchScraper =SearchScraper()
    for keyword in keyword_list:
        urls = SearchScraper.execute_search(keyword)
        print("data ready, start to insert")
        insert_query = "INSERT OR IGNORE INTO aliswitch (from_keyword, product_link) VALUES (?, ?)"
        for url in urls:
            cursor.execute(insert_query, (keyword, url))
        # Commit the transaction
        conn.commit()   
        time.sleep(5)
        SearchScraper.stop_chrome_debugging()
        