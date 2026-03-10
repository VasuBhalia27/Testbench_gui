from pathlib import Path
from openpyxl import Workbook, load_workbook
from datetime import datetime



class LogApp:
    def __init__(self):
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y--%H-%M")  # e.g. "20250729-142530"
        self.filename = f"logs_{timestamp}.xlsx"
        self.OUTPUT0_PATH = Path(__file__).parent
        self.OUTPUT1_PATH = self.OUTPUT0_PATH.parent
        self.LOG_FILE_PATH = self.OUTPUT1_PATH / "Logs" / self.filename
        
        self.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.LOG_FILE_PATH.is_file():
            wb = Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            # Write header row
            ws.append(["Sr No","DID", "Result"])
            wb.save(self.LOG_FILE_PATH)
            print(f"Created new Excel file with header at: {self.LOG_FILE_PATH}")
        else:
            print(f"Excel file already exists at: {self.LOG_FILE_PATH}")
        
        # Store workbook and worksheet as instance attributes
        self.wb = load_workbook(self.LOG_FILE_PATH)
        self.ws = self.wb.active
        self.sr_no = 1
        
    def add_log(self, did: str, result: str):
        """Append a row to the in-memory workbook.

        Call :meth:`close` (or use this object as a context manager) to
        persist the workbook to disk.  Saving on every row is avoided here
        because it is very slow for high-frequency logging.
        """
        self.ws.append([self.sr_no, did, result])
        self.sr_no += 1

    def close(self):
        """Flush the workbook to disk.  Call once when a test session ends."""
        self.wb.save(self.LOG_FILE_PATH)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
