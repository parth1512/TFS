import time
import shutil
import os
import openpyxl
import threading
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

    def _poll_loop(self):
        while self.running:
            try:
                config = config_loader.load_config() # Reload config? Or just use cached? Let's use cached primarily but handle updates if implemented. 
                # For simplicity, access global config object, assuming it's static for now or updated via GUI restart.
                # Actually, main loop might re-read config on restart.
                # Let's just use the current config from loader.
                
                file_path = config.get("excel_file", "data.xlsx")
                interval = config.get("refresh_interval", 1)
                
                if not os.path.exists(file_path):
                    logger.error(f"Excel file not found: {file_path}")
                    time.sleep(interval)
                    continue

                # Handle file locking: Copy to temp file
                temp_file = "temp_read.xlsx"
                try:
                    shutil.copy2(file_path, temp_file)
                except Exception as e:
                    logger.warning(f"Could not copy Excel file (might be locked/writing): {e}")
                    # If copy fails, we might skip this cycle or try reading original (which might fail too)
                    time.sleep(interval)
                    continue

                try:
                    wb = openpyxl.load_workbook(temp_file, data_only=True)
                    ws = wb.active
                    
                    reg_map = config.get("register_map", [])
                    
                    for mapping in reg_map:
                        cell_ref = mapping.get("excel_cell")
                        reg_addr = mapping.get("register")
                        dtype = mapping.get("type", "U16")
                        
                        if cell_ref and reg_addr:
                            try:
                                cell_val = ws[cell_ref].value
                                if cell_val is not None:
                                    register_manager.update_register(reg_addr, cell_val, dtype)
                                else:
                                    logger.debug(f"Cell {cell_ref} is empty.")
                            except Exception as e:
                                logger.error(f"Error reading cell {cell_ref}: {e}")
                                
                    wb.close()
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
