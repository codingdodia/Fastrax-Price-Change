from config import app
import os
from FastraxPOS import FastraxPOS
from flask import request, jsonify, send_file
from database import ProductDatabase
# Import routes so they register with the app
import routes_products
# import PDFextractor 
import CSVwriter
from pdf import PYpdf

# Always resolve base directory for file operations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))




db_product = ProductDatabase()

@app.route('/upload', methods=['POST'])
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


@app.route('/extract_upcs', methods=['GET'])
def extract_upcs():
    print("Received request to extract UPCs from PDF")

    texts = extractor.extract_text()
    upcs_and_costs = extractor.extract_upc_and_cost(texts)

    return {'upcs_and_costs': upcs_and_costs}, 200

@app.route('/compare_upcs', methods=['POST'])
def compare_upcs():
    response = request.get_json()
    upc_list = response.get('upcs_and_costs', [])
    if not upc_list:
        return {'error': 'No UPCs provided'}, 400

    matched_products = []
    for item in upc_list:
        product = db_product.get_product_details(item['upc'])
        if product is not None:
            if 'cost' in item and item['cost'] != '.0000':
                product['cost'] = item['cost']

            matched_products.append(product)
        else:
            continue


    result = write_to_csv(matched_products)

    

    if result:
        return jsonify(matched_products), 200
    else:
        return jsonify({"error": "Failed to write products to CSV."}), 500
    


def write_to_csv(products:list):
    csv = CSVwriter.CSV_writer()
    print("Writing matched products to CSV...")

    return csv.write_products_to_csv(products)


@app.route('/updated-cost-csv', methods=['GET'])
def download_updated_cost_csv():
    csv_path = os.path.join(BASE_DIR, '..', 'csv', 'updated_cost.csv')
    csv_path = os.path.normpath(csv_path)
    if not os.path.exists(csv_path):
        return {'error': 'CSV file not found'}, 404
    return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='updated_cost.csv')


@app.route('/Login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    global fastrax_pos
    fastrax_pos = FastraxPOS()

    return fastrax_pos.login(username, password)

@app.route('/fetch_products_data', methods=['GET'])
def get_mass_products():

    products = fastrax_pos.get_mass_products()
    count = 0
    for product in products:
        
        if not db_product.lookup_product(product['upc']):
            db_product.add_product(product)
            count += 1

    return jsonify({"message":  f"{count} Products' data fetched and stored in database."}), 200


def matched_upcs_depts(matched_products):
    """Count the number of products in each department for matched UPCs."""

    
    dept_count = {} 
    for product in matched_products:
        #print(product)
        product_dept_num = product['department_num']
        if product_dept_num:
            dept_count[product_dept_num] = dept_count.get(product_dept_num, 0) + 1

    return dept_count
@app.route('/get_dept_list', methods=['POST'])
def get_dept_list():

    data = request.get_json()

    products = data.get('matched_products', [])
    print(type(products))
    print(len(products))  # Should be a list of product dictionaries

    # Process products as needed

    matched_depts = matched_upcs_depts(products)
    dept_names = db_product.get_department_names()

    depts_counts = []

    for (dept_num, count), dept_name in zip(matched_depts.items(), dept_names):
        depts_counts.append({
            "department_name": dept_name,
            "product_count": count
        })

    return jsonify({"deptCount": depts_counts}), 200




if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)


