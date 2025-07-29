from pathlib import Path
from openpyxl import Workbook, load_workbook



class LogApp:
    def __init__(self):
        self.filename = "logs.xlsx"
        self.OUTPUT0_PATH = Path(__file__).parent
        self.OUTPUT1_PATH = self.OUTPUT0_PATH.parent
        self.LOG_FILE_PATH = self.OUTPUT1_PATH / "Logs" / self.filename
        
        self.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.LOG_FILE_PATH.is_file():
            wb = Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            # Write header row
            ws.append(["DID", "Result"])
            wb.save(self.LOG_FILE_PATH)
            print(f"Created new Excel file with header at: {self.LOG_FILE_PATH}")
        else:
            print(f"Excel file already exists at: {self.LOG_FILE_PATH}")
        
        # Store workbook and worksheet as instance attributes
        self.wb = load_workbook(self.LOG_FILE_PATH)
        self.ws = self.wb.active
        
    def add_log(self, did: str, result: str):
        self.ws.append([did, result])
        self.wb.save(self.LOG_FILE_PATH)
        print(f"Appended log: {did}, {result}")