import RPi.GPIO as GPIO
import mysql.connector
from mysql.connector import Error
import paho.mqtt.client as mqtt
import time
import logging
from mfrc522 import SimpleMFRC522
from time import sleep
from time import time
from datetime import datetime

wait=sleep
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


#User defined functions
def reset():
    ret=client.publish("channel/main", "", 0, True)



#mysql

def chck(uid):
    sql="SELECT * FROM ID_INFO WHERE UID= %s" %(uid)
    cursor.execute(sql,uid)
    connection.commit()
    record=cursor.fetchall()
    print(record)
    if record:
        sql="INSERT INTO ATT_LOG(NAME, UID, TIME, DATE, ID) VALUES(%s, %s, %s, %s, %s)"
        now = datetime.now()
        time=now.strftime("%H%M%S")
        date=now.strftime("%Y-%m-%d")
        values=(record[0][1],record[0][2], time, date, record[0][0])
        cursor.execute(sql,values)
        connection.commit()
        logging.info("Authorized")
        client.publish('channel/main', 'hi', qos=2)
    
    else:
        logging.info("Not Authorized")

try:
    connection=mysql.connector.connect(host='localhost',
                                       database='attendance',
                                       user='root',
                                       password='password')
    if connection.is_connected():
        cursor=connection.cursor(buffered=True)
        logging.info("Database connected")
except Error as e:
    logging.info("Error while connecting to Mysql",e)
    

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
    wait(2)
wait(3)


# ret=client.publish("channel/main", "hi")
# logging.info("published return="+ str(ret))
# client.loop_stop()
# client.disconnect()

#main
#Setting up reader object
reader = SimpleMFRC522()

while True:
    #reading initially to check for admin card
#     try:
#        id,text = reader.read()
#     finally:
#        GPIO.cleanup()
    logging.info("Setting id=123 for testing")
    id='123' #test condition will remove after testing
    #if admin card replace q with admin card uid
    if id=='q':
        logging.info('Record adding')
        #new uid is read and published to the server channel
        try:
            id,text = reader.read()
            ret=client.publish('channel/main', id, qos=2)
            logging.info("published return="+ str(ret))
            wait(1)
        except KeyboardInterrupt:
            break
        finally:
            client.disconnect()
            GPIO.cleanup()
    else:
        logging.info("Checking in existing records")
        result=chck(id)
        wait(2)
        print('checking')
        

