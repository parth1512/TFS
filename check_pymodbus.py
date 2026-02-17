import pymodbus.datastore
import inspect

print("pymodbus.datastore members:")
print(dir(pymodbus.datastore))

try:
    from pymodbus.datastore import ModbusSlaveContext
    print("ModbusSlaveContext found in pymodbus.datastore")
except ImportError:
    print("ModbusSlaveContext NOT found in pymodbus.datastore")

try:
    import pymodbus.server
    print("pymodbus.server members (partial):")
    print(dir(pymodbus.server))
except:
    pass
