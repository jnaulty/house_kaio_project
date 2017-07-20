'''
test.py

Run for basic diagnostic
ampy --port /dev/ttyUSB0 run test.py

'''

import config
import gc
import network

def mem_info():
    print('Starting diagnostic')
    print("mem_free: %s" % gc.mem_free())
    print("gc_collect()")
    gc.collect()
    print("mem_free: %s" % gc.mem_free())


def hello_world():
    print('Hello world! I can count to 10:')
    for i in range(1,11):
            print(i)


def setup_wifi():
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    print('Connecting Wifi')
    sta_if.active(True)
    sta_if.connect(config.ESSID, config.PASSWORD)
    print('Connection On: %s' % sta_if.isconnected())

def wifi_info():
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    print('ESP8266 Wifi station on: %s' % sta_if.active())
    print('ESP8266 AP on: %s' % ap_if.active())
    print('ESP8266 network info:\nIP Address, netmask, gateway, DNS\n%s' % str(ap_if.ifconfig()))


def test_wifi():
    setup_wifi()

def main():
    print('\n')
    hello_world()
    print('\n')
    print('Mem_stats')
    mem_info()
    print('\n')
    wifi_info()
    test_wifi()



if __name__=="__main__":
    main()


