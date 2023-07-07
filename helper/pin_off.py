import sys
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

args_len = len(sys.argv)

for i in range(args_len):
    j = i+1

    if j < args_len:
        gate_out = int(sys.argv[j])
        GPIO.setup(gate_out, GPIO.OUT)
        GPIO.output(gate_out,GPIO.LOW)
