
import time
import sys
import threading
from modbus_server import modbus_server
from excel_reader import excel_reader
from register_manager import register_manager
from logger import logger, log_queue

def verify_setup():
    print("--- Modbus Data Verification Script ---")
    print("1. Starting Excel Reader...")
    excel_reader.start()

    print("2. Waiting 5 seconds for data poll...")
    time.sleep(5)
    
    print("3. Checking Register 40005 (H2S Concentration)...")
    try:
        # Address 40005 maps to offset 0 in our logic if we subtracted 40001, 
        # BUT update_register implementation:
        # if >= 40001: -= 40001 (so 40005 -> 4)
        offset = 40005 - 40001
        count = 2 # Float is 2 words
        
        values = register_manager.store.getValues(offset, count)
        print(f"   Raw Registers (Offset {offset}): {values}")
        
        import struct
        if values:
            packed = struct.pack('>HH', *values)
            val_float = struct.unpack('>f', packed)[0]
            print(f"   Decoded Float Value: {val_float:.4f}")
            
            if abs(val_float - 14.0) < 0.1:
                print("   [PASS] Value matches expected 14.0 from '14 ppm hrs.xls'")
            else:
                print(f"   [FAIL] Value {val_float} does not match expected 14.0")
        else:
            print("   [FAIL] No values read.")
            
    except Exception as e:
        print(f"   [ERROR] Could not access registers: {e}")

    print("4. Cleaning up...")
    excel_reader.stop()
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_setup()
