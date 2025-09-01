import sqlite3


class ProductDatabase:
    def __init__(self, db_path='../database/products.db'):
        self.db_path = db_path
        self._create_table()
        self.conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=True)
        self.user_id = None

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=True)

    def _create_table(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upc TEXT NOT NULL,
                name TEXT NOT NULL,
                department_name TEXT NOT NULL,
                department_num INTEGER NOT NULL,
                cost REAL NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def _get_user_id(self, username):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user[0] if user else None

    def add_user(self, username):
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            conn.commit()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            print(f"User '{username}' added with ID: {user[0]}")
            self.user_id = user[0] if user else None
        except sqlite3.IntegrityError:
            print(f"User '{username}' already exists.")
            self.user_id = self._get_user_id(username)
            print(f"Retrieved existing user ID: {self.user_id}")
        finally:
            cursor.close()
            conn.close()

    def add_product(self, upc, name, department_name, department_num, cost, price, category) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        if self.user_id is None:
            #print("User ID is not set. Please add a user first.")
            return False
        try:
            cursor.execute(
                'INSERT INTO products (upc, name, department_name, department_num, cost, price, category, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (str(upc), name, department_name, department_num, cost, price, category, self.user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            self.update_product(str(upc), cursor=cursor, conn=conn, cost=cost, price=price, department_name=department_name, department_num=department_num, category=category)
            return False

    def lookup_product(self, upc) -> bool:
        """Check if a product with the given UPC exists in the database."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM products WHERE upc = ? and user_id = ?', (str(upc), self.user_id))
            product = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching product: {e}")
            product = None
        finally:
            cursor.close()
            conn.close()
        return bool(product)

    def get_product_details(self, upc, all_details:bool=True, details:list=None):
        conn = self._get_conn()
        cursor = conn.cursor()
        product = None
        try:
            if upc is None or upc == '':
                return None
            cursor.execute('SELECT * FROM products WHERE upc = ? AND user_id = ?', (str(upc), self.user_id))
            product = cursor.fetchone()
        except sqlite3.Error as e:
            print (f"Error fetching product details: {e}, UPC: {upc}")
        result = None
        if product:
            if all_details:
                result = {
                    'upc': product[1],
                    'name': product[2],
                    'department_name': product[3],
                    'department_num': product[4],
                    'cost': product[5],
                    'price': product[6],
                    'category': product[7]
                }
            elif details is not None:
                result = {}
                for detail in details:
                    if detail == 'upc':
                        result['upc'] = product[1]
                    elif detail == 'name':
                        result['name'] = product[2]
                    elif detail == 'department_name':
                        result['department_name'] = product[3]
                    elif detail == 'department_num':
                        result['department_num'] = product[4]
                    elif detail == 'cost':
                        result['cost'] = product[5]
                    elif detail == 'price':
                        result['price'] = product[6]
                    elif detail == 'category':
                        result['category'] = product[7]
        cursor.close()
        conn.close()
        return result
        
    
    def get_department_names(self):
        """Retrieve all unique department names from the database."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT department_name FROM products WHERE user_id = ?', (self.user_id,))
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dept[0] for dept in departments]
    
    def query_department(self, department_num):
        """Retrieve all products in a specific department."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE department_num = ? and user_id = ?', (department_num, self.user_id))
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return [
            {
                'upc': product[1],
                'name': product[2],
                'department_name': product[3],
                'department_num': product[4],
                'cost': product[5],
                'price': product[6],
                'category': product[7]
            } for product in products
        ]

    def update_product(self, upc, cost=None, price=None, department_name=None, department_num=None, category=None, cursor=None, conn=None):
        if conn is None:
            conn = self._get_conn()
        
        if cursor is None:
            cursor = conn.cursor()

        updates = []
        params = []

        if cost is not None:
            updates.append('cost = ?')
            params.append(cost)
        if price is not None:
            updates.append('price = ?')
            params.append(price)
        if department_name is not None:
            updates.append('department_name = ?')
            params.append(department_name)
        if department_num is not None:
            updates.append('department_num = ?')
            params.append(department_num)
        if category is not None:
            updates.append('category = ?')
            params.append(category)
        if self.user_id is not None:
            updates.append('user_id = ?')
            params.append(self.user_id)

        if not updates:
            cursor.close()
            conn.close()
            return False

        params.append(upc)
        query = f'UPDATE products SET {", ".join(updates)} WHERE upc = ?'
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def close(self):
        pass  # No persistent connection to close


# if __name__ == "__main__":
#     db = ProductDatabase()
#     db.add_user("test_user")
#     user_id = db._get_user_id("test_user")
#     print(f"User ID for 'test_user': {user_id}")

#     db.add_product("123456789012", "Test Product", "Electronics", 1, 50.0, 75.0, "Gadgets")
#     product = db.get_product_details("123456789012")
#     print(f"Product details: {product}")