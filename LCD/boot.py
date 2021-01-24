from esp8266_i2c_lcd import I2cLcd
from machine import I2C
from machine import Pin
# i2c = I2C(scl=Pin(22),sda=Pin(21),freq=100000)
# lcd = I2cLcd(i2c, 0x27, 2, 16)
# lcd.clear()
# lcd.putstr('Uncle Engineer\nMicroPython')

i2c = I2C(scl=Pin(22),sda=Pin(21),freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
import utime as time

text = (' '*16)+ 'Uncle Engineer MicroPython'
count = 0
counttext = len(text)
while True:
    lcd.clear()
    print(text[count:16+count])
    lcd.putstr(text[count:16+count])
    time.sleep(0.5)
    count += 1
    if count > counttext:
        count = 0


