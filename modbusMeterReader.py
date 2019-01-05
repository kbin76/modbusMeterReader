#!/usr/bin/env python3

import sys
import argparse
import minimalmodbus
import json
import collections
import datetime, time
import platform

## Parse command line arguments
argparser = argparse.ArgumentParser( description='Read data points from Electricity Meter via Modbus and output as JSON')
argparser.add_argument( '--metername', default='meter1', help='Name to give the meter in the JSON output attribute "meterName"')
argparser.add_argument( '--jsontype', default='electricityMeterReading', help='Value to set "type" attribute to in the output JSON record')
argparser.add_argument( '-b', dest='baud', type=int, default=9600, help='Baudrate for RS-485 communication (default 9600)')
argparser.add_argument( '-s', dest='serialport', default='/dev/ttyAMA0', help='Serial device name (default /dev/ttyAMA0)')
argparser.add_argument( '-a', dest='address', type=int, default=1, help='Address (RS-485 Node Address) of meter (default=1)')
argparser.add_argument( '-t', dest='metertype', default="EASTRON_SDM630V2", help='Type of Energy meter (default=EASTRON_SDM630V2)')
args = argparser.parse_args()

minimalmodbus.BAUDRATE = args.baud
instrument = minimalmodbus.Instrument( args.serialport, args.address)

meter_database = {
	'EASTRON_SDM630V2': {
		'name': 'Eastron SDM630V2',
		'data_points': [
			{ 'modbus_addr': 0x00, 'name': 'L1_V', 'description': "L1 Line to Neutral (V)", 'type': 'float' },
			{ 'modbus_addr': 0x02, 'name': 'L2_V', 'description': "L2 Line to Neutral (V)", 'type': 'float' },
			{ 'modbus_addr': 0x04, 'name': 'L3_V', 'description': "L3 Line to Neutral (V)", 'type': 'float' },

			{ 'modbus_addr': 0xC8, 'name': 'L1L2_V', 'description': "L1 Line to L2 (V)", 'type': 'float' },
			{ 'modbus_addr': 0xCA, 'name': 'L2L3_V', 'description': "L2 Line to L3 (V)", 'type': 'float' },
			{ 'modbus_addr': 0xCC, 'name': 'L3L1_V', 'description': "L3 Line to L1 (V)", 'type': 'float' },

			{ 'modbus_addr': 0x06, 'name': 'L1_A', 'description': "L1 Current (A)", 'type': 'float' },
			{ 'modbus_addr': 0x08, 'name': 'L2_A', 'description': "L2 Current (A)", 'type': 'float' },
			{ 'modbus_addr': 0x0A, 'name': 'L3_A', 'description': "L3 Current (A)", 'type': 'float' },
			{ 'modbus_addr': 0xE0, 'name': 'N_A', 'description': "Neutral Current (A)", 'type': 'float' },

			{ 'modbus_addr': 0x0C, 'name': 'L1_W', 'description': "L1 Power (W)", 'type': 'float' },
			{ 'modbus_addr': 0x0E, 'name': 'L2_W', 'description': "L2 Power (W)", 'type': 'float' },
			{ 'modbus_addr': 0x10, 'name': 'L3_W', 'description': "L3 Power (W)", 'type': 'float' },

			{ 'modbus_addr': 0x12, 'name': 'L1_VA', 'description': "L1 Volt Amps (VA)", 'type': 'float' },
			{ 'modbus_addr': 0x14, 'name': 'L2_VA', 'description': "L2 Volt Amps (VA)", 'type': 'float' },
			{ 'modbus_addr': 0x16, 'name': 'L3_VA', 'description': "L3 Volt Amps (VA)", 'type': 'float' },

			{ 'modbus_addr': 0x34, 'name': 'Tot_W', 'description': "Total System Power (W)", 'type': 'float' },
			{ 'modbus_addr': 0x38, 'name': 'Tot_VA', 'description': "Total System Volt Amps (VA)", 'type': 'float' },
			{ 'modbus_addr': 0x0156, 'name': "Tot_kWh", 'description': "Total Energy (kWh)", 'type': 'float' },
			{ 'modbus_addr': 0x46, 'name': 'LineFrequence_Hz', 'description': "Line frequency (Hz)", 'type': 'float' },

			{ 'modbus_addr': 0x48, 'name': 'EnergyImported_kWh', 'description': "Energy Imported Accumulated (kWh)", 'type': 'float' },
			{ 'modbus_addr': 0x4A, 'name': 'EnergyExported_kWh', 'description': "Energy Exported Accumulated (kWh)", 'type': 'float' },

			{ 'modbus_addr': 0x54, 'name': 'N_MAX_A', 'description': "Neutral Maximum Current (A)", 'type': 'float' },
			{ 'modbus_addr': 0x0108, 'name': 'L1_MAX_A', 'description': "L1 Maximum Current (A)", 'type': 'float' },
			{ 'modbus_addr': 0x010A, 'name': 'L2_MAX_A', 'description': "L2 Maximum Current (A)", 'type': 'float' },
			{ 'modbus_addr': 0x010C, 'name': 'L3_MAX_A', 'description': "L3 Maximum Current (A)", 'type': 'float' }
		]	
	}
}

if not args.metertype in meter_database:
	print("ERROR: Unknown meter type '" + args.metertype + "', exiting", file=sys.stderr)
	sys.exit(-1)
meter = meter_database[args.metertype]

result = collections.OrderedDict()

## Add Metername and type
result['type'] = args.jsontype
result['meterName'] = args.metername
result['meterType'] = meter['name']
result['collector'] = sys.argv[0] + ", hostname=" + platform.node() + ", serialport=" + args.serialport + ", RS485_addr=" + str(args.address)

## Add Timestamp
result['ts'] = datetime.datetime.utcnow().isoformat() + "Z"
utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
result['ts_local'] = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

## Read all datapoints
for dp in meter['data_points']:
	if dp['type'] == "float":
		value = instrument.read_float( dp['modbus_addr'], functioncode=4, numberOfRegisters=2)
	else:
		value = "UNSUPPORTED_DATA_TYPE"
	#result.append({})
	result[dp['name']] = value

## Dump result to STDOUT
print( json.dumps(result))


