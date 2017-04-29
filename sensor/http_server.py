try:
    import usocket as socket
except:
    import socket

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

def main(micropython_optimize=False):
    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    #print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    #print("Listening, connect your browser to http://<this_host>:8080/")

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        req=client_sock.recv(4096)
        processed_request=inRequest(req)
        #print(processed_request)
        # TODO write output of processPOST to file
        processPOST(processed_request)

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
   content=''
   #print(text)
   text=text.decode('utf-8')
   print(text)
   if text[0:3]=='GET':
      method='GET'
   else:
      method='POST'
      k=len(text)-1
      while k>0 and text[k]!='\n' and text[k]!='\r':
         k=k-1
      content=text[k+1:]
   text=text[text.index(' ')+1:]
   url=text[:text.index(' ')]
   return {"method":method,"url":url,"content":content}

def processPOST(response_dict):
    '''
    input is diction from inRequest
    outputs dictionary of content from POST request
    '''
    #print(response_dict)
    response_content = response_dict['content']
    #print(response_dict['method'])
    if response_dict['method'] != 'POST':
        return
    res_offset = response_content.find('ssid')
    response_content = response_content[res_offset:]
    response_param_list= response_content.split('&')
    param_dict = {}
    for ele in response_param_list:
        #TODO make the following code parse in a pythonic way
        # this is not pythonic
        key_value_pair = ele.split('=')
        param_dict[key_value_pair[0]] = key_value_pair[1]
    print(param_dict)
    return param_dict

main()

