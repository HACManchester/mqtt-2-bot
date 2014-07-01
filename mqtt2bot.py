#!/usr/bin/python
import mosquitto
import random
import socket
import sqlite3
import time
import yaml

from prettydate import pretty_date

config_f = open('config.yaml')
config = yaml.safe_load(config_f)
config_f.close()

def send_to_bot(message):
    global config
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((config['bot']['server'], config['bot']['port']))
        s.send('%s %s' % (config['bot']['channel'], message))
        s.close()
    except Exception, e:
        pass

def last_seen(username):
    conn = sqlite3.connect('last_seen.db')
    c = conn.cursor()
    un = (username,)
    c.execute("SELECT timestamp FROM lastseen WHERE username=?", un)
    ls = c.fetchone()
    c.execute("DELETE FROM lastseen WHERE username=?;", un)
    c.execute("INSERT INTO lastseen VALUES(?,?);", (username, int(time.time())))
    conn.commit()
    conn.close()
    return ls


def on_message(mosq, obj, msg):
	if msg.topic == 'door/outer/opened/username':
		ls = last_seen(msg.payload)
		if not ls:
			send_to_bot("%s opened the outer door." % msg.payload)
		else:
			send_to_bot("%s opened the outer door. Last seen %s." % (msg.payload, pretty_date(ls[0])))
	elif msg.topic == 'door/outer/buzzer':
		send_to_bot("%s" % random.choice(['Buzzer', 'Buzzer', 'Buzzer', 'Buzzer', 'Buzzer', 'Buzzer', 'Buzzer', 'Buzzer', 'Buzzer', 'rezzuB', 'Buzzard']))
	elif msg.topic == 'door/outer/invalidcard':
		send_to_bot("Unknown card at door")
	elif msg.topic == 'bot/outgoing':
		send_to_bot(msg.payload)
	elif msg.topic == 'door/shutter/opened':
		send_to_bot("Shutter Opened!")
	elif msg.topic == 'door/shutter/closed':
		send_to_bot("Shutter Closed!")

conn = sqlite3.connect('last_seen.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS lastseen (username TEXT, timestamp INTEGER);")
conn.commit()
conn.close()

mqttc = mosquitto.Mosquitto(config['mqtt']['name'])	
while True:
	mqttc.connect(config['mqtt']['server'])
	mqttc.subscribe("door/outer/#")
	mqttc.subscribe("bot/outgoing")
	mqttc.subscribe("door/shutter/#")
	mqttc.on_message = on_message
	 
	while mqttc.loop() == 0:
		pass
	print ("MQTT connection lost!")
	mqttc.disconnect()
	time.sleep(5)
