# import os for file path operations
import os
import csv
# from PDFextractor import PDFUPCExtractor

class CSV_writer:
    def __init__(self):
        # Always resolve the path relative to this file's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(base_dir, '..', 'csv', 'updated_cost.csv')
        self.file_path = os.path.normpath(self.file_path)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, mode='w', newline='') as file:
            file.write('')  # Create or clear the file
        
        # self.extractor = PDFUPCExtractor("..\\uploads\\DougPriceChg.pdf")

    def write(self, product, updated_cost = 0, updated_price = 0, description='', manufacturer='', brand='', is_active=1, vendor='', part_num='', part_num_units='', part_cost='', child_upc='', num_units=''):
        fieldNames = ['upc', 'name', 'description', 'department', 'department_number', 'category',
                      'manufacturer', 'brand', 'is_active', 'cost', 'price',
                      'vendor', 'part_num', 'part_num_units', 'part_cost', 'child_upc', 'num_units']
        
        cost = updated_cost if updated_cost != 0 else product['cost']
        price = updated_price if updated_price != 0 else product['price']

        row = {
            'upc': product['upc'], 
            'name': product['name'], 
            'description': description, 
            'department': product['department_name'], 
            'department_number': product['department_num'], 
            'category': product['category'], 
            'manufacturer': manufacturer, 
            'brand': brand, 
            'is_active': is_active, 
            'cost': cost, 
            'price': price, 
            'vendor': vendor, 
            'part_num': part_num, 
            'part_num_units': part_num_units, 
            'part_cost': part_cost, 
            'child_upc': child_upc, 
            'num_units': num_units
        }
        try:
            with open(self.file_path, 'r', newline='') as file:
                lines = list(file)
            if len(lines) > 1:
                # Append if line 2 exists
                with open(self.file_path, 'a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldNames)
                    writer.writerow(row)
                return
            else:
                # If file is new or only header exists, write header and first row
                with open(self.file_path, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldNames)
                    writer.writeheader()
                    writer.writerow(row)
        except FileNotFoundError:
            pass
        # Write header and first row if file is new or only header exists
        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerow(row)
            

    def append(self, product):
        with open(self.file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([product])
    
    def write_products_to_csv(self, products, updated_cost = 0, updated_price = 0):
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            print("Writing header to CSV...")
            writer.writerow(['upc','name','description','department','department_number','category','manufacturer','brand','is_active','cost','price','vendor','part_num','part_num_units','part_cost','child_upc','num_units'])
            # Prepare all rows
            rows = []
            count = 0
            for product in products:
                count += 1
                #print(f"Processing product {count}/{len(products)}: {product['name']} ({product['upc']})")
                rows.append([
                    product.get('upc', ''),
                    product.get('name', ''),
                    product.get('description', ''),
                    product.get('department', ''),
                    product.get('department_number', ''),
                    product.get('category', ''),
                    product.get('manufacturer', ''),
                    product.get('brand', ''),
                    product.get('is_active', ''),
                    product.get('cost', 0),
                    product.get('price', 0),
                    product.get('vendor', ''),
                    product.get('part_num', ''),
                    product.get('part_num_units', ''),
                    product.get('part_cost', ''),
                    product.get('child_upc', ''),
                    product.get('num_units', ''),
                ])
            writer.writerows(rows) 

            return {'message': 'CSV writing completed successfully.'}, 200

