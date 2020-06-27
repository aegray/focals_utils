import sys
import bluetooth
from bluetooth.ble import DiscoveryService


loop_name='DA:56:38:78:F5:A7'

#focals_addr = '00:00:00:87:E7:D9'
focals_addr = '00:00:00:C1:B2:D2'
#87:E7:D9'
focals_name = 'Focals - 00YE'




#focals_name='Focals-00YE'

if sys.argv[1] == 'd':
    service = DiscoveryService()
    devices = service.discover(2)

    for k, v in devices.items():
        print(k, v) #, bluetooth.lookup_name(k))

        if v == focals_name:
            print("FOUND: ", k, v, k == focals_addr)

elif sys.argv[1] == 's':

    services = bluetooth.find_service(address=focals_addr)

    for svc in services:
        print(svc)
#
#    services = bluetooth.find_service(address=loop_name)
#
#    for svc in services:
#        print(svc)
#

elif sys.argv[1] == 'c':

    #
    #private static final UUID KONA_BLUETOOTH_SERVICE_RECORD_UUID = UUID.fromString("00001101-0000-1000-8000-00805f9b34fb");

    services = bluetooth.find_service(address=focals_addr, uuid="00001101-0000-1000-8000-00805f9b34fb")
    #address=focals_addr)



    if len(services) == 0:
        print("Nothing found")
    else:
        print("Found service: ", services[0])
        print("Connecting")
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((services[0]['host'], services[0]['port']))
        print("Connected")

        while True:
            r = sock.recv(255)
            if not r:
                break
            print(r)

        print("Recvdone")
        sock.close()




#for svc in services:
#    print(svc)






#
#{'protocol': None, 'name': None, 'service-id': None, 'profiles': [], 'service-classes': ['1200'], 'host': '00:00:00:87:E7:D9', 'provider': None, 'port': None, 'description': None}
#{'protocol': 'L2CAP', 'name': 'Generic Access Profile', 'service-id': None, 'profiles': [], 'service-classes': ['1800'], 'host': '00:00:00:87:E7:D9', 'provider': 'BlueZ for Android', 'port': 31, 'description': None}
#{'protocol': 'L2CAP', 'name': 'Device Information Service', 'service-id': None, 'profiles': [], 'service-classes': ['180A'], 'host': '00:00:00:87:E7:D9', 'provider': 'BlueZ for Android', 'port': 31, 'description': None}
#{'protocol': 'L2CAP', 'name': 'Generic Attribute Profile', 'service-id': None, 'profiles': [], 'service-classes': ['1801'], 'host': '00:00:00:87:E7:D9', 'provider': 'BlueZ for Android', 'port': 31, 'description': None}
#{'protocol': 'RFCOMM', 'name': 'Focals SPP Service', 'service-id': None, 'profiles': [], 'service-classes': ['1101', '00000000-DECA-FADE-DECA-DEAFDECACAFF'], 'host': '00:00:00:87:E7:D9', 'provider': None, 'port': 1, 'description': None}
#
#private static final UUID KONA_BLUETOOTH_SERVICE_RECORD_UUID = UUID.fromString("00001101-0000-1000-8000-00805f9b34fb");
#for k, v in devices.items():
#    print(k, v) #, bluetooth.lookup_name(k))
#

#import bluetooth
#
#nearby = bluetooth.discover_devices(lookup_names=True)
#
#for bdaddr in nearby:
#    print(bdaddr)
#    #print(bluetooth.lookup_name(bdaddr))
#
