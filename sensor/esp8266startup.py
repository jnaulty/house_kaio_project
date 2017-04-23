try:
    import usocket as socket
    import network as network
    from umqtt.simple import MQTTClient
except:
    import socket

import os
import time
import gc

CONFIG_PATH = "wifi.cfg"
WIFI_SSID = ""
WIFI_PASSWORD = ""
MQTT_HOST = "192.168.1.168"
MQTT_PORT = "1883"
SENSOR_NAME = "security001"
SENSOR_TOPIC = "security"
CONFIG = dict()
MQTTCLIENT = None

index = '''HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n
<html>
    <head>
    </head>
    <body>
        <form action="/" method="POST" form="espForm">
            WIFI SSID:<br>
            <input type="text" name="ssid"><br>
            <p>WIFI Password:<p>
            <input type="text" name="wifiPassword">
            <p>Sensor Name:<p>
            <input type="text" name="sensorName">
            <p>Sensor Topic:<p>
            <input type="text" name="sensorTopic">
            <p>MQTT Host:<p>
            <input type="text" name="mqttHost">
            <br>
            <button type="submit">post</button>
        </form>
    </body>
</html>
'''

HTML_TO_CONFIG = dict()
HTML_TO_CONFIG["ssid"] = "WIFI_SSID"
HTML_TO_CONFIG["wifiPassword"] = "WIFI_PASSWORD"
HTML_TO_CONFIG["mqttHost"] = "MQTT_HOST"
HTML_TO_CONFIG["sensorTopic"] = "SENSOR_TOPIC"
HTML_TO_CONFIG["sensorName"] = "SENSOR_NAME"

def configInit():
    CONFIG["CONFIG_PATH"] = CONFIG_PATH
    CONFIG["WIFI_SSID"] = WIFI_SSID
    CONFIG["WIFI_PASSWORD"] = WIFI_PASSWORD
    CONFIG["MQTT_HOST"] = MQTT_HOST
    CONFIG["MQTT_PORT"] = MQTT_PORT
    CONFIG["SENSOR_NAME"] = SENSOR_NAME
    CONFIG["SENSOR_TOPIC"] = SENSOR_TOPIC
    return

def startAccessPoint():
    disableSTA()
    print("Starting up Access Point Mode")
    try:
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(True)
    except:
        print("ERROR: There was an error starting the Access Point")
        return False
    return True

def disableAP():
    print("Disabling AP")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    return

def disableSTA():
    print("Disabling STA")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    return

def startWifi():
    print("Starting up Wifi connection")
    print("SSID: %s" %CONFIG["WIFI_SSID"])
    disableAP()
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(CONFIG["WIFI_SSID"], CONFIG["WIFI_PASSWORD"])
        if sta_if.isconnected():
            print('Network config:', sta_if.ifconfig())
            print("Wifi Connection Successfull!")
            return True
        else:
            return False
    print("Wifi Already Connected!")
    print('Network config:', sta_if.ifconfig())
    return True

def startMqtt():
    print("Starting up MQTT Connection...")
    print("MQTT Server: %s" %CONFIG["MQTT_HOST"])
    print("MQTT Port: %s" %CONFIG["MQTT_PORT"])
    try:
        client = MQTTClient("umqtt_client", CONFIG["MQTT_HOST"])
        client.connect()
    except OSError as e:
        print("MQTT Error: %s" %e)
        return client, False
    return client, True


def configExists():
    files = os.listdir()
    for file in files:
        if file == CONFIG_PATH:
            return True
    return False

def deleteConfig():
    if configExists():
        return os.remove(CONFIG_PATH)
    else:
        print('no file found')

def writeConfig(htmlConfig):
    print("Writting new config to file: %s" % CONFIG_PATH)
    f = open(CONFIG_PATH, "w")
    for key, value in htmlConfig.items():
        f.write(HTML_TO_CONFIG[key]+":"+value+"\n")
    f.close()
    return True

def readConfig():
    if configExists():
        f = open(CONFIG_PATH, 'r')
        for line in f:
            configList = line.strip().split(":")
            if len(configList) == 2:
                key = configList[0]
                value = configList[1]
                if key in CONFIG:
                    print('Writing to global scope: CONFIG[%s] = %s' % (key, value))
                    CONFIG[key] = value
                else:
                    print("Error in parsing network config, back to AP mode")
                    print("%s" %line)
                    f.close()
                    return False
            else:
                print("Error in parsing network config, back to AP mode")
                print("%s")%line
                f.close()
                return False
        f.close()
    else:
        print("Could not read file, file does not exists")
        return False
    return True

def startHTTPServer(micropython_optimize=False):
    s = socket.socket()
    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    print("Bind address info:", ai)
    addr = ai[0][-1]
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    #print("Listening, connect your browser to http://%s:8080" %addr)
    counter = 0
    while True:
        res = s.accept()
        print(gc.mem_free())
        #print(res)
        client_sock = res[0]
        client_addr = res[1]
        req=client_sock.recv(4096)
        processed_request=inRequest(req)
        #print(processed_request)
        htmlDict = processPOST(processed_request)
        if htmlDict:
            #print("Received html POST request: %s" % htmlDict)
            print(htmlDict)
        if not micropython_optimize:
            # To read line-oriented protocol (like HTTP) from a socket (and
            # avoid short read problem), it must be wrapped in a stream (aka
            # file-like) object. That's how you do it in CPython:
            #print('not optimize')
            client_stream = client_sock.makefile("rwb")
        else:
            # .. but MicroPython socket objects support stream interface
            # directly, so calling .makefile() method is not required. If
            # you develop application which will run only on MicroPython,
            # especially on a resource-constrained embedded device, you
            # may take this shortcut to save resources.
            client_stream = client_sock

        client_stream.write(index)
        client_stream.close()
        if not micropython_optimize:
            client_sock.close()
        counter += 1
        #print()


def inRequest(text):
    text = text.decode("utf-8")
    print(text)
    content=''
    if text[0:3]=='GET':
        method='GET'
    else:
        method='POST'
        k=len(text)-1
        while k>0 and text[k]!='\n' and text[k]!='\r':
            k=k-1
        content=text[k+1:]
    url=text[:text.index(' ')]
    return {"method":method,"url":url,"content":content}

def processPOST(response_dict):
    response_content = response_dict['content']
    print(response_content)
    response_param_list= response_content.split('&')
    param_dict = {}
    if response_dict['method'] != 'POST':
        return
    for ele in response_param_list:
        #TODO make the following code parse in a pythonic way
        # this is not pythonic
        key_value_pair = ele.split('=')
        if len(key_value_pair) < 2:
            print("Error processing the HTTP POST")
            return
        param_dict[key_value_pair[0]] = key_value_pair[1]
    return param_dict

def apInit():
    startAccessPoint()
    req = startHTTPServer()
    writeConfig(req)
    return True

def main():
    configInit()
    wifiTrials = 0
    wifiSuccess = False
    mqttSuccess = False
    client = None
    while(True):
        if not configExists() or wifiTrials >=3:
            # start apInit and wait for new config file to be created.
            if wifiTrials >=3:
                print("Wifi connection failed too many times")
            print("Returning back to Access Point Mode")
            apInit()
            wifiTrials = 0
            wifiSuccess = False
            mqttSuccess = False
        # Config exists, read config and start wifi connection
        if not wifiSuccess:
            wifiTrials+=1
            if not readConfig():
                print("Deleting Config and returning back to Access Point Mode")
                deleteConfig()
                continue
            wifiSuccess = startWifi()
            time.sleep(10)
        if wifiSuccess:
            mqttTrials = 0
            wifiTrials = 0
            if not mqttSuccess:
                while mqttTrials <= 5:
                    client, mqttSuccess = startMqtt()
                    if mqttSuccess:
                        print("MQTT Server Connection Successfull!")
                        time.sleep(2)
                        break
                    else:
                        mqttTrials+=1
                        time.sleep(2)
            if mqttSuccess:
                try:
                    print("Start Sending Data...")
                    client.publish(CONFIG["SENSOR_TOPIC"], "Hello")
                    time.sleep(5)
                except OSError as e:
                    print("Publish Error: %s" %e)
                    client.close()
                    mqttSuccess = False
    print("Main Loop ended")
    return

main()
