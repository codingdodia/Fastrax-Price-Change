from config import app
import os
from flask_cors import CORS
from flask import request, jsonify, send_file
from database import ProductDatabase
import copy
import CSVwriter
from pdf import PYpdf 
from FetchFastrax import FastTraxFetcher

CORS(app)
# Always resolve base directory for file operations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_product = ProductDatabase()

# Delete all files in uploads folder at server start
uploads_dir = os.path.join(BASE_DIR, 'uploads')
if os.path.exists(uploads_dir):
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part in the request")
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return {'error': 'No selected file'}, 400
    global pdf_path
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    pdf_path = os.path.join(uploads_dir, file.filename)
    # Remove old file if it exists
    if os.path.exists(pdf_path):
         os.remove(pdf_path)
    global extractor
    extractor = PYpdf(pdf_path)
    print("Saving to uploads/")
    file.save(pdf_path)
    if extractor.check_path(pdf_path):
        return {'message': 'File uploaded successfully'}, 200
    
    return {'error': 'Invalid file path'}, 400


@app.route('/api/extract_upcs', methods=['GET'])
def extract_upcs():
    print("Received request to extract UPCs from PDF")

    texts = extractor.extract_text()
    upcs_and_costs = extractor.extract_upc_and_cost(texts)

    print

    return {'upcs_and_costs': upcs_and_costs}, 200

@app.route('/api/compare_upcs', methods=['POST'])
def compare_upcs():
    db_product.add_user("mountain")
    response = request.get_json()
    upc_list = response.get('upcs_and_costs', [])
    if not upc_list:
        return {'error': 'No UPCs provided'}, 400

    matched_products_upcs = []
    for item in upc_list:
        product = db_product.get_product_details(item['upc'])
        if product is not None:
            matched_products_upcs.append(product)
        else:
            continue
    if not matched_products_upcs:
        return jsonify({"error": "No matching products found."}), 404
    return jsonify(matched_products_upcs), 200

    
@app.route('/api/write_to_csv', methods=['POST'])
def write_to_csv():

    data = request.get_json()
    upc_list = data.get('upc_list', [])
    csv = CSVwriter.CSV_writer()
    print("Writing matched products to CSV...")
    
    return csv.write_products_to_csv(matched_products)

@app.route('/api/updated-cost-csv', methods=['GET'])
def download_updated_cost_csv():
    csv_path = os.path.join(BASE_DIR, '..', 'csv', 'updated_cost.csv')
    csv_path = os.path.normpath(csv_path)
    if not os.path.exists(csv_path):
        return {'error': 'CSV file not found'}, 404
    return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='updated_cost.csv')


@app.route('/api/Login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    global fastrax_fetcher
    fastrax_fetcher = FastTraxFetcher()
    db_product.add_user(username)

    return fastrax_fetcher.login(username, password)
    # global fastrax_pos
    # fastrax_pos = FastraxPOS()

    # return fastrax_pos.login(username, password)
@app.route('/api/2fa', methods=['POST'])
def complete_2FA():
    data = request.get_json()
    code = data.get('code')
    response = data.get('response')
    global fastrax_fetcher
    if fastrax_fetcher:
        return fastrax_fetcher.complete_2FA(code, response)
    return {'error': 'Not logged in'}, 401

@app.route('/api/fetch_products_data', methods=['GET'])
def fetch_all_products_data():

    products = fastrax_fetcher.fetch_all_items()
    count = 0
    for product in products:
        if not db_product.lookup_product(product['upc'] and product['upc'] != ''):
            db_product.add_product(
                product['upc'],
                product['name'],
                product['department_name'],
                product['department_num'],
                product['cost'],
                product['price'],
                product['category']
            )
            count += 1

    return jsonify({"message":  f"{count} Products' data fetched and stored in database."}), 200


def matched_upcs_depts(passed_in_matched_products, dept_names):
    """Count the number of products in each department for matched UPCs."""


    dept_count = {}
    for product in passed_in_matched_products:
        #print(product)
        product_dept_name = product['department_name']
        if product_dept_name in dept_names:
            dept_count[product_dept_name] = dept_count.get(product_dept_name, 0) + 1
    print(dept_count)

    return dept_count
@app.route('/api/get_dept_list', methods=['POST'])
def get_dept_list():

    data = request.get_json()
    global matched_products
    matched_products = data.get('matched_products', [])  # Should be a list of product dictionaries

    # Process products as needed

    dept_names = db_product.get_department_names()
    depts_counts = matched_upcs_depts(matched_products, dept_names)

    return jsonify({"deptCount": depts_counts}), 200

@app.route('/api/update_prices', methods=['POST'])
def update_prices():

    data = request.get_json()
    matched_products_copy = copy.deepcopy(matched_products)
    upcs_and_costs = data['upc_list']['upcs_and_costs']
    matched_products_copy = change_products_cost(upcs_and_costs, matched_products_copy)
    products_updated = []
    for product in matched_products_copy:
        if product['department_name'] == data['department']:
            if data['isPercent']:
                product['price'] = round(float(product['price']) * (1 + float(data['value']) / 100), 2)
                
                products_updated.append(product)
            else:
                product['price'] = round(float(product['price']) + float(data['value']), 2)

                products_updated.append(product)

    return jsonify({'products_updated': products_updated, 'old_products': matched_products}), 200

@app.route('/api/confirm_prices', methods=['POST'])
def confirm_prices():
    data = request.get_json()
    
    global matched_products
    products_updated = []
    for product in matched_products:
        if product['department_name'] == data['department']:
            if data['isPercent']:
                product['price'] = round(float(product['price']) * (1 + float(data['value']) / 100), 2)
                products_updated.append(product)
            else:
                product['price'] = round(float(product['price']) + float(data['value']), 2)

                products_updated.append(product)


    return jsonify({'products_updated': products_updated, 'message': 'Prices confirmed!'}), 200

def change_products_cost(upc_list, matched_products_copy):

    for item in upc_list:
        print('Processing item:', item)
        if 'cost' in item and item['cost'] != '.0000':
            print('Updating cost for UPC:', item['upc'], 'to', item['cost'])
            for product in matched_products_copy:
                if product['upc'] == item['upc']:
                    product['cost'] = item['cost']

    return matched_products_copy


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


