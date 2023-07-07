import sys
import RPi.GPIO as GPIO


def reset_app_callback(channel):
    print("reset APP")

def reset_printer_callback(channel):
    print("reset PRINTER")

def reboot_raspi_callback(channel):
    print("reboot RASPI")


pin_reset_app = int(sys.argv[1])
pin_reset_printer = int(sys.argv[2])
pin_reboot_raspi = int(sys.argv[3])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(pin_reset_app, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pin_reset_printer, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pin_reboot_raspi, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


GPIO.add_event_detect(pin_reset_app, GPIO.FALLING, callback=reset_app_callback, bouncetime=1000)
GPIO.add_event_detect(pin_reset_printer, GPIO.FALLING, callback=reset_printer_callback, bouncetime=1000)
GPIO.add_event_detect(pin_reboot_raspi, GPIO.FALLING, callback=reboot_raspi_callback, bouncetime=1000)

message = input("Press enter to quit\n\n")