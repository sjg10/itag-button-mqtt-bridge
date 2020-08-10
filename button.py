from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from time import sleep

class Button(DefaultDelegate, Peripheral):
    BTN_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
    BAT_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
    ALERT_UUID = "00002a06-0000-1000-8000-00805f9b34fb"

    def __init__(self):
        DefaultDelegate.__init__(self)
        Peripheral.__init__(self)
        self.withDelegate(self)

    def connect(self, address, on_btn_press):
        self.c_btn = None
        self.c_bat = None
        self.c_alert = None
        Peripheral.connect(self, address)
        if self.__get_char():
            self.on_btn_press = on_btn_press
            return True
        else:
            self.disconnect()
            return False

    def __get_char(self):
        serv = self.getServices()
        for s in serv:
            cs = s.getCharacteristics()
            for c in cs:
                if self.BTN_UUID == c.uuid: self.c_btn = c
                if self.BAT_UUID == c.uuid: self.c_bat = c
                if self.ALERT_UUID == c.uuid: self.c_alert = c
        return self.c_btn and self.c_bat and self.c_alert

    def handleNotification(self, cHandle, data):
        if self.c_btn and self.c_btn.getHandle() == cHandle: self.on_btn_press(data)
        if self.c_bat and self.c_bat.getHandle() == cHandle: pass
        if self.c_alert and self.c_alert.getHandle() == cHandle: pass

    def get_bat(self):
        return self.c_bat.read()[0]

