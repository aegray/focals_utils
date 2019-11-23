#!/usr/bin/env python3

import os
import time
import threading
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import struct

import array
from gi.repository import GObject, GLib

from pynput.keyboard import Key, Listener


#try:
#  from gi.repository import GObject, GLib
#except ImportError:
#  import gobject as GObject, GLib
import sys


from random import randint

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


input_char="53b2ad55-c810-4c75-8a25-e1883a081ef6"
input_devid = "013300f1-9242-f0b5-ca48-e6cbd1ee6172" # dev id, can't listen notification
input_unk = "e18210e2-415d-42af-b7ce-f789de42d888"



# actual thing has:
# 1800 Generic acess / primary service
# DEVICE name: UUID: 00002A00-0000-1000-8000-00805F9B34FB (READ)
# APPEARANCE UUID:  00002A01-0000-1000-8000-00805F9B34FB (READ)
# PERIPHERAL PRIVACY FLAG UUID:  00002A02-0000-1000-8000-00805F9B34FB (READ, WRITE), WRITE REQUEST
# PERIPHERAL PREFERRED CONNECTION PARAMTERS UUID:  00002A04-0000-1000-8000-00805F9B34FB (READ)

# 1801 Generic attribute / primary service
# SERVICE CHANGED UUID:  00002A05-0000-1000-8000-00805F9B34FB (INDICATE)
#   Descriptor: Client Characteristic Configuration UUID: 0x2902

# 180F Battery Service / primary service
# BATTERY LEVEL UUID: 00002A19-0000-1000-8000-00805F9B34FB (READ,NOTIFY)
#   Descriptor: Client Characteristic Configuration UUID: 0x2902

# CUSTOM SERVICE: 39DE08DC-624E-4D6F-8E42-E1ADB7D92FE1
#   CUSTOM CHARACTERISTIC UUID: 53B2AD55-C810-4C75-8A25-E1883A081EF6 (READ, NOTIFY)
#    Descriptor: Client char 0x2902
#   CUSTOM CHARACTERISTIC UUID: E18210E2-415D-42AF-B7CE-F789DE42D888 (WRITE), WRITE REQUEST
#   CUSTOM CHARACTERISTIC UUID: 013300F1-9242-F0B5-CA48-E6CBD1EE6172 (READ, WRITE), WRITE REQUEST
#

class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(FocalsLoopMainService(bus, 0))
        self.add_service(BatteryService(bus, 1))
        #self.add_service(FocalsLoopGenericSvcChangedService(bus, 1))

    def send_keys(self, code, is_rpt):
        print("Notifying Key: ", code, is_rpt)
        self.services[0].send_keys(code, is_rpt)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()



class FocalsLoopMainService(Service):
    SVC_UUID = '39de08dc-624e-4d6f-8e42-e1adb7d92fe1'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SVC_UUID, True)

        self.add_characteristic(FocalsLoopDevIdChrc(bus, 0, self))
        self.add_characteristic(FocalsLoopUnkChrc(bus, 1, self))
        self.add_characteristic(FocalsLoopInputChrc(bus, 2, self))

    def send_keys(self, keycode, is_rpt):
        self.characteristics[-1].send_keys(keycode, is_rpt)



class FocalsLoopGenericSvcChangedService(Service):
    SVC_UUID = '00001801-0000-1000-8000-00805f9b34fb'


    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SVC_UUID, True)

        self.add_characteristic(FocalsLoopServiceChangedChrc(bus, 0, self))

class BatteryService(Service):
    """
    Fake Battery service that emulates a draining battery.

    """
    SVC_UUID = '180f'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SVC_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))

class BatteryLevelCharacteristic(Characteristic):
    """
    Fake Battery Level characteristic. The battery level is drained by 2 points
    every 5 seconds.

    """
    CHRC_UUID = '2a19'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'notify'],
                service)
        self.notifying = False
        self.battery_lvl = 100
        #GObject.timeout_add(5000, self.drain_battery)

    def notify_battery_level(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': [dbus.Byte(self.battery_lvl)] }, [])

    #def drain_battery(self):
    #    if not self.notifying:
    #        return True
    #    if self.battery_lvl > 0:
    #        self.battery_lvl -= 2
    #        if self.battery_lvl < 0:
    #            self.battery_lvl = 0
    #    print('Battery Level drained: ' + repr(self.battery_lvl))
    #    self.notify_battery_level()
    #    return True

    def ReadValue(self, options):
        print('Battery Level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False



def get_loop_time():
    return int(time.time_ns() / 640109.0)


start_ticks = None

def make_key_press(keymask, is_repeat):
    global start_ticks
    is_repeat = 1 if is_repeat else 0
    t = get_loop_time()

    if start_ticks is None:
        start_ticks = t - 1000

    t = t - start_ticks

    value = []
    value.append(dbus.Byte(t & 0xff))
    value.append(dbus.Byte((t >> 8) & 0xff))
    value.append(dbus.Byte((t >> 16) & 0xff))
    value.append(dbus.Byte((t >> 24) & 0xff))

    value.append(dbus.Byte(keymask))
    value.append(dbus.Byte(is_repeat))
    return value
    #value.append(dbus.Byte(0x06))
    #return struct.pack("<IBB", t, keymask, is_repeat)


class FocalsLoopInputChrc(Characteristic):
    CHRC_UUID = '53b2ad55-c810-4c75-8a25-e1883a081ef6'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write', 'notify'],
                service)

        self.last_key_press = make_key_press(0x00, 0x0)
        self.notifying = False

    def send_keys(self, keycode, is_rpt):
        self.last_key_press = make_key_press(keycode, is_rpt)
        print("SENDING KEYS: ", keycode, is_rpt, self.last_key_press)
        self.notify_clients()

    def StartNotify(self):
        print("%s : StartNotify"%(self))
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True


    def StopNotify(self):
        print("%s : StopNotify"%(self))
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False

    def notify_clients(self):
        ival = (self.last_key_press[3] << 24) + (self.last_key_press[2] << 16) + (self.last_key_press[1] << 8) + self.last_key_press[0]

        #le_vals = struct.unpack("<IBB", self.last_key_press)
        print("Notifying: %d : %x : %x"%( ival, int(self.last_key_press[4]), int(self.last_key_press[5]))) #le_vals)
        self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': self.last_key_press }, [])

    def on_key(self, keymask, is_repeat):
        self.last_key_press = make_key_press(keymask, is_repeat)
        self.notify_clients()

    def ReadValue(self, options):
        print("%s : ReadValue"%(self), options)
        return [ 0x01 ]


    def WriteValue(self, value, options):
        print("%s : WriteValue"%(self), value, options)



class FocalsLoopDevIdChrc(Characteristic):
    CHRC_UUID = '013300f1-9242-f0b5-ca48-e6cbd1ee6172'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['notify', 'read', 'write'],
                service)

        self._value = [
                dbus.Byte(7),
                dbus.Byte(54),
                dbus.Byte(68),
                dbus.Byte(68),
                dbus.Byte(161),
                dbus.Byte(126),
                dbus.Byte(104),
                dbus.Byte(37),
                dbus.Byte(167),
                dbus.Byte(200),
                dbus.Byte(171),
                dbus.Byte(119),
                dbus.Byte(124)
            ]
        #, signature=dbus.Signature('y'))

    def StartNotify(self):
        print("%s : StartNotify"%(self))

    def StopNotify(self):
        print("%s : StopNotify"%(self))

    def ReadValue(self, options):
        print("%s : ReadValue"%(self), options)
        return self._value

    def WriteValue(self, value, options):
        print("%s : WriteValue"%(self), value, options)


class FocalsLoopUnkChrc(Characteristic):
    CHRC_UUID = 'e18210e2-415d-42af-b7ce-f789de42d888'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['notify', 'read', 'write'],
                service)


    def StartNotify(self):
        print("%s : StartNotify"%(self))

    def StopNotify(self):
        print("%s : StopNotify"%(self))

    def ReadValue(self, options):
        print("%s : ReadValue"%(self), options)
        return None
        #return self._value

    def WriteValue(self, value, options):
        print("%s : WriteValue"%(self), value, options)



class FocalsLoopServiceChangedChrc(Characteristic):
    CHRC_UUID = '00002a05-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['notify', 'read', 'write'],
                service)

    def StartNotify(self):
        print("%s : StartNotify"%(self))

    def StopNotify(self):
        print("%s : StopNotify"%(self))

    def ReadValue(self, options):
        print("%s : ReadValue"%(self), options)
        return None

    def WriteValue(self, value, options):
        print("%s : WriteValue"%(self), value, options)


#
#
#class TestSecureCharacteristic(Characteristic):
#    """
#    Dummy test characteristic requiring secure connection.
#
#    """
#    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef5'
#
#    def __init__(self, bus, index, service):
#        Characteristic.__init__(
#                self, bus, index,
#                self.TEST_CHRC_UUID,
#                ['secure-read', 'secure-write'],
#                service)
#        self.value = []
#        self.add_descriptor(TestSecureDescriptor(bus, 2, self))
#        self.add_descriptor(
#                CharacteristicUserDescriptionDescriptor(bus, 3, self))
#
#    def ReadValue(self, options):
#        print('TestSecureCharacteristic Read: ' + repr(self.value))
#        return self.value
#
#    def WriteValue(self, value, options):
#        print('TestSecureCharacteristic Write: ' + repr(value))
#        self.value = value
#
#
#class TestSecureDescriptor(Descriptor):
#    """
#    Dummy test descriptor requiring secure connection. Returns a static value.
#
#    """
#    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef6'
#
#    def __init__(self, bus, index, characteristic):
#        Descriptor.__init__(
#                self, bus, index,
#                self.TEST_DESC_UUID,
#                ['secure-read', 'secure-write'],
#                characteristic)
#
#    def ReadValue(self, options):
#        return [
#                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
#        ]

def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


class LoopInputMapper:
    def __init__(self):
        self.keysdown = 0x0
        self.mapping = {
                Key.enter : 0x1,
                Key.up : 0x2,
                Key.down : 0x4,
                Key.left : 0x8,
                Key.right : 0x10
        }

    def pressed(self, code):
        if code in self.mapping:
            newcode = self.keysdown | self.mapping[code]
            if newcode == self.keysdown:
                # repeat
                return (self.keysdown, 1)
            else:
                self.keysdown = newcode
                return (self.keysdown, 0)

        return None


    def released(self, code):
        if code in self.mapping:
            newcode = self.keysdown & (~(self.mapping[code]))
            print("Rel: ", code, self.mapping[code], self.keysdown, newcode)
            if newcode == self.keysdown:
                return None
            else:
                self.keysdown = newcode
                return (self.keysdown, 0)

        return None



def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)

    mainloop = GObject.MainLoop()

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=register_app_error_cb)


    input_mapper = LoopInputMapper()

    # force advertisement of the main uuid
    os.system("sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 06 11 07 E1 2F D9 B7 AD E1 42 8E 6F 4D 4E 62 DC 08 DE 39 00 00 00 00 00 00 00 00 C8 00")
    os.system("sudo hciconfig hci0 leadv 0")

    def on_press(key):
        res = input_mapper.pressed(key)
        if res:
            GLib.idle_add(app.send_keys, res[0], res[1])
            #app.send_keys(res[0], res[1])
    #    print('{0} pressed'.format(
    #        key))

    def on_release(key):
        res = input_mapper.released(key)
        if res:
            #app.send_keys(res[0], res[1])
            GLib.idle_add(app.send_keys, res[0], res[1])
        #GLib.idle_add(app.send_keypress, key, 0)
        #print('{0} release'.format(
        #    key))

        #if key == Key.esc:
        #    # Stop listener
        #    return False

    def input_thr():
        with Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()


    thr = threading.Thread(target=input_thr)
    thr.daemon = True
    thr.start()

    mainloop.run()

if __name__ == '__main__':
    main()

