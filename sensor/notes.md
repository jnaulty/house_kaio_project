# load files, setup wifi
ampy --port /dev/ttyUSB0 put test_doc_server.py
ampy --port /dev/ttyUSB0 run test.py

picocom /dev/ttyUSB0 -b115200

curl -d "param1=value1&param2=value2&\nEND" -X POST http://192.168.1.161:8080 -vvv 
