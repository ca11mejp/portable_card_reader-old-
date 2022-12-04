import paho.mqtt.client as mqtt
import mysql.connector
import time
import logging
from mysql.connector import Error
from time import time
from time import sleep
from datetime import datetime

logging.basicConfig(level=logging.INFO)

wait=sleep

#mqtt callbacks

def on_log(client, userdata, level, buf):
    logging.info(buf)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        logging.info("Client connected ok")
    else:
        logging.info("Bad connection returned code= "+str(rc))
        client1.loop_stop()

def on_disconnect(client, userdata, rc):
    logging.info("Client disconnected ok")

def on_subscribe():
    logging.info("Subscribed")

def on_publish(client, userdata, mid):
    logging.info("In on_publish callback mid=" +str(mid))

def on_message(client, userdata, message):
    topic=message.topic
    rcv=str(message.payload.decode('utf-8'))
    pty(rcv)

def pty(rcv):
    msg=rcv.split()
    print(msg)
    if msg[0]=='1':
        logging.info('Logging')
        result=log_in(msg)
    elif msg[0]=='0':
        logging.info('Adding')
        result=menu(msg)
        
def menu(msg):
    print("MAIN MENU")
    print("===========")
    print("1. Add new entry")
    print("2. Delete an entry")
    print("Press anything else for cancelling")
    choice=int(input("Choose option: "))
    if choice==1:
        ad(msg)
    elif choice==2:
        dlt()
    else:
        print("Exiting...")
    
#mysql connection

try:
    connection=mysql.connector.connect(host='localhost',
                                       database='attendance',
                                       user='jp',
                                       password='password')
    if connection.is_connected():
        cursor=connection.cursor(buffered=True)
        logging.info("Database ready")

except Error as e:
    logging.info("Eroor while connecting to mysql: ", e)




def chck(ID):
    sql="SELECT * FROM ID_INFO WHERE ID= %s" %(ID)
    cursor.execute(sql)
    connection.commit()
    record=cursor.fetchall()
    return record

def log_in(msg):
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
    uid=msg[2]
    sql="SELECT * FROM ID_INFO WHERE UID= %s" %(uid)
    cursor.execute(sql)
    connection.commit()
    record=cursor.fetchall()
    if record:
        logging.info("Card already in use")
        snd='nil nil nil nil nil nil'
        client1.publish('channel/back', snd, qos=2)
    else:
        print("New entry to be added: ")
        name=input("Enter name: ")
        sql="INSERT INTO ID_INFO(NAME, UID) VALUES (%s, %s)"
        values=(name, msg[2])
        cursor.execute(sql,values)
        connection.commit()
        logging.info("Entry added")
        sql="SELECT * FROM ID_INFO WHERE UID=%s" %(int(msg[2]))
        cursor.execute(sql)
        connection.commit()
        record=cursor.fetchall()
        snd="2 "+str(record[0][0])+" "+str(record[0][2])+" "+str(record[0][1])+" nil nil"
        client1.publish('channel/back', snd, qos=2)

def dlt():
    ID=input("Enter the ID of the entry to be deleted: ")
    record=chck(ID)
    if record:
        sql="DELETE FROM ID_INFO WHERE ID= "+ ID
        cursor.execute(sql)
        connection.commit()
        snd="3 "+ID+" nil nil nil nil"
        client1.publish('channel/back', snd, qos=2)
        sql="SELECT MAX(ID) FROM ID_INFO"
        cursor.execute(sql)
        connection.commit()
        result=cursor.fetchall()
        print(result)
        if result[0][0]==None:
            result[0]=101
        sql="ALTER TABLE ID_INFO AUTO_INCREMENT=%s" %(result[0])
        cursor.execute(sql)
        connection.commit()

    else:
        logging.info("Record does not exist")
        snd='nil nil nil nil nil nil'
        client1.publish('channel/back', snd, qos=2)


#main
Broker='165.232.183.7'
mqtt.Client.connected_flag=False
client1=mqtt.Client('Server')
client1.username_pw_set('jp', password='startmqtt')
client1.on_log=on_log
client1.on_connect=on_connect
client1.on_disconnect=on_disconnect
client1.on_publish=on_publish
client1.connect(Broker)
client1.loop_start()

##client2=mqtt.Client('Server')
##client2.username_pw_set('jp', password='startmqtt')
##client2.on_log=on_log
##client2.on_connect=on_connect
##client2.on_disconnect=on_disconnect
##client2.on_publish=on_publish
##client2.connect(Broker)
##client2.loop_start()

while not client1.connected_flag:
    logging.info("In wait loop client1")
    wait(2)
wait(3)

##while not client2.connected_flag:
##    logging.info("In waiting loop client2")
##    wait(2)
##wait(3)

client1.subscribe('channel/main',qos=2)

while True:
    try:
        client1.on_message=on_message
    except KeyboardInterrupt:
        break

client1.disconnect()
##client2.disconnect()
cursor.close()
connection.close()

