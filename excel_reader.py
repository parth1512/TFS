import time
import shutil
import os
import pandas as pd
import threading
import re
from logger import logger
from config_loader import config_loader
from register_manager import register_manager

class ExcelReader:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("Excel polling started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Excel polling stopped.")

    def _parse_cell_ref(self, cell_ref):
        """
        Parses a cell reference like 'F49' into (row_index, col_index).
        Returns (None, None) if invalid.
        Uses 0-based indexing for returned values.
        """
        if not cell_ref:
            return None, None
            
        match = re.match(r"([A-Z]+)([0-9]+)", cell_ref.upper())
        if not match:
            return None, None
            
        col_str, row_str = match.groups()
        
        # Convert row string to 0-based index
        # Excel rows start at 1. Pandas with header=None starts at 0.
        # So '1' -> 0.
        try:
            row_idx = int(row_str) - 1
        except ValueError:
            return None, None
            
        # Convert column string to 0-based index
        # A=0, B=1, ... Z=25, AA=26
        col_idx = 0
        for char in col_str:
            col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
        col_idx -= 1
        
        return row_idx, col_idx

    def _poll_loop(self):
        while self.running:
            try:
                config = config_loader.load_config()
                file_path = config.get("excel_file", "data.xlsx")
                interval = config.get("refresh_interval", 1)
                
                if not os.path.exists(file_path):
                    logger.error(f"Excel file not found: {file_path}")
                    time.sleep(interval)
                    continue

                # Handle file locking: Copy to temp file
                # Use a temp extension that matches original to help engines guess format if needed
                name, ext = os.path.splitext(file_path)
                temp_file = f"temp_read{ext}"
                
                try:
                    shutil.copy2(file_path, temp_file)
                except Exception as e:
                    logger.warning(f"Could not copy Excel file (might be locked/writing): {e}")
                    time.sleep(interval)
                    continue

                try:
                    # Read using pandas, no header assumed to match absolute cell references
                    df = pd.read_excel(temp_file, header=None)
                    
                    reg_map = config.get("register_map", [])
                    
                    for mapping in reg_map:
                        cell_ref = mapping.get("excel_cell")
                        reg_addr = mapping.get("register")
                        dtype = mapping.get("type", "U16")
                        
                        if cell_ref and reg_addr:
                            row_idx, col_idx = self._parse_cell_ref(cell_ref)
                            
                            if row_idx is not None and col_idx is not None:
                                try:
                                    # check bounds
                                    if row_idx < len(df) and col_idx < df.shape[1]:
                                        cell_val = df.iloc[row_idx, col_idx]
                                        
                                        # Handle NaN/None
                                        if pd.isna(cell_val):
                                            logger.debug(f"Cell {cell_ref} is empty.")
                                        else:
                                            register_manager.update_register(reg_addr, cell_val, dtype)
                                    else:
                                        logger.warning(f"Cell {cell_ref} is out of bounds.")
                                except Exception as e:
                                    logger.error(f"Error reading cell {cell_ref}: {e}")
                            else:
                                logger.warning(f"Invalid cell reference: {cell_ref}")
                                
                except Exception as e:
                    logger.error(f"Error reading Excel workbook: {e}")
                finally:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass

                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Unexpected error in Excel polling loop: {e}")
                time.sleep(1)

excel_reader = ExcelReader()
