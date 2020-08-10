from bluepy.btle import Scanner, DefaultDelegate
import sys 
# Where in the config to look for the name, and the name to search for
BLIND_AD_TYPE_NAME=9
BLIND_NAME="iTAG"
SCAN_TIME = 10.0

if __name__ == "__main__":
    scanner = Scanner()
    print("Scanning for devices...")
    devices = scanner.scan(SCAN_TIME)
    blindaddrs = []
    print("\nDevices found:")
    for dev in scanner.getDevices():
        print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
           print("  %s = %s" % (desc, value))
        if dev.getValueText(BLIND_AD_TYPE_NAME) == BLIND_NAME:
            blindaddrs.append(dev.addr)

    if len(blindaddrs) > 0:
        print("\nButtons found:")
        for i, addr in enumerate(blindaddrs):
            print(str(i) + ": " + addr)
    else:
        print("No blinds detected. They may be off, or even in a connected state")
        print("Try resetting the blind and ensuring any connected app has disconnected from the blind.")
        sys.exit(-1)

