from esp8266_i2c_lcd import I2cLcd
from machine import I2C
from machine import Pin
import dht
import time


i2c = I2C(scl=Pin(5),sda=Pin(4),freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

#################
import network
import socket

serverip = '192.168.1.150'
port = 7500

time.sleep(10)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
#sta_if.scan()
time.sleep(1)
sta_if.connect("Uncle Engineer2(2.4GHz)", "212224236")

lcd.clear()
lcd.putstr('Connecting...\n\n')

time.sleep(3)
network_status = sta_if.isconnected()
print("STATUS: ", sta_if.isconnected()) 
# sta_if.ifconfig()
#################


d = dht.DHT22(Pin(2))

ipaddr = sta_if.ifconfig()[0]

if network_status:
    textok = 'CONNECTED'
else:
    textok = 'FAILED'

time.sleep(2)
lcd.clear()
lcd.putstr('IP:{}\nSTATUS: {}\n'.format(ipaddr,textok))

time.sleep(2)
lcd.clear()
lcd.putstr('Loading...\n\n')

while True:
    d.measure()
    temp = d.temperature()
    humid = d.humidity()
    time.sleep(2)
    lcd.clear()
    lcd.putstr('TEMP: {} C    HUMID: {}'.format(temp,humid))
    data = 'TEMP: {} C HUMID: {}'.format(temp,humid)
    if network_status == True:
        try:
            server = socket.socket()
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

            server.connect((serverip,port))
            time.sleep(1)
            server.send(data.encode('utf-8'))

            data_server = server.recv(1024).decode('utf-8')
            print('Data from Server: ', data_server)
            server.close()
        except:
            lcd.clear()
            lcd.putstr('Server: Failed\n\n')
            
    else:
        network_status = sta_if.isconnected()
        if network_status:
            textok = 'CONNECTED'
        else:
            textok = 'FAILED'

        time.sleep(2)
        lcd.clear()
        lcd.putstr('IP:{}\nSTATUS: {}\n'.format(ipaddr,textok))
        '''
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

        server.connect((serverip,port))
        server.send(data.encode('utf-8'))

        data_server = server.recv(1024).decode('utf-8')
        print('Data from Server: ', data_server)
        server.close()
        '''
