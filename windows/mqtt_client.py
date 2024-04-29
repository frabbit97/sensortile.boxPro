import paho.mqtt.client as mqtt
class MQTTClient:
    def __init__(self, broker_address, port, username, password):
        self.broker_address = broker_address
        self.port = port
        self.username = username
        self.password = password
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish

    def __init__(self, broker_address, port):
        self.broker_address = broker_address
        self.port = port
        self.username = ""
        self.password = ""
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish

    def connect(self):
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print("Connection to MQTT broker failed, return code:", rc)

    def on_publish(self, client, userdata, mid):
        print("Message published successfully")

    def publish_message(self, topic, message):
        self.client.publish(topic, message)
