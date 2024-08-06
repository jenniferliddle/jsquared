import time
import machine
from picographics import PicoGraphics, DISPLAY_INKY_PACK
from umqtt.simple import MQTTClient
import network

# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Fill in your network name (ssid) and password here:
ssid = 'LBW2gig'
password = 'castleton'
wlan.connect(ssid, password)

# Display
graphics = PicoGraphics(DISPLAY_INKY_PACK)
WIDTH, HEIGHT = graphics.get_bounds()
graphics.set_update_speed(3)
graphics.set_font("sans")
graphics.set_pen(15)
graphics.clear()
graphics.set_pen(0)
graphics.set_thickness(5)
graphics.update()

# mqtt
SERVER="192.168.1.150"
ClientID = f'raspberry-sub-{time.time_ns()}'
user = "emqx"
password = "public"
topic = "jsquared/inky"

def sub(topic, msg):
    print('received message %s on topic %s' % (msg, topic))
    graphics.set_pen(15)
    graphics.clear()
    graphics.set_pen(0)
    graphics.text(msg, 20, 60, scale=4)
    graphics.update()


def connect(client):
    print('Connecting to MQTT Broker "%s"' % (SERVER))
    client.connect()

def reconnect(client):
    print('Failed to connect to MQTT broker, Reconnecting...')
    time.sleep(5)
    client.connect()
    
def main():
    client = MQTTClient(ClientID, SERVER, 1883)
    try:
        connect(client)
    except OSError as e:
        reconnect(client)

    client.set_callback(sub)
    client.subscribe(topic)
    while True:
        if True:
            client.wait_msg()
        else:
            client.check_msg()
            time.sleep(1)

main()
