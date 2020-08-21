#!venv/bin/python3.8

import logging
import sched
import sys
import time

import paho.mqtt.client as mqtt
import yaml
import yeelight as yl

# setup logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout)
logging.info("Start application")

# load config
with open("yeelightConfig.yaml", 'r') as stream:
    config = yaml.safe_load(stream)


# setup yeelight
def refreshAvailableBulbs():
    global bulbs
    availiableBulbs = yl.discover_bulbs()
    bulbs = {}
    for availiableBulb in availiableBulbs:
        bulb = yl.Bulb(availiableBulb["ip"], auto_on=True)
        name = bulb.get_properties()["name"]
        bulbs[name] = bulb
    logging.info("Update available bulbs. Currently {} bulbs are online.".format(len(bulbs)))


bulbs = {}
refreshAvailableBulbs()

# setup schedluer
scheduler = sched.scheduler(time.time, time.sleep)

# setup flows
flows = {
    "greenFlash": {
        "flow": yl.Flow(
            count=1,
            action=yl.Flow.actions.recover,
            transitions=[
                yl.HSVTransition(120, 100, duration=600),
                yl.HSVTransition(120, 100, duration=500, brightness=1),
                yl.HSVTransition(120, 100, duration=600)
            ]
        ),
        "duration": (600 + 500 + 600) / 1000
    }
}


# setup mqtt
def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker with result code \"{}\".".format(rc))
    client.subscribe(config["mqtt"]["topic"] + "/#")


def on_message(client, userdata, msg):
    global bulbs
    command = msg.payload.decode("utf-8")
    logging.info("New command \"{}\" in topic \"{}\"".format(command, msg.topic))
    lampName = msg.topic.replace(config["mqtt"]["topic"] + "/", "")
    if lampName in bulbs:
        bulb = bulbs[lampName]
        if command == "toggle":
            bulb.toggle()
        elif command == "turnon":
            bulb.turn_on()
        elif command == "turnoff":
            bulb.turn_off()
        elif command.startswith("flow"):
            flowName = command.replace("flow ", "")
            if flowName in flows:
                flow = flows[flowName]["flow"]
                flowDuration = flows[flowName]["duration"]
                bulbWasOff = bulb.get_properties()["power"] == "off"
                bulb.start_flow(flow)
                if bulbWasOff:
                    scheduler.enter(flowDuration, 1, bulb.turn_off)
            else:
                logging.error("Unkown flow name \"{}\".".format(flowName))
        else:
            logging.error("Unkown command \"{}\".".format(command))
    else:
        logging.error("Unkown lamp \"{}\".".format(lampName))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(config["mqtt"]["user"], password=config["mqtt"]["password"])
client.tls_set(ca_certs=config["mqtt"]["certpath"])
logging.info(
    "Try to connected to MQTT broker \"{}\" at port \"{}\".".format(config["mqtt"]["host"], config["mqtt"]["port"]))
client.connect(config["mqtt"]["host"], config["mqtt"]["port"], 60)
client.loop_start()


# refreshing loop
def refreshAvailableBulbsRoutine(sc):
    refreshAvailableBulbs()
    scheduler.enter(config["yeelight"]["refreshingInterval"], 2, refreshAvailableBulbsRoutine, (sc,))


scheduler.enter(config["yeelight"]["refreshingInterval"], 2, refreshAvailableBulbsRoutine, (scheduler,))
scheduler.run()
