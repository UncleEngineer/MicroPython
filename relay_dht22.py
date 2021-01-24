from machine import Pin
import time
import dht
# Initailize
RLPIN = 5 # RELAY PIN
relay = Pin(RLPIN, Pin.OUT)
# Setup State ON/OFF
ON = 0
OFF = 1

def turn_on():
    relay.value(ON)
    print('RELAY ON')
    
def turn_off():
    relay.value(OFF)
    print('RELAY OFF')

# DHT22
d = dht.DHT22(Pin(4))
state = False
count = 0

while True:
    d.measure()
    temp = d.temperature()
    humid = d.humidity()
    print(count)
    print('TEMP: {} HUMID: {}'.format(temp,humid)) 
    if temp > 45:
        state = True
        #print('TURN ON')
    else:
        state = False
        #print('TURN OFF')
    if state == True:
        turn_on() # Open Fan
    else:
        turn_off()   
    print('RELAY STATE: ',relay.value())
    print('-------')
    count += 1 # count = count + 1
    time.sleep(3)
    
    
    
    
