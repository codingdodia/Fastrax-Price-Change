import requests
from bs4 import BeautifulSoup
import sys


class FastTraxFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        self.products = []
        self.product = {
                    "name": "",
                    'upc': "",
                    "dept_name": "",
                    "department_num": "",
                    "cost": "",
                    "price": "",
                    "category": ""
                }

    def login(self, username, password) -> bool:
        # 1. Load the login page to get the CSRF token
        login_page = self.session.get("https://cc.fastraxpos.com/login")
        soup = BeautifulSoup(login_page.text, "html.parser")
        token = soup.find("input", {"name": "_token"})["value"]

        # 2. Prepare the payload with the token, email, and password
        payload = {
            "_token": token,
            "email": username,
            "password": password
        }

        # 3. Post the login form
        response = self.session.post("https://cc.fastraxpos.com/login", data=payload)

        # 4. Check if login was successful (look for dashboard or a known element)
        if response.url.endswith("/dashboard"):
            print("Login successful")
            self.logged_in = True
            return {"message": "Login successful"}, 200
        else:
            print("Login failed")
            self.logged_in = False
            return {"message": "Login failed"}, 401

    def go_to_mass_update(self):
        """Navigate to the Mass Updates page and fetch items,
        Going to this page is neccessary to call the get-items API"""
        response = self.session.get("https://cc.fastraxpos.com/client/pos/mass-updates")
        if response.status_code == 200:
            print("Navigated to Mass Updates page")
        else:
            print("Failed to navigate to Mass Updates page")

    def get_items(self, draw, offset, per_page):
        """Fetch items for from the /get-items API"""
        payload = {
            "draw": str(draw),
            "offset": str(offset),
            "perPage": str(per_page),
            "search": "",
            "zone": "854",
            "filters[priceType]": "",
            "filters[product_type]": "all",
            "filters[active]": "active",
            "order": "product_name+asc",
            "settings[tag_group_setting]": "all",
            "settings[item_type]": "all",
            "settings[product_aliases]": "all",
            "settings[active_dropdown]": "active",
            "vendor_id": "0",
            "matching_vendor_only": "",
            "include_child_items": "",
            "reloadCache": "0",
            "searchType": "desc-upc"
        }
        response = self.session.get("https://cc.fastraxpos.com/client/pos/mass-updates/get-items", params=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve items")
            return None

    def process_items(self, items):
        if not items:
            print("No items to process")
            return

        for item in items.get('data', []):
            self.product['name'] = item.get('product_name')
            self.product['upc'] = item.get('product_upc')
            self.product['department_name'] = item.get('department_name')
            self.product['department_num'] = item.get('department_number')
            self.product['cost'] = item.get('cost')
            self.product['price'] = item.get('price')
            self.product['category'] = item.get('category_path')
            self.products.append(self.product.copy())
            print(f"Product Name: {item.get('product_name')}, UPC: {item.get('product_upc')}")

    def fetch_all_items(self):
        if not self.logged_in:
            print("Not logged in. Please login first.")
            return

        self.go_to_mass_update()
        response = self.get_items(1, 0, sys.maxsize) # Fetch all items in one go, sys.maxsize is used to get the most items in one page
        self.process_items(response)

        if(response):
            records_Filtered = response.get('recordsFiltered', 0)
            draws = 1
            if(records_Filtered > sys.maxsize):
                draws = records_Filtered // sys.maxsize + 1
                offset = sys.maxsize
                for draw in range(1, draws + 1):
                    response = self.get_items(draw, offset, sys.maxsize)
                    self.process_items(response)
                    offset += sys.maxsize

        if self.products:
            print(f"Retrieved {len(self.products)} products")
            return self.products

# if __name__ == "__main__":
#     fetcher = FastTraxFetcher()
#     if fetcher.login("mountain", "Ruhan2019"):
#         fetcher.fetch_all_items()





