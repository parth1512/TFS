import pymodbus
import inspect

print("pymodbus version:", pymodbus.__version__)
print("pymodbus dir:", dir(pymodbus))

try:
    from pymodbus.device import ModbusDeviceIdentification
    print("Found in pymodbus.device")
except ImportError:
    print("Not found in pymodbus.device")

try:
    from pymodbus.server import ModbusDeviceIdentification
    print("Found in pymodbus.server")
except ImportError:
    print("Not found in pymodbus.server")

# Try to look for it recursively or in likely places
import pkgutil
print("Submodules:")
for importer, modname, ispkg in pkgutil.iter_modules(pymodbus.__path__):
    print(modname)
