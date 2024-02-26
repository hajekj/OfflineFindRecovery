import asyncio
import logging
from datetime import datetime
import csv
import os

from scanner import OfflineFindingScanner

logging.basicConfig(level=logging.INFO)

pubkeys = []

def calculate_ble_distance(RSSI_at1m, RSSI, n):
    """
    Calculate the distance between a BLE transmitter and receiver using RSSI.
    
    Parameters:
    - RSSI_at1m: The RSSI value measured at 1 meter from the transmitter.
    - RSSI: The measured RSSI value at the receiver.
    - n: The path loss exponent.
    
    Returns:
    - The estimated distance in meters.
    """
    distance = 10 ** ((RSSI_at1m - RSSI) / (10 * n))
    return distance

class CSVWriter():

    filename = None
    fp = None
    writer = None

    def __init__(self, filename):
        self.filename = filename
        self.fp = open(self.filename, 'w', encoding='utf8')
        self.writer = csv.writer(self.fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')

    def close(self):
        self.fp.close()

    def write(self, *args):
        self.writer.writerow(args)

    def size(self):
        return os.path.getsize(self.filename)

    def fname(self):
        return self.filename

async def scan() -> None:
    scanner = await OfflineFindingScanner.create()

    file = open('discovery-keys.csv', "r")
    csvreader = csv.reader(file, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
    for row in csvreader:
        pubkeys.append(row[1])
    file.close()

    print("Scanning for FindMy-devices...")
    print()
    mycsv = CSVWriter('discovery-output.csv')

    RSSI_at1m = -52
    pathLossExponent = 2.0

    async for device in scanner.scan_for(2 * 60, extend_timeout=True):
        if device.status == 0:
            distance = calculate_ble_distance(RSSI_at1m, device.additional_data.get('rssi'), pathLossExponent)
            mycsv.write(device.mac_address,str(datetime.utcnow()),device.adv_key_b64,device.additional_data.get('rssi'),distance)

            if  device.adv_key_b64 in pubkeys:
                distanceStr = "Distance"
                print(f"Device - {device.mac_address}")
                print(f"  Time:         {datetime.utcnow()}")
                print(f"  Public key:   {device.adv_key_b64}")
                print(f"  Lookup key:   {device.hashed_adv_key_b64}")
                print(f"  Status byte:  {device.status:x}")
                print(f"  Hint byte:    {device.hint:x}")
                print("  Extra data:")
                print(f"    {distanceStr:20}: {distance}")
                for k, v in sorted(device.additional_data.items()):
                    print(f"    {k:20}: {v}")
                print()
            # else:
            #     print(f"Device - {device.mac_address}")
            #     print(f"  Time:         {datetime.utcnow()}")
            #     print(f"  Public key:   {device.adv_key_b64}")
            #     for k, v in sorted(device.additional_data.items()):
            #         print(f"    {k:20}: {v}")
        # else:
        #     print(f"Device - {device.mac_address}")
        #     print(f"  Time:         {datetime.utcnow()}")
        #     print(f"  Public key:   {device.adv_key_b64}")
        #     print(f"  Status byte:  {device.status:x}")
        #     for k, v in sorted(device.additional_data.items()):
        #         print(f"    {k:20}: {v}")

    mycsv.close()
    print("Closing")

if __name__ == "__main__":
    asyncio.run(scan())
