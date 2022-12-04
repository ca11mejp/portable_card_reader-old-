import paho.mqtt.client as mqtt
import mysql.connector
#import RPi.GPIO as GPIO
import time
import logging
from mysql.connector import Error
from time import time
from time import sleep
from datetime import datetime

logging.basicConfig(level=logging.INFO)

wait=sleep
state=0

#mqtt callbacks

def on_log(client, userdata, level, buf):
    logging.info(buf)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        logging.info("Client connected ok")
    else:
        logging.info("Bad connection returned code= "+str(rc))
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    logging.info("Client disconnected ok")

def on_subscribe():
    logging.info("Subscribed")

def on_publish(client, userdata, mid):
    logging.info("In on_publish callback mid=" +str(mid))

def on_message(client, userdata, message):
    topic=message.topic
    state=1
    rcv=str(message.payload.decode('utf-8'))
    pty(rcv)

def reset():
    ret=client1.publish('channel/main', '', 0, True)
    

#mysql connection

try:
    connection=mysql.connector.connect(host='localhost',
                                       database='attendance',
                                       user='root',
                                       password='password')
    if connection.is_connected():
        cursor=connection.cursor(buffered=True)
        logging.info("Database ready")

except Error as e:
    logging.info("Error while connecting to mysql: ", e)


#user defined
def c_read():
    try:
        uid, text = reader.read()
    finally:
        GPIO.cleanup()
    return uid
        
def tp_lvl(uid):
    snd="0 Nil "+uid
    client1.publish('channel/main', snd, qos=2)
    while state==0:
        client1.on_message=on_message
    logging.info("Priority mode ended")
    
def pty(rcv):
    msg=rcv.split()
    print(msg[0])
    if msg[0]=='2':
        print("save")
        ad(msg)
    elif msg[0]=='3':
        print("dlt")
        dlt(msg)
    else:
        logging.info("Nothing is going to happen")

def chck(ID):
    sql="SELECT * FROM ID_INFO WHERE ID= %s" %(ID)
    cursor.execute(sql)
    connection.commit()
    record=cursor.fetchall()
    return record

def log(msg):
    record=chck(msg[1])
    if record:
        sql="INSERT INTO ATT_LOG (ID, NAME, UID, TIME, DATE) VALUES (%s, %s, %s, %s, %s)"
        values=(record[0][1], record[0][3], record[0][2], record[0][4], record[0][5])
        cursor.execute(sql,values)
        connection.commit()
        logging.info("Authorized")
    else:
        logging.info("Not Authorized")

def ad(msg):
    sql="INSERT INTO ID_INFO(NAME, UID) VALUES (%s, %s)"
    values=(name, msg[2])
    cursor.execute(sql,values)
    connection.commit()
    logging.info("Entry added")


def dlt(msg):
    ID=msg[1]
    sql="DELETE FROM ID_INFO WHERE ID= "+ ID
    cursor.execute(sql)
    connection.commit()
    sql="SELECT MAX(ID) FROM ID_INFO"
    cursor.execute()
    connection.commit()
    result=cursor.commit()
    print(result)
    if result[0][0]==None:
        result[0][0]=101
    sql="ALTER TABLE ID_INFO AUTO_INCREMENT=%s" %(result[0][0])
    cursor.execute(sql)
    connection.commit()


#main
Broker='165.232.183.7'
mqtt.Client.connected_flag=False
client1=mqtt.Client('Reader')
client1.username_pw_set('jp', password='startmqtt')
client1.on_log=on_log
client1.on_connect=on_connect
client1.on_disconnect=on_disconnect
client1.on_publish=on_publish
client1.connect(Broker)
client1.loop_start()

while not client1.connected_flag:
    logging.info("In wait loop client1")
    wait(2)
wait(3)

reader = SimpleMFRC522()

while True:
    uid=c_read()

    if uid='q':
        logging.info("Priority mode")
        uid=c_read
        tp_lvl(uid)
        
    else:
        logging.info("Checking in existing records")
        result=chck(uid)
        wait(7)
        print('Logging')

client1.loop_stop()
client1.disconnect()
cursor.close()
connection.close()

