from flask import Flask, request
import datetime
import os
import paho.mqtt.client as mqtt
import threading
from pprint import pprint, pformat
import json

app = Flask(__name__)

MQTT_AVAIL_TOPIC = 'eaglepower/availability'
MQTT_DEMAND_TOPIC = 'eaglepower/demand/value'
MQTT_SUM_TOPIC = 'eaglepower/summation/value'
MQTT_PRICE_TOPIC = 'eaglepower/price/value'


client = None
client_connected = False


class AbstractDataBlock(object):
    key = None

    @classmethod
    def fromObject(cls, o):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

class DemandDataBlock(AbstractDataBlock):
    KEY = 'InstantaneousDemand'

    def __init__(self, demand):
        # demand in kW.
        super(DemandDataBlock, self).__init__()
        self.demand = demand

    @classmethod
    def fromObject(cls, o):
        """
        {"componentId": "all",
         "data": {"demand": 0.717, "units": "kW"},
         "dataType": "InstantaneousDemand",
         "subdeviceGuid": "00078100008fa8bc",
         "timestamp": "1605672440000"}

        :param o:
        :return:
        """
        demand = o['data']['demand']
        units = o['data']['units']
        if units == 'kW':
            value = float(demand)
        elif units == 'W':
            value = float(demand * 1000)
        else:
            raise Exception('Unknown unit for demand block. \n{}'.format(pformat(o)))

        return cls(demand=value)

    def post(self):
        if client is None or client_connected == False:
            return
        client.publish(MQTT_DEMAND_TOPIC, self.demand)

class SummationDataBlock(AbstractDataBlock):
    KEY = 'CurrentSummation'

    def __init__(self, summation):
        # float value representing kWh
        super(SummationDataBlock, self).__init__()
        self.summation = summation

    @classmethod
    def fromObject(cls, o):
        """
        {"componentId": "all",
         "data": {"summationDelivered": 123298.985,
                  "summationReceived": 0.0,
                  "units": "kWh"},
         "dataType": "CurrentSummation",
         "subdeviceGuid": "00078100008fa8bc",
         "timestamp": "1605672461000"}

        :param o:
        :return:
        """
        summation = float(o['data']['summationDelivered'])
        units = o['data']['units']
        if units != 'kWh':
            raise Exception('Unknown unit for demand block. \n{}'.format(pformat(o)))

        return cls(summation=summation)

    def post(self):
        if client is None or client_connected == False:
            return
        client.publish(MQTT_SUM_TOPIC, self.summation)


class PriceDataBlock(AbstractDataBlock):
    KEY = 'Price'

    def __init__(self, price):
        # float price in dollars.
        super(PriceDataBlock, self).__init__()
        self.price = price

    @classmethod
    def fromObject(cls, o):
        """
        {"componentId": "all",
         "data": {"PriceCurrency": "USD",
                  "PriceDuration": 65535,
                  "PriceRateLabel": "Block 1",
                  "PriceStartTime": 1605672472,
                  "PriceTier": 0,
                  "PriceTrailingDigits": 4,
                  "price": 0.0935,
                  "units": "min"},
         "dataType": "Price",
         "subdeviceGuid": "00078100008fa8bc",
         "timestamp": "1605672472000"}

        :param o:
        :return:
        """
        price = float(o['data']['price'])

        return cls(price=price)

    def post(self):
        if client is None or client_connected == False:
            return
        client.publish(MQTT_PRICE_TOPIC, self.price)


def processPostData(postData):
    # The time from the sender clock for the data received.
    timestamp = float(postData['timestamp']) / 1000
    # ts = datetime.datetime.fromtimestamp(timestamp)
    body = postData.get('body')
    if not body:
        return

    DATABLOCKS = (
        DemandDataBlock,
        SummationDataBlock,
        PriceDataBlock,
    )
    DATABLOCKS_MAP = {x.KEY:x for x in DATABLOCKS}

    for b in body:
        dt = b.get('dataType')
        if dt is None:
            continue

        dataCls = DATABLOCKS_MAP.get(dt)
        if dataCls is None:
            continue

        o = dataCls.fromObject(b)
        o.post()



@app.route('/data', methods=['POST'])
def data():
    data = request.get_json()
    processPostData(data)
    return ''


def iterMockData(path):
    with open(path, 'r') as f:
        c = f.read()
        for block in c.split('\n\n'):
            block = block.strip()
            if block:
                d = json.loads(block)
                yield d


def connectMqtt():
    global client
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        global client_connected
        print("Connected with result code " + str(rc))
        if rc == 0:
            client.publish(MQTT_AVAIL_TOPIC, 'online')
            client_connected = True

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    client = mqtt.Client(client_id='EaglePower')
    client.will_set(MQTT_AVAIL_TOPIC, 'offline')

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(os.environ['MQTT_HOST'], int(os.environ['MQTT_PORT']), 60)
    client.loop_start()
    # client.loop_forever()
    return client


def main():
    connectMqtt()

    # for d in iterMockData('dumps.txt'):
    #     processPostData(d)
    #     # return

    app.run(host='0.0.0.0', port=44202)

if __name__ == '__main__':
    main()
