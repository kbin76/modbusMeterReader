# modbusMeterReader
Python script for fetching readings from Energy Meters over Modbus protocol (running over RS-485 electrical serial line)

Currently only Eastron SDM630V2 energy meter is supported.

Also includes bash script that publishes output from python script to MQTT server.


## Pre-requisites

 - minimalmodbus (Python Module), "pip3 install minimalmodbus"
 - pyserial (Python Module, used by minimalmodbus), "pip3 install pyserial"


## Hardware

This is currently tested on a Raspberry Pi V2 using the "Zihatec RS422/RS845 Raspberry Pi Hat" that can be bought here: (https://www.hwhardsoft.de/)


## Example of usage

```
pi@host1:~/modbusMeterReader $ ./modbusMeterReader.py | jq .
{
  "type": "electricityMeterReading",
  "meterName": "meter1",
  "meterType": "Eastron SDM630V2",
  "collector": "./modbusMeterReader.py, hostname=host1, serialport=/dev/ttyAMA0, RS485_addr=1",
  "ts": "2019-01-05T17:00:09.446251Z",
  "ts_local": "2019-01-05T18:00:09.446568+01:00",
  "L1_V": 234.1771697998047,
  "L2_V": 0,
  "L3_V": 0,
  "L1L2_V": 234.19248962402344,
  "L2L3_V": 0,
  "L3L1_V": 234.18356323242188,
  "L1_A": 0.11964401602745056,
  "L2_A": 0,
  "L3_A": 0,
  "N_A": 0.12096608430147171,
  "L1_W": 25.85260581970215,
  "L2_W": 0,
  "L3_W": 0,
  "L1_VA": 27.197898864746094,
  "L2_VA": 0,
  "L3_VA": 0,
  "Tot_W": 26.136699676513672,
  "Tot_VA": 27.56019401550293,
  "Tot_kWh": 0.132999986410141,
  "LineFrequence_Hz": 49.929725646972656,
  "EnergyImported_kWh": 0.132999986410141,
  "EnergyExported_kWh": 0,
  "N_MAX_A": 24.923120498657227,
  "L1_MAX_A": 0.12036865204572678,
  "L2_MAX_A": 0,
  "L3_MAX_A": 0
}


pi@host1:~/modbusMeterReader $ ./modbusMeterReaderMQTT.sh --mqtt-hostname host2 --mqtt-topic 'energy/meter1' --metername 'meter1' -s /dev/ttyAMA0
*** Success!

```



## Command line arguments
```
usage: modbusMeterReader.py [-h] [--metername METERNAME] [--jsontype JSONTYPE]
                            [-b BAUD] [-s SERIALPORT] [-a ADDRESS]
                            [-t METERTYPE]

Read data points from Electricity Meter via Modbus and output as JSON

optional arguments:
  -h, --help            show this help message and exit
  --metername METERNAME
                        Name to give the meter in the JSON output attribute
                        "meterName"
  --jsontype JSONTYPE   Value to set "type" attribute to in the output JSON
                        record
  -b BAUD               Baudrate for RS-485 communication (default 9600)
  -s SERIALPORT         Serial device name (default /dev/ttyAMA0)
  -a ADDRESS            Address (RS-485 Node Address) of meter (default=1)
  -t METERTYPE          Type of Energy meter (default=EASTRON_SDM630V2)

```
