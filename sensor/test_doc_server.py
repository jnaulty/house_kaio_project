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
CONTENT = b"""\
HTTP/1.0 200 OK

Hello #%d from MicroPython!
"""
def processPost(post):
    split = post.split(' ')
    print(str(split))

def main(micropython_optimize=False):
    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080/")

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)

        if not micropython_optimize:
            # To read line-oriented protocol (like HTTP) from a socket (and
            # avoid short read problem), it must be wrapped in a stream (aka
            # file-like) object. That's how you do it in CPython:
            client_stream = client_sock.makefile("rwb")
        else:
            # .. but MicroPython socket objects support stream interface
            # directly, so calling .makefile() method is not required. If
            # you develop application which will run only on MicroPython,
            # especially on a resource-constrained embedded device, you
            # may take this shortcut to save resources.
            client_stream = client_sock

        print("Request:")
        req = client_stream.readline()
        print(req)
        while True:
            if 'POST' in req:
                print('hello POST')
                h = client_stream.read()
                print(h)
                processPost(str(h))
                break
            h = client_stream.readline()
            print(h)
            if 'END' in h:
                print('end of the world')
                break
            if h == b"" or h == b"\r\n":
                break
            #print(h)
        client_stream.write(CONTENT % counter)

        client_stream.close()
        if not micropython_optimize:
            client_sock.close()
        counter += 1
        print()


main()
