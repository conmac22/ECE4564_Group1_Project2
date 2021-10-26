from gpiozero import RGBLED
from time import sleep

led = RGBLED(red = 16, green = 20, blue = 21)

while(1):
    led.color = (1,1,1)
    sleep(1)
    led.color = (1,0,0)
    sleep(1)
    led.color = (0,1,0)
    sleep(1)
    led.color = (0,0,1)
    sleep(1)