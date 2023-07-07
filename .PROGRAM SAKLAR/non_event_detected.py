import sys
import RPi.GPIO as GPIO
from time import sleep

# init var
press_down_ra = False
press_up_ra = False
counter_down_ra = 0

press_down_rp = False
press_up_rp = False
counter_down_rp = 0

press_down_rr = False
press_up_rr = False
counter_down_rr = 0

pin_reset_app = int(sys.argv[1])
pin_reset_printer = int(sys.argv[2])
pin_reboot_raspi = int(sys.argv[3])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(pin_reset_app, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pin_reset_printer, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pin_reboot_raspi, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:

    # ================ btn shutdown/reboot/restart APP ==============
    if GPIO.input(pin_reset_app) == GPIO.HIGH:
        counter_down_ra += 1
        press_down_ra = True
    elif GPIO.input(pin_reset_app) == GPIO.LOW:

        if press_down_ra:
            press_down_ra = False #reset
            press_up_ra = True

    if press_up_ra:
        press_up_ra = False #reset
        print("reset APP")
        
        counter_down_ra = 0
    
    # =================================================
    
    if GPIO.input(pin_reset_printer) == GPIO.HIGH:
        counter_down_rp += 1
        press_down_rp = True
    elif GPIO.input(pin_reset_printer) == GPIO.LOW:

        if press_down_rp:
            press_down_rp = False #reset
            press_up_rp = True

    if press_up_rp:
        press_up_rp = False #reset
        print("reset PRINTER")
        
        counter_down_rp = 0
    
    # ================================================

    if GPIO.input(pin_reboot_raspi) == GPIO.HIGH:
        counter_down_rr += 1
        press_down_rr = True
    elif GPIO.input(pin_reboot_raspi) == GPIO.LOW:

        if press_down_rr:
            press_down_rr = False #reset
            press_up_rr = True

    if press_up_rr:
        press_up_rr = False #reset
        print("reboot RASPI")
        
        counter_down_rr = 0
    # =============== end btn shutdown/reboot/ restart APP ==========

    sleep(0.1)