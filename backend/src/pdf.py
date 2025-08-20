import PyPDF2
import re
import os


class PYpdf:

    def extract_number_after_for_dates(self):
        texts = self.extract_text()
        results = []
        for text in texts:
            # Find all matches after 'FOR DATES', remove all whitespace from the number
            matches = re.findall(r"FOR DATES\s*([\d\s]+)", text)
            for match in matches:
                cleaned = re.sub(r"\s+", "", match)
                results.append(cleaned)
        return results

    def __init__(self, path):

        self.path = path


    def extract_text(self) -> list[str]:
        if not self.check_path(self.path):
            return []
        with open(self.path, "rb") as pdf:
            reader = PyPDF2.PdfReader(pdf, strict=False)
            pdf_text = []
            for page in reader.pages:
                content = page.extract_text()
                pdf_text.append(content)

        return pdf_text
    
    def extract_date(self):
        texts = self.extract_text()
        for text in texts:
            # Look for 'FOR DATES' followed by two 8-digit numbers separated by a dash
            match = re.search(r"FOR DATES\s*\d{8}\s*-\s*(\d{8})", text)
            if match:
                return match.group(1)
        return None


    def extract_upc_and_cost(self, texts) -> list[dict]:
        upcs_and_costs = []

        unit_costs = []
        unit_upcs = []

        case_upcs = []
        case_costs = []

        date = self.extract_date()
        if date:
            print("Extracted Date:", date)

        for text in texts:

            unit_upc = re.findall(r'UNIT UPC: (\d+)', text)
            for upc in unit_upc:
                unit_upcs.append(upc)


            case_upc = re.findall(r'CASE UPC: (\d+)', text)
            for upc in case_upc:
                case_upcs.append(upc)

            

            # Split lines for more control    
            lines = text.split('\n')

            for line in lines:
                if re.search(rf'\b{re.escape(date)}\b', line):
                    matches = re.findall(r'(?:\d*\.\d{4})', line)
                    for match in matches:
                        case_costs.append(match)

                if "PER UNIT:" in line:
                    # Extract the value after "PER UNIT:"
                    match = re.search(r'PER UNIT:\s*\$?([\d\.]+)', line)
                    if match:
                        per_unit_value = match.group(1)
                        unit_costs.append(per_unit_value)


        if(len(case_costs) == len(case_upcs)):
            for i in range(len(case_upcs)):
                upcs_and_costs.append({
                    'upc': case_upcs[i],
                    'cost': case_costs[i]
                })   

        if (len(unit_upcs) == len(unit_costs)):
            for i in range(len(unit_upcs)):
                upcs_and_costs.append({
                    'upc': unit_upcs[i],
                    'cost': unit_costs[i]
                })

        return upcs_and_costs

    def check_path(self, path) -> bool:

        if os.path.exists(path) and (path.endswith('.PDF') or path.endswith('.pdf')):
            return os.path.isfile(path)
        return False
