import sys
import RPi.GPIO as GPIO
from time import sleep

gate_out = int(sys.argv[1])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(gate_out, GPIO.OUT)

GPIO.output(gate_out,GPIO.HIGH)
#sleep(1)
#GPIO.output(gate_out,GPIO.LOW)