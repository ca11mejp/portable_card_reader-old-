import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import logging
from mfrc522 import SimpleMFRC522
from time import time
from datetime import datetime

#setting up log object
logging.basicConfig(level=logging.INFO)

#All the callback functions are defined here
def on_log(client, userdata, level, buf):
    logging.info(buf)
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        logging.info("connected ok")
    else:
        logging.info("Bad connection send returned code="+str(rc))
        client.loop_stop()
def on_disconnect(client, userdata, rc):
    logging.info("Client disconnected ok")
def on_publish(client, userdata, mid):
    logging.info("In on_publish callback mid=" + str(mid))
def reset():
    ret=client.publish("channel/main", "", 0, True)

#Starting of server connection and initialising callbacks
Broker='165.232.183.7'
mqtt.Client.connected_flag=False
client=mqtt.Client('rpi')
client.username_pw_set('jp', password='startmqtt')
client.on_log=on_log
client.on_connect=on_connect
client.on_disconnect=on_disconnect
client.on_publish = on_publish
client.connect(Broker)
client.loop_start()

#Checking if connection was successful or not
while not client.connected_flag:
    logging.info("In wait loop")
    time.sleep(2)
time.sleep(3)


# ret=client.publish("channel/main", "hi")
# logging.info("published return="+ str(ret))
# client.loop_stop()
# client.disconnect()

#main
#Setting up reader object
reader = SimpleMFRC522()

while True:
    #reading initially to check for admin card
    try:
       id,text = reader.read()
    finally:
       GPIO.cleanup()
    id='q' #test condition will remove after testing
    #if admin card replace q with admin card uid
    if id=='q':
        logging.info('Record adding')
        #new uid is read and published to the server channel
        try:
            id,text = reader.read()
            ret=client.publish('channel/main', id, qos=2)
            logging.info("published return="+ str(ret))
            time.sleep(1)
        except KeyboardInterrupt:
            break
        finally:
            client.disconnect()
            GPIO.cleanup()
    else:
        try:
        
            client.publish('channel/main', 'hi', qos=2)
            print('hi')
            time.sleep(5)
