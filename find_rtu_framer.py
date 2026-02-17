import pymodbus
import inspect
import pkgutil

print("pymodbus version:", pymodbus.__version__)

# Check if direct import works
try:
    from pymodbus import ModbusRtuFramer
    print("Found in pymodbus (top level)")
except ImportError:
    print("Not found in pymodbus (top level)")

# Inspect transaction
try:
    import pymodbus.transaction
    print("pymodbus.transaction members:", dir(pymodbus.transaction))
except ImportError:
    print("Could not import pymodbus.transaction")

# Inspect framer
try:
    import pymodbus.framer
    print("pymodbus.framer members:", dir(pymodbus.framer))
except ImportError:
    try:
        from pymodbus import framer
        print("pymodbus.framer members (via from):", dir(framer))
    except:
        print("Could not import pymodbus.framer")

