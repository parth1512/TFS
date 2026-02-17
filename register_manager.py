import threading
import struct
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.datastore import ModbusDeviceContext 
from logger import logger

class RegisterManager:
    def __init__(self):
        self.lock = threading.Lock()
        # Initialize with a large enough block to cover typical usage
        # We'll use a single block for Holding Registers (HR) - Function Code 03
        # and Input Registers (IR) - Function Code 04 checks.
        self.store = ModbusSequentialDataBlock(0, [0] * 65536)
        
        # Create standard context (HR and IR usually map to the same data in simple slaves,
        # or we can separate them. For this app, we'll map both to the same store for simplicity 
        # unless strict separation is needed. Mapping both ensures FC03 and FC04 work.)
        self.context = ModbusDeviceContext(
            di=None, co=None, hr=self.store, ir=self.store, # zero_mode=True remove checks
        )
        
        # Single slave context
        self.server_context = ModbusServerContext(devices=self.context, single=True)

    def update_register(self, address, value, data_type, endian='big'):
        """
        Updates the register at `address` with `value` converted according to `data_type`.
        Address is 1-based (modbus standard), converted to 0-based for pymodbus internally if needed,
        but ModbusSequentialDataBlock handles address offsets.
        Pymodbus usually expects 0-based address for the datablock, 
        so we need to be careful with the mapping from config (usually 1-based 40001 -> offset 0).
        
        Assumptions: 
        - Config uses standard Modbus addressing (e.g., 40001). 
        - We treat 40001 as offset 0, 30001 as offset 0 for Input Registers.
        - Simplified: We will subtract 40001 (or 30001) or just use the raw offset if provided in config.
        - BETTER APPROACH: Config should specify the REGISTER INDEX (e.g., 0, 1, 100). 
          Or if it specifies 40001, we subtract 40001. 
          Let's assume the config provides the raw register address requested by Master.
        """
        
        # Normalize address (Primitive logic: if > 40000 assume Holding Register offset)
        # For simplicity, we will trust the user config to provide the address the master will request.
        # But `ModbusSequentialDataBlock` is 0-indexed relative to its start.
        # If we initialize checking 0, then address 0 is the first one.
        # If Master requests 40001, in Modbus PDU it requests address 0.
        # So we should use 0-based offsets in our logic.
        
        # If user puts "40001" in config, we assume they mean offset 0.
        # If "1", we assume offset 1. This is ambiguous.
        # Convention: We'll convert 40001 -> 0, 30001 -> 0. 
        # If value < 30000, we treat it as direct index.
        
        register_idx = address
        if register_idx >= 40001:
            register_idx -= 40001
        elif register_idx >= 30001:
            register_idx -= 30001
        
        if register_idx < 0:
            logger.error(f"Invalid register address: {address}")
            return

        registers = self._convert_to_registers(value, data_type, endian)
        
        if registers:
            with self.lock:
                # ModbusSequentialDataBlock(0, ...) means 0-based indexing for us here.
                self.store.setValues(register_idx, registers)
                logger.debug(f"Updated Addr {register_idx} (Orig: {address}) with {registers}")

    def _convert_to_registers(self, value, data_type, endian):
        """
        Converts a value to a list of 16-bit registers (words).
        """
        try:
            if data_type.upper() == "U16":
                val = int(value)
                return [val & 0xFFFF]
            
            elif data_type.upper() == "S16":
                val = int(value)
                return [val & 0xFFFF] # Python handles signed representation in formatting, but for storage we just masking
                # Actually `struct` is safer for signed.
                # return list(struct.unpack('>H', struct.pack('>h', val)))

            elif data_type.upper() == "U32":
                val = int(value)
                # Pack as 4 bytes, then unpack as 2 shorts
                packed = struct.pack('>I' if endian == 'big' else '<I', val)
                return list(struct.unpack('>HH' if endian == 'big' else '<HH', packed))

            elif data_type.upper() == "S32":
                val = int(value)
                packed = struct.pack('>i' if endian == 'big' else '<i', val)
                return list(struct.unpack('>HH' if endian == 'big' else '<HH', packed))

            elif data_type.upper() == "FLOAT" or data_type.upper() == "FLOAT32":
                val = float(value)
                packed = struct.pack('>f' if endian == 'big' else '<f', val)
                return list(struct.unpack('>HH' if endian == 'big' else '<HH', packed))
            
            else:
                logger.error(f"Unknown data type: {data_type}")
                return None

        except Exception as e:
            logger.error(f"Error converting value {value} to {data_type}: {e}")
            return None

register_manager = RegisterManager()  # Global instance
