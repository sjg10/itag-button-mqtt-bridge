from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import paho.mqtt.client as mqtt
import os,sys, signal,json, threading
from button import Button
from time import sleep


class ButtonMQTTBridge:
    def __init__(self, name, default_topic, default_msg):
        self.name = name
        self.b = Button()
        self.targets = [{"topic": default_topic, "msg": default_msg}]
        print("Default targets set ", self.targets)

    def connect(self, mac_addr, mqttprops):
        if self.b.connect(mac_addr, self.on_press):
            self.client = client = mqtt.Client(self.name, userdata=self)
            client.on_connect = self.on_connect()
            client.on_disconnect = self.on_disconnect()
            client.on_message = self.on_message()
            client.username_pw_set(mqttprops['user'], mqttprops['pass'])
            client.connect(mqttprops['address'], mqttprops['port'])
            return True
        else:
            return False

    def watch_button(self):
        def run():
            while True:
                self.b.waitForNotifications(1.0)
        self.t = self.ListenerThread(self.b)
        self.t.start()

    class ListenerThread(threading.Thread):
        """Thread for listening to button presses (for some reason async button notifications with bluepy fail"""
        def __init__(self,  btn, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._stop_event = threading.Event()
            self.btn = btn

        def stop(self):
            self._stop_event.set()

        def stopped(self):
            return self._stop_event.is_set()
        def run(self):
            while not self.stopped():
                self.btn.waitForNotifications(0.5)

    def run(self):
        self.watch_button()
        self.client.loop_forever()

    def on_press(self, data):
        for target in self.targets:
            print("Button pressed so sending",target)
            self.client.publish(target["topic"], payload=target["msg"])

    def publish_status(self):
        battery = self.b.get_bat()
        print("Sending battery", battery) 
        self.client.publish(self.name + "/bat", payload=battery)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self):
        def con_handler(client, s, flags, rc):
            print("Connected with result code "+str(rc))
            if rc == 0:
                # Subscribing in on_connect() means that if we lose the connection and
                # reconnect then subscriptions will be renewed.
                client.subscribe(s.name + "/targets")
                client.subscribe(s.name + "/status")
                s.publish_status()
        return con_handler

    def on_disconnect(self):
        def discon_handler(client, s, rc):
            print("Disconnect")
            if s.t:
                print("Stop listening")
                s.t.stop()
                s.t.join()
            if s.b:
                print("Device disconnecting")
                s.b.disconnect()
        return discon_handler

    def disconnect(self):
        self.client.disconnect()

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self):
        def msg_handler(client, s, msg):
            print(msg.topic+" "+str(msg.payload))
            if msg.topic == self.name + "/status":
                s.publish_status()
            elif msg.topic == self.name + "/targets":
                try:
                    js = json.loads(msg.payload.decode("utf-8"))
                    if "targets" in js:
                        self.targets = js["targets"]
                        print("New targets set ", self.targets)
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    pass
        return msg_handler

if __name__ == "__main__":
    mac = os.environ["BUTTON_MAC"]
    name = os.environ["DEVICE_NAME"]
    
    mqttprops = {}
    mqttprops['user'] = os.environ["MQTT_USERNAME"]
    mqttprops['pass'] = os.environ["MQTT_PASSWORD"]
    mqttprops['port'] = int(os.environ["MQTT_PORT"])
    mqttprops['address'] = os.environ["MQTT_ADDRESS"]

    b = ButtonMQTTBridge(name, os.environ["DEFAULT_TOPIC"], os.environ["DEFAULT_MSG"])
    if b.connect(mac, mqttprops):
        def signal_handler(sig, frame):
            print("Caught Ctrl+C")
            b.disconnect()
        signal.signal(signal.SIGINT, signal_handler)
        print("Starting main loop, SIGINT/CTRL+C to escape")
        b.run()
    else:
        print("Could not connect to device", file=sys.stderr)
        sys.exit(-1)

