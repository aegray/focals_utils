



import sys


import gatt
import time
import struct

input_char="53b2ad55-c810-4c75-8a25-e1883a081ef6"
input_devid = "013300f1-9242-f0b5-ca48-e6cbd1ee6172" # dev id, can't listen notification
input_unk = "e18210e2-415d-42af-b7ce-f789de42d888"


#[DA:56:38:78:F5:A7]    Characteristic [e18210e2-415d-42af-b7ce-f789de42d888]

loop_name='DA:56:38:78:F5:A7'


if len(sys.argv) > 1:
    loop_name = sys.argv[1].upper()


#loop_name='72:22:8a:8b:79:11'.upper() #] 72-22-8A-8B-79-11

manager = gatt.DeviceManager(adapter_name='hci0')

ts_last_key = 0
devts_last_key = 0

def get_time():
    return time.time_ns()

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("%s : connected : %s " % (get_time(), self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("%s : connect_fail : %s : %s"%(get_time(), self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("%s : disconnect : %s"%(get_time(), self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        print("%s : resolved_services : %s" % (get_time(), self.mac_address))
        for service in self.services:
            print("%s : available_service : %s : %s"%(get_time(), self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("%s : available_char : %s : %s : %s"%(get_time(), self.mac_address, service.uuid, characteristic.uuid))
                for descriptor in characteristic.descriptors:
                    try:
                        print("        [%s]\t\t\tDescriptor [%s]" % (self.mac_address, descriptor.uuid)) #, descriptor.read_value()))
                        #print("        [%s]\t\t\tDescriptor [%s] (%s)" % (self.mac_address, descriptor.uuid, descriptor.read_value()))
                    except:
                        pass

                if characteristic.uuid == input_char:
                    #pass
                    characteristic.enable_notifications()
                elif characteristic.uuid == input_devid:
                    res = characteristic.read_value()
                    vals = []
                    try:
                        for x in res:
                            vals.append(x)
                        print("%s : devid_read : %s : %s : %s : %s"%(get_time(), self.mac_address, service.uuid, characteristic.uuid, vals))
                    except:
                        pass
                    #characteristic.read_value()))
                elif characteristic.uuid == input_unk:
                    #pass
                    print("%s : unk_read : %s : %s : %s : %s"%(get_time(), self.mac_address, service.uuid, characteristic.uuid, characteristic.read_value()))


                #print(characteristic.uuid, characteristic.read_value())



    def descriptor_read_value_failed(self, descriptor, error):
        pass
    #print('descriptor_value_failed: ')

    def characteristic_enable_notifications_failed(self, characteristic, error):
        print("%s : enable_notifications_failed : %s : %s : %s"%(get_time(), self.mac_address, characteristic.uuid, error))

    def characteristic_enable_notifications_succeeded(self, characteristic):
        print("%s : enable_notifications_succeeded : %s : %s"%(get_time(), self.mac_address, characteristic.uuid))

    def characteristic_value_updated(self, characteristic, value):
        global ts_last_key
        global devts_last_key
        t = get_time()
        print("%s : char_updated : %s : %s : %s :"%(t, self.mac_address, characteristic.uuid, len(value)), value)
        if characteristic.uuid == input_char:
            le_vals = struct.unpack("<IBB", value)

            #le_vals2 = struct.unpack("<HHBB", value)

            tdelt_dev = le_vals[0] - devts_last_key
            tdelt_host = t - ts_last_key

            devts_last_key = le_vals[0]
            ts_last_key = t

            #be_vals = struct.unpack(">IBB", value)
            print("%s : key_event : %s : %s : %s / %s"%(t, self.mac_address, le_vals, tdelt_dev, tdelt_host))




device = AnyDevice(mac_address=loop_name.lower(), manager=manager)
device.connect()

manager.run()

# loop has 2 services with 4 characteristics total:
#[DA:56:38:78:F5:A7]  Service [39de08dc-624e-4d6f-8e42-e1adb7d92fe1]
#[DA:56:38:78:F5:A7]    Characteristic [013300f1-9242-f0b5-ca48-e6cbd1ee6172]
# read gives:
#  013300f1-9242-f0b5-ca48-e6cbd1ee6172 dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))

#[DA:56:38:78:F5:A7]    Characteristic [e18210e2-415d-42af-b7ce-f789de42d888]
# read gives nothing  (e18210e2-415d-42af-b7ce-f789de42d888 None)

#[DA:56:38:78:F5:A7]    Characteristic [53b2ad55-c810-4c75-8a25-e1883a081ef6]
# read gives:
#   53b2ad55-c810-4c75-8a25-e1883a081ef6 dbus.Array([dbus.Byte(55), dbus.Byte(115), dbus.Byte(29), dbus.Byte(1), dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y'))

#[DA:56:38:78:F5:A7]  Service [00001801-0000-1000-8000-00805f9b34fb]
#[DA:56:38:78:F5:A7]    Characteristic [00002a05-0000-1000-8000-00805f9b34fb]
# read gives nothing (00002a05-0000-1000-8000-00805f9b34fb None)

#1573337675061547065 : resolved_services : DA:56:38:78:F5:A7
#1573337675061571403 : available_service : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1
#1573337675061577253 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172
#1573337675264382064 : devid_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : [dbus.Byte(3), dbus.Byte(38), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(124), dbus.Byte(100), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)]
#1573337675264434670 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888
#1573337675264448206 : unk_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888 : None
#1573337675354460469 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#        [DA:56:38:78:F5:A7]                     Descriptor [00002902-0000-1000-8000-00805f9b34fb] (dbus.Array([dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y')))
#1573337675445010680 : available_service : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb
#1573337675445058241 : available_char : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb
#        [DA:56:38:78:F5:A7]                     Descriptor [00002902-0000-1000-8000-00805f9b34fb] (dbus.Array([dbus.Byte(2), dbus.Byte(0)], signature=dbus.Signature('y')))
#1573337675543243578 : char_updated : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : 13 : b'\x03&DD\xa1|d%\xa7\xc8\xabw|'
#1573337675625045893 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#


# keypresses are on char 53b2ad55-c810-4c75-8a25-e1883a081ef6
# it appears char update is 5 bytes:
#       timestamp(4) keymask isrepeat
#
#       timestamp is a 4 byte unsigned int (as far as I can tell) - stored little endian
#           on a random sampling of keypresses, comparing nanosecond time deltas in host to
#           "timestamp" in device gives:
#               Average multiplier to nanos:  640109.1964106214 (host_delta_ns / dev_delta)
#                       2.4159769438541765e-06 (dev_delta / host_delta_ns)
#
#       keymask (can be or'd together for multiple keys)
#           0x01 = click/center
#           0x02 = up
#           0x04 = down
#           0x08 = left
#           0x10 = right
#
#       isrepeat:
#           0x0 = for initial keydown or keyup
#           0x1 = when key is held down, if this is a "key still down event" that gets sent a couple times a second
#
#### I'm guessing that 013300f1-9242-f0b5-ca48-e6cbd1ee6172 is a device signature / id - this has come up with the same value every time i read it
# dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))
# 1573328895440030646 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))
# 1573328942922492729 : char_updated : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : 13 : b'\x076DD\xa1~h%\xa7\xc8\xabw|'
#1573326369.1595156 : char_updated : DA:56:38:78:F5:A7 :   013300f1-9242-f0b5-ca48-e6cbd1ee6172 :      b'\x076DD\xa1~h%\xa7\xc8\xabw|'
# 1573328947819608043 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : dbus.Array([dbus.Byte(183), dbus.Byte(21), dbus.Byte(123), dbus.Byte(1), dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y'))


#Enable notification failed:  013300f1-9242-f0b5-ca48-e6cbd1ee6172 Operation is not supported
#Enable notification failed:  e18210e2-415d-42af-b7ce-f789de42d888 Operation is not supported

# we can get notifications on the foollowing 2:
#Enable notification succeeded:  53b2ad55-c810-4c75-8a25-e1883a081ef6
#Enable notification succeeded:  00002a05-0000-1000-8000-00805f9b34fb
#       My best guess based on googling is 2a05 is service changed - which will tell you
#       when some bt service changes so you can do rediscovery - sort of doubt this one is
#       important

#Char updated:  013300f1-9242-f0b5-ca48-e6cbd1ee6172 b'\x076DD\xa1~h%\xa7\xc8\xabw|'
#       Semi guessing 013300f1 is battery
#Char updated:  53b2ad55-c810-4c75-8a25-e1883a081ef6 b'7s\x1d\x01\x00\x00'
#       Sure that this is the actual keypresses (you can see when stuff gets clicked)





#  raw dump:
#
#[DA:56:38:78:F5:A7] Resolved services
#[DA:56:38:78:F5:A7]  Service [39de08dc-624e-4d6f-8e42-e1adb7d92fe1]
#[DA:56:38:78:F5:A7]    Characteristic [013300f1-9242-f0b5-ca48-e6cbd1ee6172]
#013300f1-9242-f0b5-ca48-e6cbd1ee6172 dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))
#[DA:56:38:78:F5:A7]    Characteristic [e18210e2-415d-42af-b7ce-f789de42d888]
#e18210e2-415d-42af-b7ce-f789de42d888 None
#[DA:56:38:78:F5:A7]    Characteristic [53b2ad55-c810-4c75-8a25-e1883a081ef6]
#53b2ad55-c810-4c75-8a25-e1883a081ef6 dbus.Array([dbus.Byte(55), dbus.Byte(115), dbus.Byte(29), dbus.Byte(1), dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y'))
#[DA:56:38:78:F5:A7]  Service [00001801-0000-1000-8000-00805f9b34fb]
#[DA:56:38:78:F5:A7]    Characteristic [00002a05-0000-1000-8000-00805f9b34fb]
#00002a05-0000-1000-8000-00805f9b34fb None
#Enable notification failed:  013300f1-9242-f0b5-ca48-e6cbd1ee6172 Operation is not supported
#Char updated:  013300f1-9242-f0b5-ca48-e6cbd1ee6172 b'\x076DD\xa1~h%\xa7\xc8\xabw|'
#Enable notification failed:  e18210e2-415d-42af-b7ce-f789de42d888 Operation is not supported
#Enable notification succeeded:  53b2ad55-c810-4c75-8a25-e1883a081ef6
#Char updated:  53b2ad55-c810-4c75-8a25-e1883a081ef6 b'7s\x1d\x01\x00\x00'
#Enable notification succeeded:  00002a05-0000-1000-8000-00805f9b34fb
#
#



#
#1573327130.9314907 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'nBQ\x01\x01\x00'
#1573327131.1114945 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xc5CQ\x01\x01\x01'
#1573327131.3365586 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15EQ\x01\x01\x01'
#1573327131.5612767 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'UFQ\x01\x01\x01'
#1573327131.7414005 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95GQ\x01\x01\x01'
#1573327131.9215784 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5HQ\x01\x01\x01'
#1573327132.146374 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%JQ\x01\x01\x01'
#1573327132.3264403 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'eKQ\x01\x01\x01'
#1573327132.5504787 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x8eLQ\x01\x00\x00'

#1573326380.5382295 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb4\xf0>\x01\x10\x00'
#1573326380.6282048 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\xf1>\x01\x00\x00'


# dump of short pressing keys
# startup / connect
#1573326368.6425087 : resolved_services : DA:56:38:78:F5:A7
#1573326368.642538 : available_service : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1
#1573326368.6425447 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172
#1573326368.6425807 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))
#1573326368.7029905 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888
#1573326368.7030802 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888 : None
#1573326368.7925992 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#1573326368.7926943 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : dbus.Array([dbus.Byte(55), dbus.Byte(115), dbus.Byte(29), dbus.Byte(1), dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y'))
#1573326368.9727747 : available_service : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb
#1573326368.9728153 : available_char : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb
#1573326368.9729083 : char_read : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb : None
#1573326369.1593866 : enable_notifications_failed : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : Operation is not supported
#1573326369.1595156 : char_updated : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : b'\x076DD\xa1~h%\xa7\xc8\xabw|'
#1573326369.1595678 : enable_notifications_failed : DA:56:38:78:F5:A7 : e18210e2-415d-42af-b7ce-f789de42d888 : Operation is not supported
#1573326369.1596608 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#1573326369.1597304 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'7s\x1d\x01\x00\x00'
#1573326369.159789 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 00002a05-0000-1000-8000-00805f9b34fb
#
#
#
#
#
#
# right press - down and release quickly (appears to be a keydown, keyup event)
#1573326380.5382295 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb4\xf0>\x01\x10\x00'
#1573326380.6282048 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\xf1>\x01\x00\x00'
#1573326382.2036345 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x07\xfb>\x01\x10\x00'
#1573326382.2925532 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'z\xfb>\x01\x00\x00'
#1573326383.8684185 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x89\x05?\x01\x10\x00'
#1573326383.958567 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe4\x05?\x01\x00\x00'
#1573326385.7138538 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x0e\x11?\x01\x10\x00'
#1573326385.803592 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'l\x11?\x01\x00\x00'
#1573326388.2338045 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xca ?\x01\x10\x00'
#1573326388.2789 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x1a!?\x01\x00\x00'
#1573326389.9441414 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'k+?\x01\x10\x00'
#1573326390.033562 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xdc+?\x01\x00\x00'
#1573326392.553806 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x9d;?\x01\x10\x00'
#1573326392.598816 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b' <?\x01\x00\x00'
#
#
#
#
#
#
# up press - down and release quickly
#1573326413.2544355 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xff\xbc?\x01\x02\x00'
#1573326413.3895316 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x07\xbe?\x01\x00\x00'
#1573326414.379689 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'C\xc4?\x01\x02\x00'
#1573326414.5144806 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xdd\xc4?\x01\x00\x00'
#1573326415.8196545 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x05\xcd?\x01\x02\x00'
#1573326415.9096951 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb2\xcd?\x01\x00\x00'
#1573326417.0798542 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe3\xd4?\x01\x02\x00'
#1573326417.1696882 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'u\xd5?\x01\x00\x00'
#1573326418.4296887 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'v\xdd?\x01\x02\x00'
#1573326418.5194747 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5\xdd?\x01\x00\x00'
#1573326419.869866 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\xe6?\x01\x02\x00'
#1573326419.9148889 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xcd\xe6?\x01\x00\x00'
#1573326421.399874 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x05\xf0?\x01\x02\x00'
#1573326421.444829 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'Y\xf0?\x01\x00\x00'
#1573326422.8390481 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x00\xf9?\x01\x02\x00'
#1573326422.8847864 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'n\xf9?\x01\x00\x00'
#
#
#
#
#
#
#
#
#
#
#
#
#
# left press - down and release quickly
#1573326430.2652354 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b"M'@\x01\x08\x00"
#1573326430.3103848 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b"\xbc'@\x01\x00\x00"
#1573326431.4803042 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5.@\x01\x08\x00'
#1573326431.5251892 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'l/@\x01\x00\x00'
#1573326432.7854147 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\r7@\x01\x08\x00'
#1573326432.8741786 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x9e7@\x01\x00\x00'
#1573326434.0448208 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'0?@\x01\x08\x00'
#1573326434.1354432 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xab?@\x01\x00\x00'
#1573326435.5743241 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'~H@\x01\x08\x00'
#1573326435.665285 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x0eI@\x01\x00\x00'
#1573326436.9704456 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'yQ@\x01\x08\x00'
#1573326437.0595896 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x05R@\x01\x00\x00'
#1573326438.319416 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xdeY@\x01\x08\x00'
#1573326438.4103234 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'eZ@\x01\x00\x00'
#1573326439.6705341 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x16b@\x01\x08\x00'
#1573326439.7602835 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa4b@\x01\x00\x00'
#
#
#
#
#
#
#
#
# down press - down and release quickly
#1573326443.4056284 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa8y@\x01\x04\x00'
#1573326443.4506202 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe9y@\x01\x00\x00'
#1573326445.0248713 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x8e\x83@\x01\x04\x00'
#1573326445.0703194 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf8\x83@\x01\x00\x00'
#1573326446.465731 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x8e\x8c@\x01\x04\x00'
#1573326446.510534 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf5\x8c@\x01\x00\x00'
#1573326447.9056942 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xbc\x95@\x01\x04\x00'
#1573326447.995741 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x1e\x96@\x01\x00\x00'
#1573326449.3909948 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd6\x9e@\x01\x04\x00'
#1573326449.4352577 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'W\x9f@\x01\x00\x00'
#1573326450.7855754 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xcd\xa7@\x01\x04\x00'
#1573326450.875861 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x1e\xa8@\x01\x00\x00'
#1573326452.720772 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd7\xb3@\x01\x04\x00'
#1573326452.810821 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'6\xb4@\x01\x00\x00'
#1573326454.4749427 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x9e\xbe@\x01\x04\x00'
#1573326454.5199118 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x02\xbf@\x01\x00\x00'
#
#
#
#
#
#
#
#
#
# center / main click press - down and release quickly
#1573326458.931048 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa8\xda@\x01\x01\x00'
#1573326458.9761508 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe8\xda@\x01\x00\x00'
#1573326460.6412365 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'W\xe5@\x01\x01\x00'
#1573326460.686217 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'p\xe5@\x01\x00\x00'
#1573326462.3961933 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'Y\xf0@\x01\x01\x00'
#1573326462.4862905 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xae\xf0@\x01\x00\x00'
#1573326463.9712656 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'!\xfa@\x01\x01\x00'
#1573326464.0160441 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'g\xfa@\x01\x00\x00'
#1573326465.5012324 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x86\x03A\x01\x01\x00'
#1573326465.546126 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xfc\x03A\x01\x00\x00'
#1573326467.166399 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'/\x0eA\x01\x01\x00'
#1573326467.256241 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'|\x0eA\x01\x00\x00'
#1573326468.8315682 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'V\x18A\x01\x01\x00'
#1573326468.8761613 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xbf\x18A\x01\x00\x00'
#1573326470.4962304 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5"A\x01\x01\x00'
#1573326470.540674 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5#A\x01\x00\x00'
#
#


############## Long presses:
#
#1573327078.205795 : resolved_services : DA:56:38:78:F5:A7
#1573327078.2058246 : available_service : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1
#1573327078.2058487 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172
#1573327078.2058678 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))
#1573327078.2797472 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888
#1573327078.2797885 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888 : None
#1573327078.3701746 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#1573327078.370271 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : dbus.Array([dbus.Byte(53), dbus.Byte(35), dbus.Byte(65), dbus.Byte(1), dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y'))
#1573327078.550294 : available_service : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb
#1573327078.5503178 : available_char : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb
#1573327078.5504246 : char_read : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb : None
#1573327078.737855 : enable_notifications_failed : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : Operation is not supported
#1573327078.7381566 : char_updated : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : b'\x076DD\xa1~h%\xa7\xc8\xabw|'
#1573327078.7382932 : enable_notifications_failed : DA:56:38:78:F5:A7 : e18210e2-415d-42af-b7ce-f789de42d888 : Operation is not supported
#1573327078.7385073 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#1573327078.738713 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5#A\x01\x00\x00'
#1573327078.738925 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 00002a05-0000-1000-8000-00805f9b34fb
#
#
#
#
#
#
#1573327082.5554883 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x14\x14P\x01\x10\x00'
#1573327082.735772 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'V\x15P\x01\x10\x01'
#1573327082.9605794 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x9b\x16P\x01\x10\x01'
#1573327083.1405475 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf5\x17P\x01\x10\x01'
#1573327083.3656282 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'E\x19P\x01\x10\x01'
#1573327083.545725 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x85\x1aP\x01\x10\x01'
#1573327083.7699585 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xc5\x1bP\x01\x10\x01'
#1573327083.860446 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5\x1cP\x01\x00\x00'
#
#
#1573327087.50575 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x043P\x01\x10\x00'
#1573327087.6855567 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'F4P\x01\x10\x01'
#1573327087.9109066 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x8b5P\x01\x10\x01'
#1573327088.0906007 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe56P\x01\x10\x01'
#1573327088.3148918 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'58P\x01\x10\x01'
#1573327088.4962223 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'u9P\x01\x10\x01'
#1573327088.7207441 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb5:P\x01\x10\x01'
#1573327088.9005682 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf5;P\x01\x10\x01'
#1573327089.1257417 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'E=P\x01\x10\x01'
#1573327089.1705093 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x9f=P\x01\x00\x00'
#
#
#
#1573327092.7259338 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa6SP\x01\x10\x00'
#1573327092.950764 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x0cUP\x01\x10\x01'
#1573327093.1309674 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'eVP\x01\x10\x01'
#1573327093.3551557 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5WP\x01\x10\x01'
#1573327093.580716 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15YP\x01\x10\x01'
#1573327093.7607994 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'UZP\x01\x10\x01'
#1573327093.9856863 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5[P\x01\x10\x01'
#1573327094.1657476 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5\\P\x01\x10\x01'
#1573327094.3908403 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%^P\x01\x10\x01'
#1573327094.570598 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'e_P\x01\x10\x01'
#1573327094.6607616 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf1_P\x01\x00\x00'
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#1573327099.3851922 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'D}P\x01\x02\x00'
#1573327099.565732 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x85~P\x01\x02\x01'
#1573327099.7459743 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xc5\x7fP\x01\x02\x01'
#1573327099.971066 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x05\x81P\x01\x02\x01'
#1573327100.1500258 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'E\x82P\x01\x02\x01'
#1573327100.3761065 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95\x83P\x01\x02\x01'
#1573327100.5560803 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5\x84P\x01\x02\x01'
#1573327100.7809975 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15\x86P\x01\x02\x01'
#1573327100.960837 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\x87P\x01\x02\x01'
#1573327101.0959628 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5\x88P\x01\x00\x00'
#
#
#
#1573327103.5710046 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'j\x97P\x01\x02\x00'
#1573327103.7960973 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5\x98P\x01\x02\x01'
#1573327103.976069 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15\x9aP\x01\x02\x01'
#1573327104.155196 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\x9bP\x01\x02\x01'
#1573327104.3810704 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95\x9cP\x01\x02\x01'
#1573327104.5609093 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5\x9dP\x01\x02\x01'
#1573327104.785933 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%\x9fP\x01\x02\x01'
#1573327104.9659784 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'e\xa0P\x01\x02\x01'
#1573327105.1451383 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'|\xa1P\x01\x00\x00'
#
#1573327107.9360662 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf6\xb2P\x01\x02\x00'
#1573327108.1610956 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'6\xb4P\x01\x02\x01'
#1573327108.3860712 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x85\xb5P\x01\x02\x01'
#1573327108.5662642 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5\xb6P\x01\x02\x01'
#1573327108.7903106 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%\xb8P\x01\x02\x01'
#1573327108.9709935 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'e\xb9P\x01\x02\x01'
#1573327109.1961102 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb5\xbaP\x01\x02\x01'
#1573327109.3761096 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf5\xbbP\x01\x02\x01'
#1573327109.600965 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5\xbdP\x01\x02\x01'
#1573327109.7810688 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'u\xbeP\x01\x02\x01'
#1573327109.825994 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5\xbeP\x01\x00\x00'
#
#
#
#
#
#
#
#
#
#
#1573327112.9313073 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xed\xd1P\x01\x08\x00'
#1573327113.1559596 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\xd3P\x01\x08\x01'
#1573327113.336062 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95\xd4P\x01\x08\x01'
#1573327113.5161228 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5\xd5P\x01\x08\x01'
#1573327113.741083 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15\xd7P\x01\x08\x01'
#1573327113.9202619 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\xd8P\x01\x08\x01'
#1573327114.1454072 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5\xd9P\x01\x08\x01'
#1573327114.3251338 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5\xdaP\x01\x08\x01'
#1573327114.55139 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xed\xdbP\x01\x00\x00'
#
#
#
#
#1573327116.981173 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'e\xebP\x01\x08\x00'
#1573327117.2062716 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5\xecP\x01\x08\x01'
#1573327117.3862674 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5\xedP\x01\x08\x01'
#1573327117.5661542 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%\xefP\x01\x08\x01'
#1573327117.7914376 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'e\xf0P\x01\x08\x01'
#1573327117.971579 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5\xf1P\x01\x08\x01'
#1573327118.195998 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf5\xf2P\x01\x08\x01'
#1573327118.3762167 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5\xf4P\x01\x08\x01'
#1573327118.6013079 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'u\xf5P\x01\x08\x01'
#1573327118.7811804 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb5\xf6P\x01\x08\x01'
#1573327118.961314 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5\xf7P\x01\x00\x00'
#
#
#
#
#
#
#
#
#
#
#
#1573327122.5152912 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xfd\rQ\x01\x04\x00'
#1573327122.7412078 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'?\x0fQ\x01\x04\x01'
#1573327122.9214945 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95\x10Q\x01\x04\x01'
#1573327123.1461082 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x05\x12Q\x01\x04\x01'
#1573327123.3702357 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'E\x13Q\x01\x04\x01'
#1573327123.5510392 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x85\x14Q\x01\x04\x01'
#1573327123.776173 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5\x15Q\x01\x04\x01'
#1573327123.9561098 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15\x17Q\x01\x04\x01'
#1573327124.1811485 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'U\x18Q\x01\x04\x01'
#1573327124.3613005 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95\x19Q\x01\x04\x01'
#1573327124.5860722 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5\x1aQ\x01\x00\x00'
#
#1573327126.4761772 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb0&Q\x01\x04\x00'
#1573327126.6561615 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b"\xf5'Q\x01\x04\x01"
#1573327126.881255 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5)Q\x01\x04\x01'
#1573327127.0613816 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'u*Q\x01\x04\x01'
#1573327127.286425 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xc5+Q\x01\x04\x01'
#1573327127.4663641 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x05-Q\x01\x04\x01'
#1573327127.6915724 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'E.Q\x01\x04\x01'
#1573327127.8714335 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x85/Q\x01\x04\x01'
#1573327128.0963328 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf50Q\x01\x04\x01'
#1573327128.2313335 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x8c1Q\x01\x00\x00'
#
#
#
#
#
#1573327130.9314907 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'nBQ\x01\x01\x00'
#1573327131.1114945 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xc5CQ\x01\x01\x01'
#1573327131.3365586 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x15EQ\x01\x01\x01'
#1573327131.5612767 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'UFQ\x01\x01\x01'
#1573327131.7414005 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x95GQ\x01\x01\x01'
#1573327131.9215784 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xd5HQ\x01\x01\x01'
#1573327132.146374 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%JQ\x01\x01\x01'
#1573327132.3264403 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'eKQ\x01\x01\x01'
#1573327132.5504787 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\x8eLQ\x01\x00\x00'
#
#
#
#
#
#
#
#1573327135.025507 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'%\\Q\x01\x01\x00'
#1573327135.2064323 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'e]Q\x01\x01\x01'
#1573327135.4316394 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5^Q\x01\x01\x01'
#1573327135.611472 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xe5_Q\x01\x01\x01'
#1573327135.8363128 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'5aQ\x01\x01\x01'
#1573327136.0163753 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'ubQ\x01\x01\x01'
#1573327136.2414556 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xb5cQ\x01\x01\x01'
#1573327136.4213529 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xf5dQ\x01\x01\x01'
#1573327136.6463382 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'efQ\x01\x01\x01'
#1573327136.8716393 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'\xa5gQ\x01\x01\x01'
#1573327136.9614997 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : b'UhQ\x01\x00\x00'
#
#

### with decoding of structs:
#1573327516.9716907 : resolved_services : DA:56:38:78:F5:A7
#1573327516.9717212 : available_service : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1
#1573327516.971745 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172
#1573327516.9717627 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : dbus.Array([dbus.Byte(7), dbus.Byte(54), dbus.Byte(68), dbus.Byte(68), dbus.Byte(161), dbus.Byte(126), dbus.Byte(104), dbus.Byte(37), dbus.Byte(167), dbus.Byte(200), dbus.Byte(171), dbus.Byte(119), dbus.Byte(124)], signature=dbus.Signature('y'))
#1573327517.036657 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888
#1573327517.0367105 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : e18210e2-415d-42af-b7ce-f789de42d888 : None
#1573327517.1265867 : available_char : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#1573327517.126802 : char_read : DA:56:38:78:F5:A7 : 39de08dc-624e-4d6f-8e42-e1adb7d92fe1 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : dbus.Array([dbus.Byte(85), dbus.Byte(104), dbus.Byte(81), dbus.Byte(1), dbus.Byte(0), dbus.Byte(0)], signature=dbus.Signature('y'))
#1573327517.3066502 : available_service : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb
#1573327517.306771 : available_char : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb
#1573327517.3068638 : char_read : DA:56:38:78:F5:A7 : 00001801-0000-1000-8000-00805f9b34fb : 00002a05-0000-1000-8000-00805f9b34fb : None
#1573327517.494177 : enable_notifications_failed : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : Operation is not supported
#1573327517.494443 : char_updated : DA:56:38:78:F5:A7 : 013300f1-9242-f0b5-ca48-e6cbd1ee6172 : 13 : b'\x076DD\xa1~h%\xa7\xc8\xabw|'
#1573327517.4945717 : enable_notifications_failed : DA:56:38:78:F5:A7 : e18210e2-415d-42af-b7ce-f789de42d888 : Operation is not supported
#1573327517.4948094 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6
#1573327517.4949985 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'UhQ\x01\x00\x00'
#6
#1573327517.4949985 : key_event : DA:56:38:78:F5:A7 : (22112341, 0, 0) : (1432899841, 0, 0)
#1573327517.4952395 : enable_notifications_succeeded : DA:56:38:78:F5:A7 : 00002a05-0000-1000-8000-00805f9b34fb
#
#
#
#
#1573327524.102117 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x01\xdcZ\x01\x10\x00'
#6
#1573327524.102117 : key_event : DA:56:38:78:F5:A7 : (22731777, 16, 0) : (31218177, 16, 0)
#1573327524.192046 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'R\xdcZ\x01\x00\x00'
#6
#1573327524.192046 : key_event : DA:56:38:78:F5:A7 : (22731858, 0, 0) : (1390172673, 0, 0)
#1573327525.182265 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xa1\xe2Z\x01\x10\x00'
#6
#1573327525.182265 : key_event : DA:56:38:78:F5:A7 : (22733473, 16, 0) : (2715965953, 16, 0)
#1573327525.272037 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x0f\xe3Z\x01\x00\x00'
#6
#1573327525.272037 : key_event : DA:56:38:78:F5:A7 : (22733583, 0, 0) : (266557953, 0, 0)
#1573327526.127397 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x8c\xe8Z\x01\x10\x00'
#6
#1573327526.127397 : key_event : DA:56:38:78:F5:A7 : (22734988, 16, 0) : (2364037633, 16, 0)
#1573327526.2170684 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'(\xe9Z\x01\x00\x00'
#6
#1573327526.2170684 : key_event : DA:56:38:78:F5:A7 : (22735144, 0, 0) : (686381569, 0, 0)
#1573327527.0721226 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x86\xeeZ\x01\x10\x00'
#6
#1573327527.0721226 : key_event : DA:56:38:78:F5:A7 : (22736518, 16, 0) : (2263767553, 16, 0)
#1573327527.161999 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x14\xefZ\x01\x00\x00'
#6
#1573327527.161999 : key_event : DA:56:38:78:F5:A7 : (22736660, 0, 0) : (351230465, 0, 0)
#
#
#
#
#
#
#
#
#1573327551.8675847 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x8b\x89[\x01\x08\x00'
#6
#1573327551.8675847 : key_event : DA:56:38:78:F5:A7 : (22776203, 8, 0) : (2341034753, 8, 0)
#1573327551.9568424 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x01\x8a[\x01\x00\x00'
#6
#1573327551.9568424 : key_event : DA:56:38:78:F5:A7 : (22776321, 0, 0) : (25844481, 0, 0)
#1573327553.5777192 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x17\x94[\x01\x08\x00'
#6
#1573327553.5777192 : key_event : DA:56:38:78:F5:A7 : (22778903, 8, 0) : (395598593, 8, 0)
#1573327553.802852 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'`\x95[\x01\x08\x01'
#6
#1573327553.802852 : key_event : DA:56:38:78:F5:A7 : (22779232, 8, 1) : (1620400897, 8, 1)
#1573327554.0266163 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xc5\x96[\x01\x08\x01'
#6
#1573327554.0266163 : key_event : DA:56:38:78:F5:A7 : (22779589, 8, 1) : (3314965249, 8, 1)
#1573327554.2076275 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x05\x98[\x01\x08\x01'
#6
#1573327554.2076275 : key_event : DA:56:38:78:F5:A7 : (22779909, 8, 1) : (93870849, 8, 1)
#1573327554.3877409 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'E\x99[\x01\x08\x01'
#6
#1573327554.3877409 : key_event : DA:56:38:78:F5:A7 : (22780229, 8, 1) : (1167678209, 8, 1)
#1573327554.6127021 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x95\x9a[\x01\x08\x01'
#6
#1573327554.6127021 : key_event : DA:56:38:78:F5:A7 : (22780565, 8, 1) : (2509921025, 8, 1)
#1573327554.8376822 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xd5\x9b[\x01\x08\x01'
#6
#1573327554.8376822 : key_event : DA:56:38:78:F5:A7 : (22780885, 8, 1) : (3583728385, 8, 1)
#1573327555.0175965 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x15\x9d[\x01\x08\x01'
#6
#1573327555.0175965 : key_event : DA:56:38:78:F5:A7 : (22781205, 8, 1) : (362633985, 8, 1)
#1573327555.1971114 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'U\x9e[\x01\x08\x01'
#6
#1573327555.1971114 : key_event : DA:56:38:78:F5:A7 : (22781525, 8, 1) : (1436441345, 8, 1)
#1573327555.4226093 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xa5\x9f[\x01\x08\x01'
#6
#1573327555.4226093 : key_event : DA:56:38:78:F5:A7 : (22781861, 8, 1) : (2778684161, 8, 1)
#1573327555.6477854 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xe5\xa0[\x01\x08\x01'
#6
#1573327555.6477854 : key_event : DA:56:38:78:F5:A7 : (22782181, 8, 1) : (3852491521, 8, 1)
#1573327555.8276098 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'%\xa2[\x01\x08\x01'
#6
#1573327555.8276098 : key_event : DA:56:38:78:F5:A7 : (22782501, 8, 1) : (631397121, 8, 1)
#1573327556.0075383 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'e\xa3[\x01\x08\x01'
#6
#1573327556.0075383 : key_event : DA:56:38:78:F5:A7 : (22782821, 8, 1) : (1705204481, 8, 1)
#1573327556.2325883 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xb5\xa4[\x01\x08\x01'
#6
#1573327556.2325883 : key_event : DA:56:38:78:F5:A7 : (22783157, 8, 1) : (3047447297, 8, 1)
#1573327556.4126246 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xec\xa5[\x01\x00\x00'
#6
#1573327556.4126246 : key_event : DA:56:38:78:F5:A7 : (22783468, 0, 0) : (3970259713, 0, 0)
#1573327558.2569177 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'W\xb1[\x01\x04\x00'
#6
#1573327558.2569177 : key_event : DA:56:38:78:F5:A7 : (22786391, 4, 0) : (1471240961, 4, 0)
#1573327558.3471053 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x03\xb2[\x01\x00\x00'
#6
#1573327558.3471053 : key_event : DA:56:38:78:F5:A7 : (22786563, 0, 0) : (62020353, 0, 0)
#1573327559.6077616 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xde\xb9[\x01\x04\x00'
#6
#1573327559.6077616 : key_event : DA:56:38:78:F5:A7 : (22788574, 4, 0) : (3736689409, 4, 0)
#1573327559.7426429 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xa5\xba[\x01\x00\x00'
#6
#1573327559.7426429 : key_event : DA:56:38:78:F5:A7 : (22788773, 0, 0) : (2780453633, 0, 0)
#1573327560.5078185 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'H\xbf[\x01\x02\x00'
#6
#1573327560.5078185 : key_event : DA:56:38:78:F5:A7 : (22789960, 2, 0) : (1220500225, 2, 0)
#1573327560.642554 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b' \xc0[\x01\x00\x00'
#6
#1573327560.642554 : key_event : DA:56:38:78:F5:A7 : (22790176, 0, 0) : (549477121, 0, 0)
#1573327561.587654 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'&\xc6[\x01\x04\x00'
#6
#1573327561.587654 : key_event : DA:56:38:78:F5:A7 : (22791718, 4, 0) : (650533633, 4, 0)
#1573327561.677571 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xcb\xc6[\x01\x00\x00'
#6
#1573327561.677571 : key_event : DA:56:38:78:F5:A7 : (22791883, 0, 0) : (3418774273, 0, 0)
#1573327571.8030493 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x10\x06\\\x01\x01\x00'
#6
#1573327571.8030493 : key_event : DA:56:38:78:F5:A7 : (22808080, 1, 0) : (268852225, 1, 0)
#1573327572.0721157 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'e\x07\\\x01\x01\x01'
#6
#1573327572.0721157 : key_event : DA:56:38:78:F5:A7 : (22808421, 1, 1) : (1694981121, 1, 1)
#1573327572.2079666 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'h\x08\\\x01\x11\x00'
#6
#1573327572.2079666 : key_event : DA:56:38:78:F5:A7 : (22808680, 17, 0) : (1745378305, 17, 0)
#1573327572.2978098 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xf5\x08\\\x01\x10\x00'
#6
#1573327572.2978098 : key_event : DA:56:38:78:F5:A7 : (22808821, 16, 0) : (4110965761, 16, 0)
#1573327572.477885 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'5\n\\\x01\x10\x01'
#6
#1573327572.477885 : key_event : DA:56:38:78:F5:A7 : (22809141, 16, 1) : (889871361, 16, 1)
#1573327572.4784718 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'U\n\\\x01\x11\x00'
#6
#1573327572.4784718 : key_event : DA:56:38:78:F5:A7 : (22809173, 17, 0) : (1426742273, 17, 0)
#1573327572.7019873 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xa5\x0b\\\x01\x11\x01'
#6
#1573327572.7019873 : key_event : DA:56:38:78:F5:A7 : (22809509, 17, 1) : (2768985089, 17, 1)
#1573327572.927994 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xe5\x0c\\\x01\x11\x01'
#6
#1573327572.927994 : key_event : DA:56:38:78:F5:A7 : (22809829, 17, 1) : (3842792449, 17, 1)
#1573327573.10802 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'%\x0e\\\x01\x11\x01'
#6
#1573327573.10802 : key_event : DA:56:38:78:F5:A7 : (22810149, 17, 1) : (621698049, 17, 1)
#1573327573.2879379 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'e\x0f\\\x01\x11\x01'
#6
#1573327573.2879379 : key_event : DA:56:38:78:F5:A7 : (22810469, 17, 1) : (1695505409, 17, 1)
#1573327573.377861 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xf1\x0f\\\x01\x00\x00'
#6
#1573327573.377861 : key_event : DA:56:38:78:F5:A7 : (22810609, 0, 0) : (4044315649, 0, 0)
#1573327574.6830027 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xe0\x17\\\x01\x01\x00'
#6
#1573327574.6830027 : key_event : DA:56:38:78:F5:A7 : (22812640, 1, 0) : (3759627265, 1, 0)
#1573327574.8630686 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'%\x19\\\x01\x01\x01'
#6
#1573327574.8630686 : key_event : DA:56:38:78:F5:A7 : (22812965, 1, 1) : (622418945, 1, 1)
#1573327575.0878756 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'e\x1a\\\x01\x01\x01'
#6
#1573327575.0878756 : key_event : DA:56:38:78:F5:A7 : (22813285, 1, 1) : (1696226305, 1, 1)
#1573327575.0883868 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x85\x1a\\\x01\x11\x00'
#6
#1573327575.0883868 : key_event : DA:56:38:78:F5:A7 : (22813317, 17, 0) : (2233097217, 17, 0)
#1573327575.2679806 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xc5\x1b\\\x01\x11\x01'
#6
#1573327575.2679806 : key_event : DA:56:38:78:F5:A7 : (22813637, 17, 1) : (3306904577, 17, 1)
#1573327575.4927382 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x15\x1d\\\x01\x11\x01'
#6
#1573327575.4927382 : key_event : DA:56:38:78:F5:A7 : (22813973, 17, 1) : (354245633, 17, 1)
#1573327575.7178667 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'U\x1e\\\x01\x11\x01'
#6
#1573327575.7178667 : key_event : DA:56:38:78:F5:A7 : (22814293, 17, 1) : (1428052993, 17, 1)
#1573327575.8074992 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b',\x1f\\\x01\x01\x00'
#6
#1573327575.8074992 : key_event : DA:56:38:78:F5:A7 : (22814508, 1, 0) : (740252673, 1, 0)
#1573327576.077963 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\x95 \\\x01\x01\x01'
#6
#1573327576.077963 : key_event : DA:56:38:78:F5:A7 : (22814869, 1, 1) : (2501925889, 1, 1)
#1573327576.2570326 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xd5!\\\x01\x01\x01'
#6
#1573327576.2570326 : key_event : DA:56:38:78:F5:A7 : (22815189, 1, 1) : (3575733249, 1, 1)
#1573327576.3927839 : char_updated : DA:56:38:78:F5:A7 : 53b2ad55-c810-4c75-8a25-e1883a081ef6 : 6 : b'\xd2"\\\x01\x00\x00'
#6
#1573327576.3927839 : key_event : DA:56:38:78:F5:A7 : (22815442, 0, 0) : (3525467137, 0, 0)
#



