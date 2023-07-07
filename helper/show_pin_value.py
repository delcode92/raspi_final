import sys
import RPi.GPIO as GPIO
from time import sleep


pin = int(sys.argv[1])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


while True:
    print(GPIO.input(pin))
    sleep(1)
