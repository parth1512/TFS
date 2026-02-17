try:
    from pymodbus.datastore import ModbusSlaveContext
    print("Direct import worked (unexpected)")
except ImportError:
    print("Direct import failed")

try:
    from pymodbus.datastore.context import ModbusSlaveContext
    print("Import from .context worked")
except ImportError:
    print("Import from .context failed")

try:
    from pymodbus.datastore import ModbusServerContext
    print("ModbusServerContext direct import worked")
except ImportError:
    print("ModbusServerContext direct import failed")
