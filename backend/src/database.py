import sqlite3

class ProductDatabase:
    def __init__(self, db_path='..\\database\\products.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upc TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department_name TEXT NOT NULL,
                department_num INTEGER NOT NULL,
                cost REAL NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        self.cursor.close()

    def add_product(self, upc, name, department_name, department_num, cost, price, category) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO products (upc, name, department_name, department_num, cost, price, category) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (upc, name, department_name, department_num, cost, price, category)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.update_product(upc, cost=cost, price=price, department_name=department_name, department_num=department_num, category=category)
            return False

    def lookup_product(self, upc) -> bool:
        
        """Check if a product with the given UPC exists in the database."""

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE upc = ?', (upc,))
        product = cursor.fetchone()
        cursor.close()

        if product:
            return True
        else:
            return False
    
    def get_product_details(self, upc, all_details:bool=True, details:list=None):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE upc = ?', (upc,))

        product = None
        try:
            product = cursor.fetchone()
        except sqlite3.Error as e:
            print (f"Error fetching product details: {e}")
        if product:
            if all_details:
                return {
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
                return result
            cursor.close()
            return None
        else:
            cursor.close()
            return None
        
    
    def get_department_names(self):
        """Retrieve all unique department names from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT department_name FROM products')
        departments = cursor.fetchall()
        cursor.close()
        return [dept[0] for dept in departments]
    
    def query_department(self, department_num):
        """Retrieve all products in a specific department."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE department_num = ?', (department_num,))
        products = cursor.fetchall()
        cursor.close()
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

    def update_product(self, upc, cost=None, price=None, department_name=None, department_num=None, category=None):
        cursor = self.conn.cursor()
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

        if not updates:
            return False

        params.append(upc)
        query = f'UPDATE products SET {", ".join(updates)} WHERE upc = ?'
        cursor.execute(query, params)
        self.conn.commit()
        cursor.close()
        return True

    def close(self):
        self.conn.close()


