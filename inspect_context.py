from pymodbus.datastore import ModbusServerContext, ModbusDeviceContext, ModbusSequentialDataBlock
import inspect

print("ModbusServerContext signature:", inspect.signature(ModbusServerContext.__init__))

# Try to init
try:
    c = ModbusDeviceContext(hr=ModbusSequentialDataBlock(0, [0]*10))
    s = ModbusServerContext(slaves=c, single=True)
    print("ModbusServerContext init valid (classic)")
except Exception as e:
    print(f"ModbusServerContext init failed (classic): {e}")

try:
    c = ModbusDeviceContext(hr=ModbusSequentialDataBlock(0, [0]*10))
    # Maybe it takes 'slaves' as a dict, or maybe it's just 'slaves' kwarg?
    # Or maybe it's just positional?
    pass
except:
    pass
