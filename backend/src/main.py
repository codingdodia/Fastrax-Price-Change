from config import app
import os
from FastraxPOS import FastraxPOS
from flask import request, jsonify, send_file
from database import ProductDatabase
# Import routes so they register with the app
import routes_products
import PDFextractor 
import CSVwriter
from pdf import PYpdf



extractor = PYpdf()
db_product = ProductDatabase()

@app.route('/upload', methods=['POST'])
def upload_file():
    os.makedirs('uploads', exist_ok=True)
    print("Received request to upload file")
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    file.save(os.path.join('uploads', file.filename))
    return {'message': 'File uploaded successfully'}, 200


@app.route('/extract_upcs', methods=['GET'])
def extract_upcs():
    print("Received request to extract UPCs from PDF")
    os.makedirs('uploads', exist_ok=True)
    pdf_path = 'uploads/DougPriceChg.pdf'

    if not extractor.check_path(pdf_path):
        print("PDF file not found")
        return {'error': 'PDF file not found'}, 404

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
        return jsonify({"message": "Products matched and written to CSV successfully."}), 200
    else:
        return jsonify({"error": "Failed to write products to CSV."}), 500
    


def write_to_csv(products:list):
    #pdf_path = "..\\uploads\\DougPriceChg.PDF"
    #extractor = PDFextractor.PDFUPCExtractor(pdf_path)
    csv = CSVwriter.CSV_writer()
    print("Writing matched products to CSV...")

    return csv.write_products_to_csv(products)

    # for product in products:
    #     upc_type = extractor.get_upc_type(product['upc'])
    #     if upc_type == 1:
    #         unit_cost = extractor.extract_unit_cost(product['upc'])
    #         if unit_cost is not None:
    #             csv.write_products_to_csv(product, updated_cost=unit_cost)
    #         else:
    #             csv.write(product)
    #     elif upc_type == 0:
    #         case_cost = extractor.extract_case_cost(product['upc'])
    #         if case_cost is not None:
    #             csv.write_products_to_csv(product, updated_cost=case_cost)
    #         else:
    #             csv.write_products_to_csv(product)
    #     else:
    #         csv.write_products_to_csv(product)

@app.route('/updated-cost-csv', methods=['GET'])
def download_updated_cost_csv():
    csv_path = os.path.join('csv', 'updated_cost.csv')

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


if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)


