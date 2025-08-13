from flask import request
from config import app
import re
from pdfminer.high_level import extract_pages
import os




class PDFUPCExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.upcs_with_costs = []

    def extract_unit_upcs(self):
        upc_cost = {
            "upc": None,
            "cost": None
        }
        all_text = ""
        for page_layout in extract_pages(self.pdf_path):
            for element in page_layout:
                if hasattr(element, "get_text"):
                    all_text += element.get_text()
        pattern = re.compile(r"UNIT UPC: (\d+)")
        matches = pattern.findall(all_text)

        for match in matches:
            upc_cost = {
                "upc": match,
                "cost": self.extract_unit_cost(match)
            }
            self.upcs_with_costs.append(upc_cost)

        return matches

    def extract_case_upcs(self):
        all_text = ""
        for page_layout in extract_pages(self.pdf_path):
            for element in page_layout:
                if hasattr(element, "get_text"):
                    all_text += element.get_text()
        pattern = re.compile(r"CASE UPC: (\d+)")
        matches = pattern.findall(all_text)
        for match in matches:
            upc_cost = {
                "upc": match,
                "cost": self.extract_case_cost(match)
            }
            self.upcs_with_costs.append(upc_cost)
        return matches

    def extract_case_cost(self, case_upc):
        all_text =  ""
        for page_layout in extract_pages(self.pdf_path):
            for element in page_layout:
                if hasattr(element, "get_text"):
                    all_text += element.get_text()
        lines = all_text.splitlines()
        for idx, line in enumerate(lines):
            if f"CASE UPC: {case_upc}" in line:
                # If 'NEW -' or 'OLD -' in line, look 3 lines above, else 2 lines above
                offset = 2
                if "NEW-" in line:
                    offset = 3
                cost_idx = idx - offset
                # If the cost line contains 'PER UNIT:', go another line above
                if cost_idx >= 0 and "PER UNIT:" in lines[cost_idx]:
                    cost_idx -= 1
                if cost_idx >= 0:
                    cost_line = lines[cost_idx].strip()
                    match = re.search(r"(\d+\.\d{4})", cost_line)
                    if match:
                        try:
                            return float(match.group(1))
                        except ValueError:
                            pass
        return None

    def unit_or_case_upc(self, upc):
        all_text = ""
        for page_layout in extract_pages(self.pdf_path):
            for element in page_layout:
                if hasattr(element, "get_text"):
                    all_text += element.get_text()
        lines = all_text.splitlines()
        for idx, line in enumerate(lines):
            if f"UNIT UPC: {upc}" in line:
                return 1
            elif f"CASE UPC: {upc}" in line:
                return 0
        return None
    
    def extract_unit_cost(self, upc):
        all_text = ""
        for page_layout in extract_pages(self.pdf_path):
            for element in page_layout:
                if hasattr(element, "get_text"):
                    all_text += element.get_text()
        lines = all_text.splitlines()
        for idx, line in enumerate(lines):
            if f"UNIT UPC: {upc}" in line:
                offset = 1
                cost_idx = idx - offset
                if cost_idx >= 0 and "OLD-" in lines[cost_idx]:
                    cost_idx -= 1
                if cost_idx >= 0:
                    cost_line = lines[cost_idx].strip()
                    match = re.search(r"(\d+\.\d{4})", cost_line)
                    if match:
                        try:
                            return float(match.group(1))
                        except ValueError:
                            pass
        return None

    def get_upc_type(self, upc):
        all_text = ""
        for page_layout in extract_pages(self.pdf_path):
            for element in page_layout:
                if hasattr(element, "get_text"):
                    all_text += element.get_text()
        lines = all_text.splitlines()
        for line in lines:
            if upc in line:
                # Check if 'UNIT UPC' appears before the UPC in the line
                upc_index = line.find(upc)
                if upc_index != -1:
                    before_upc = line[:upc_index]
                    if "UNIT UPC" in before_upc:
                        return 1
                    elif "CASE UPC" in before_upc:
                        return 0
                    else:
                        return -1
        return None
    
    def check_path(self, path):
        return os.path.isfile(path)
    
    def get_upcs_with_costs(self):
        return self.upcs_with_costs
    
# @app.route('/extract_upcs', methods=['GET'])
# def extract_upcs():
#     print("Received request to extract UPCs from PDF")
#     os.makedirs('uploads', exist_ok=True)
#     pdf_path = 'uploads/DougPriceChg.pdf'

    
#     extractor = PDFUPCExtractor(pdf_path)
#     if not extractor.check_path(pdf_path):
#         print("PDF file not found")
#         return {'error': 'PDF file not found'}, 404
#     unit_upcs = extractor.extract_unit_upcs()
#     case_upcs = extractor.extract_case_upcs()

#     all_upcs = unit_upcs + case_upcs

#     return {'upc_list': all_upcs}, 200










