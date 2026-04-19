import pandas as pd
from io import BytesIO
import re
import json
import math


class ExcelParser:

    def __init__(self):
        self.current_group = None
        self.MOVE_ITEMS = {"PROMOTION", "DISCOUNT", "REFUND"}
        self.PROMO_GROUP = "promotion_discount_refund"
        self.result = {
            "date": None,
            "upto": None,
            "groups": {}
        }

    async def parse_excel(self, file_bytes):

        file = BytesIO(file_bytes)
        df = pd.read_excel(file)

        for _, row in df.iterrows():

            cells = self.clean_cells(row)

            if not cells:
                continue

            line = " ".join(cells)
            lower = line.lower()

            # -----------------------
            # Extract FROM date
            # -----------------------
            if self.result["date"] is None and "from" in lower:
                match = re.search(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}", line)
                if match:
                    self.result["date"] = match.group()
                continue

            # -----------------------
            # Extract TO date
            # -----------------------
            if self.result["upto"] is None and "to" in lower:
                match = re.search(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}", line)
                if match:
                    self.result["upto"] = match.group()
                continue

            # -----------------------
            # Detect Exclusive Departments
            # -----------------------
            if "exclusive departments" in lower:
                self.current_group = self.format_group_name("Exclusive Departments")
                self.result["groups"].setdefault(self.current_group, [])
                continue

            # -----------------------
            # Detect VOID LINES
            # -----------------------
            if "void lines" in lower:
                self.current_group = self.format_group_name("VOID LINES")
                self.result["groups"].setdefault(self.current_group, [])
                continue

            # -----------------------
            # Detect Summary Groups
            # -----------------------
            if "summary" in lower:
                self.current_group = self.format_group_name(line)
                self.result["groups"].setdefault(self.current_group, [])
                continue

            # -----------------------
            # Skip headers
            # -----------------------
            if "description" in lower:
                continue

            # -----------------------
            # Skip totals
            # -----------------------
            if self.is_total(line):
                continue

            # -----------------------
            # Skip separators
            # -----------------------
            if all(self.is_separator(c) for c in cells):
                continue

            # -----------------------
            # Parse records
            # -----------------------
            if self.current_group:

                record = None

                if len(cells) >= 3 and cells[-1].replace(".", "").isdigit():
                    record = {
                        "name": cells[0],
                        "qty": cells[1],
                        "amount": self.parse_amount(cells[-1])
                    }

                elif len(cells) >= 2:
                    record = {
                        "name": cells[0],
                        "amount": self.parse_amount(cells[-1])
                    }

                if not record:
                    continue

                if record["amount"] is None:
                    continue

                name_upper = record["name"].upper()

                # Move Promotion / Discount / Refund
                if self.current_group == "sales_summary" and name_upper in self.MOVE_ITEMS:
                    self.result["groups"].setdefault(self.PROMO_GROUP, [])
                    self.result["groups"][self.PROMO_GROUP].append(record)
                else:
                    self.result["groups"][self.current_group].append(record)

        # json_output = json.dumps(self.result, indent=4)
        # print(json_output)
        # with open("output.json", "w", encoding="utf-8") as f:
        #     f.write(json_output)

        # print(json_output)
        return self.result


    # -----------------------
    # Helpers
    # -----------------------
    def format_group_name(self, name):
        name = name.strip().lower()
        name = re.sub(r"[^a-z0-9\s]", "", name)
        name = re.sub(r"\s+", "_", name)
        return name

    def clean_cells(self, row):
        return [str(c).strip() for c in row if pd.notna(c) and str(c).strip() != ""]

    def parse_amount(self, v):
        try:
            return float(str(v).replace(",", ""))
        except:
            return None

    def is_separator(self, text):
        return re.fullmatch(r"-+", text) is not None

    def is_total(self, text):
        return "total" in text.lower()

    def clean_json(self, data):
        if isinstance(data, dict):
            return {k: self.clean_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.clean_json(v) for v in data]
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return None
            return data
        else:
            return data