from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service   
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from flask import request, jsonify
import time


class FastraxPOS:

    def __init__(self): 
        self.products = []
        self.product = {
                    "name": "", 
                    "dept": "",
                    "cost": "",
                    "price": "",
                    "category": ""

                                }
            
        self.service = Service("..\\drivers\\geckodriver.exe")
        self.options = Options()
        self.options.add_argument("--headless")  # Run in headless mode USE THIS IF YOU WANT TO RUN IN THE BACKGROUND
        


    def to_json(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'department_num': self.department_num,
            'department_name': self.department_name,
            'category': self.category,
            'cost': self.cost,
            'price': self.price
        }
    
    def login(self, username, password):
        try:
            self.driver = webdriver.Firefox(service=self.service, options=self.options)
            self.actions = ActionChains(self.driver)
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")

        print("Attempting to log in...")
        self.driver.get("https://cc.fastraxpos.com/")
        input_element = self.driver.find_element(By.NAME, "email")
        input_element.send_keys(username)
        input_element = self.driver.find_element(By.NAME, "password")
        input_element.send_keys(password)
        input_element.send_keys(Keys.RETURN)
        time.sleep(2)

        print("Login attempt completed. Checking for success...")

        # Check if login was successful by looking for a specific element on the dashboard page
        # This assumes that the dashboard page has a unique element that only appears when logged in

        for request in self.driver.requests:
            
            if request.url == "https://cc.fastraxpos.com/client/dashboard":
                if request.response.status_code == 200:
                    return jsonify({"message": "Login successful"}), 200
                else:
                    return jsonify({"message": "Login failed"}), 401
        return jsonify({"message": "Login failed"}), 401
    

    def get_mass_products(self):
        import sys
        import threading

        def timer_thread(stop_event):
            start_time = time.time()
            first = True
            while not stop_event.is_set():
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                if not first:
                    sys.stdout.write('\033[F')
                sys.stdout.write(f"\rFetching products... Press Ctrl+C to stop. Elapsed time: {mins:02d}:{secs:02d}\n")
                sys.stdout.flush()
                time.sleep(1)
                first = False
            sys.stdout.write("\n")

        stop_event = threading.Event()
        timer = threading.Thread(target=timer_thread, args=(stop_event,))
        timer.start()

        count = 0

        try:
            self.driver.set_window_size(1920, 1080)
            self.driver.get('https://cc.fastraxpos.com/client/pos/mass-updates')
            time.sleep(5)

            result_box = self.driver.find_element(By.ID, 'result-box')
            item_list = result_box.find_element(By.TAG_NAME, 'select')
            item_list.click()
            entries = item_list.find_elements(By.TAG_NAME, 'option')
            for entry in entries:
                if entry.text == '50':               
                    entry.click()
                    break
            time.sleep(0.5)
            odds = self.driver.execute_script("return document.getElementsByClassName('odd');")
            data_table = self.driver.find_element(By.CLASS_NAME, 'dataTables_scroll')
            interior_table = data_table.find_element(By.CLASS_NAME, "dataTables_empty")
            div_els = interior_table.find_elements(By.TAG_NAME, 'div')  
            for div in div_els:
                if div.text == "Load All Items":
                    div.click()
                    break
            time.sleep(7)
            item_table = self.driver.find_element(By.ID, 'itemList')
            table_body = item_table.find_element(By.TAG_NAME, 'tbody')
            item_list_paginate = self.driver.find_element(By.ID, 'itemList_paginate')
            item_list_paginate_span = item_list_paginate.find_element(By.TAG_NAME, 'span')
            page_index = item_list_paginate_span.find_elements(By.TAG_NAME, 'a')
            amount_of_pages = page_index[len(page_index) -1].text

            # last_button = item_list_paginate.find_element(By.ID, 'itemList_last')
            # last_button.click()
            time.sleep(5)

            for page in range(1 ,3):
                print(f"Fetching page {page} of {amount_of_pages}...")
                rows = table_body.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    self.driver.execute_script("arguments[0].scrollIntoView();", row)
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) > 1:
                        item_name = cols[1].text
                        item_upc = cols[2].text
                        item_cost = cols[3].text
                        item_price = cols[4].text
                        item_dept = cols[5].text
                        try:
                            item_category = row.find_element(By.TAG_NAME, 'span').get_attribute('data-title')
                        except NoSuchElementException:
                            item_category = cols[6].text
                        self.product = {
                            "name": item_name, 
                            "upc": item_upc,
                            "cost": item_cost,
                            "price": item_price,
                            "department": item_dept,
                            "category": item_category
                        }
                        self.products.append(self.product)
                        count += 1
                        print(f"Products found: {count}", end='\r')
                    else:
                        break
                next_button = item_list_paginate.find_element(By.ID, 'itemList_next')
                if next_button.get_attribute('class') == 'paginate_button next disabled':
                    break
                next_button.click()
                time.sleep(5)

        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Stopping timer...")
        finally:
            stop_event.set()
            timer.join()
            print(f"\nTotal products found: {count}")
        return self.products, 200

