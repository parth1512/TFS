import pymodbus
import inspect
import pkgutil

print("pymodbus version:", pymodbus.__version__)

try:
    from pymodbus.transaction import ModbusRtuFramer
    print("Found in pymodbus.transaction")
except ImportError:
    print("Not found in pymodbus.transaction")

try:
    from pymodbus.framer.rtu_framer import ModbusRtuFramer
    print("Found in pymodbus.framer.rtu_framer")
except ImportError:
    print("Not found in pymodbus.framer.rtu_framer")

try:
    from pymodbus.framer import ModbusRtuFramer
    print("Found in pymodbus.framer")
except ImportError:
    print("Not found in pymodbus.framer")
