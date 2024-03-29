import RPi.GPIO as GPIO
import sys, socket, select, os, re, json, random
from time import sleep
from datetime import datetime
import threading
from escpos.printer import Usb
from configparser import ConfigParser

class logging:
    def __init__(self, stat) -> None:
        self.stat = stat

    def debug(self, msg):
        if self.stat: print(msg)
    def info(self, msg):
        if self.stat: print(msg)
    def error(self, msg):
        if self.stat: print(msg)

class GPIOHandler:
    def __init__(self) -> None:

        
        # read config file
        print("read config file ...")
        self.config = ConfigParser()
        self.config.read( os.path.expanduser("config.cfg") )


        # init for debug
        print("set logger message ...")
        self.logger = logging( int(self.config['APP']['SHOW_LOGGER']) )


        # global variable
        print("set GPIO pin ... ")
        self.led1, self.led2, self.gate = 8,10,18
        self.threads = 11 #31
        self.connected = 29
        self.restartLed = 32
        self.printerWarning = 32 #36

        # buttons
        self.shutdown = 38
        self.resetPrintCounter = 15
        self.restartService = 40

        self.loop1, self.loop2, self.button = 12,13,7

        self.stateLoop1, self.stateLoop2, self.stateButton, self.stateGate, self.setDate, self.bypass_print, self.bypass_rfid = False, False, False, False, False, False, False

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        # buat koneksi socket utk GPIO
        host = self.config['APP']['SERVER_IP']
        port = int(self.config['APP']['PORT'])




        self.gpio_stat = False
        self.conn_server_stat = False
        self.printer_stat = False
        self.blinking_thread = False
        self.blinking_printer_thread = False
        self.blinking_flag = True


        print("Run main thread ... ")

        ping = self.config['APP']['SERVER_PING_CMD']
        server_ip = self.config['APP']['SERVER_IP']
        optimized = int( self.config['APP']['GPIO_OPTIMIZED'] )
        mt_sleep = int( self.config['APP']['MAIN_THREAD_SLEEP'] )
        socket_timeout = int( self.config['APP']['SOCKET_TIMEOUT'] )

        print("Run network PING thread ... ")

        # network_ping_thread = threading.Thread(target=self.network_ping, args=(ping, server_ip, mt_sleep))
        # network_ping_thread.start()

        while True:

            try:
                
                # 2. send bytes of data string
                self.s.sendall( bytes(f"SOCKET-PING from client ... ", 'utf-8') )
                self.blinking_flag = False
            except Exception as e:
                self.logger.debug("\n\n===> GPIO handshake fail <===\n\n")
                self.logger.debug(str(e) + "\n\n")

                self.conn_server_stat = False
                self.blinking_flag = True
                try:
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.s.settimeout(socket_timeout)
                    self.s.connect((host, port))

                    self.s.sendall( bytes(f"GPIO handshake from {host}:{port}", 'utf-8') )
                    self.logger.info("\n\n===> GPIO handshake success <===\n\n")

                    # standby data yg dikirim dari server disini
                    recv_serv_thread = threading.Thread(target=self.recv_server)
                    recv_serv_thread.start()

                    ########### get server date
                    self.s.sendall( bytes(f"date#getdate#end", 'utf-8') )
                    self.logger.info("get date from server ... ")
                    ###########################

                    self.conn_server_stat = True

                    # ======== connect indicator on ========
                    self.blinking_flag = False
                    GPIO.setup(self.connected, GPIO.OUT)
                    GPIO.output(self.connected,GPIO.HIGH)
                    #======================================


                except Exception as e:
                    # ======== connect indicator off ========
                    if not self.blinking_thread:
                        blink_thread = threading.Thread(target=self.blink)
                        blink_thread.start()
                    #======================================

                    self.conn_server_stat = False
                    self.blinking_flag = True
                    self.logger.info("GPIO handshake fail")
                    self.logger.error(str(e))

            # run threads GPIO and rfid only once
            if not self.gpio_stat:
                lp1 = int(self.config['APP']['USE_LOOP1'])
                if optimized:
                    op_GPIO_thread = threading.Thread(target=self.run_OPTIMIZED_GPIO, args=(lp1,))
                    op_GPIO_thread.start()
                else:
                    old_GPIO_thread = threading.Thread(target=self.run_GPIO)
                    old_GPIO_thread.start()

                try:
                    rfid_input_thread = threading.Thread(target=self.rfid_input)
                    rfid_input_thread.start()
                except Exception as e:
                    print("error thread RFID",str(e))

                self.gpio_stat = True

                # ======== gpio thread and rfid indicator on ========
                GPIO.setup(self.threads, GPIO.OUT)
                GPIO.output(self.threads,GPIO.HIGH)
                #======================================

            sleep(mt_sleep)

    def blinkPrinterWarning(self):
            GPIO.setup(self.printerWarning, GPIO.OUT)
            while True:
                if self.blinking_printer_thread:
                    GPIO.output(self.printerWarning,GPIO.LOW)
                    sleep(0.4)

                    GPIO.output(self.printerWarning,GPIO.HIGH)
                    sleep(0.4)

                elif not self.blinking_printer_thread:
                    GPIO.output(self.printerWarning,GPIO.LOW)

                sleep(0.2)

    def blink(self):

        if self.blinking_flag:
            self.blinking_thread = True
            GPIO.setup(self.connected, GPIO.OUT)

            while True:
                if self.blinking_flag:
                    GPIO.output(self.connected,GPIO.LOW)
                    sleep(0.4)

                    GPIO.output(self.connected,GPIO.HIGH)
                    sleep(0.4)

                sleep(0.2)

    def getPath(self,fileName):
        path = os.path.dirname(os.path.realpath(__file__))
        return '/'.join([path, fileName])

    def print_barcode(self,barcode, status_online=True):

        try:
            location = self.config['ID']['LOKASI']
            company = self.config['ID']['PERUSAHAAN']
            gate_num = self.config['POSISI']['PINTU']
            gate_name = self.config['POSISI']['NAMA']
            vehicle_type = self.config['POSISI']['KENDARAAN']
            footer1 = self.config['KARCIS']['FOOTER1']
            footer2 = self.config['KARCIS']['FOOTER2']
            footer3 = self.config['KARCIS']['FOOTER3']
            footer4 = self.config['KARCIS']['FOOTER4']
            counter = int( self.config['PRINTER']['COUNTER'] )
            max_print = int( self.config['PRINTER']['MAX_PRINT'] )
            vid = int( self.config['PRINTER']['VID'], 16 )
            pid = int( self.config['PRINTER']['PID'], 16 )
            in_ep = int( self.config['PRINTER']['IN'], 16 )
            out_ep = int( self.config['PRINTER']['OUT'], 16 )

            new_time_text = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            self.p = Usb(vid, pid , timeout = 0, in_ep = in_ep, out_ep = out_ep)
            paper_stat = 2

            # plenty of paper
            if paper_stat == 2:
                # Print text
                self.p.set('center', density=0)
                self.p.text(location + "\n" + company + "\n------------------------------------\n" + gate_name + " " + gate_num + " | " + vehicle_type + "\n" + new_time_text + "\n")

                print("\n---------------BARCODE---------------------\n")
                if status_online==False:
                    barcode = "000" + str(barcode) # add 000 for offline barcode
                    # self.p.text("**OFFLINE**\n")

                print(str(barcode))
                print("\n---------------END BARCODE---------------------\n")
                self.p.barcode("{B" + str(barcode), "CODE128", height=50, width=2, function_type="B")

                self.p.text("------------------------------------\n" + footer1 + "\n" + footer2 + "\n" + footer3 + "\n" + footer4)

                # Cut paper
                if int(self.config['APP']['CUT_PAPER']):
                    self.p.cut(mode="FULL")
                self.p.close()


            # if offline still open gate after print struct
            if not status_online:
                self.stateButton = True
                self.stateGate = True
                GPIO.output(self.led2,GPIO.HIGH)
                self.logger.info("RELAY ON (Gate Open)")
                GPIO.output(self.gate,GPIO.HIGH)
                sleep(0.3)
                GPIO.output(self.gate,GPIO.LOW)
                self.logger.info("RELAY OFF")

        except Exception as e:
            print(str(e))

    def restartAPP(self, channel):
        print("restart APP")
        GPIO.output(self.connected,GPIO.LOW)

        # blinking indicator lamp
        c = 0
        while True:
            if c == 3:
                break

            GPIO.output(self.restartLed,GPIO.HIGH)
            sleep(0.3)
            GPIO.output(self.restartLed,GPIO.LOW)
            sleep(0.3)
            c = c + 1

        service_path = "./GPIO_SERVICE"
        # python = sys.executable
        pid = os.getpid()
        print("==> PID: ", pid)

        os.execl(service_path, service_path)

        #subprocess.call([python] + sys.argv)

        #subprocess.call((
         #  './restart.sh',
        #))
        #os.system(self.config['APP']['RESTART_APP_CMD'])

    def resetPrinter(self, channel):
        print("reset PRINTER")

    def run_OPTIMIZED_GPIO(self, loop1):
        print("==> run GPIO thread")

        GPIO.setup(self.loop1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.loop2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.shutdown, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.restartService, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.resetPrintCounter, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.setup(self.led1, GPIO.OUT)
        GPIO.setup(self.led2, GPIO.OUT)
        GPIO.setup(self.gate, GPIO.OUT)
        GPIO.setup(self.restartLed, GPIO.OUT)

        # init var
        press_down = False
        press_up = False
        counter_down = 0
        # counter_up = 0
        gpio_sleep = float(self.config['APP']['GPIO_THREAD_SLEEP'])

        # run restart app & reset printer
        GPIO.add_event_detect(self.restartService, GPIO.FALLING, callback=self.restartAPP, bouncetime=1000)
        GPIO.add_event_detect(self.resetPrintCounter, GPIO.FALLING, callback=self.resetPrinter, bouncetime=1000)

        if loop1:
            while True:

                # kondisi masuk
                if GPIO.input(self.loop1) == GPIO.LOW and GPIO.input(self.button) == GPIO.LOW and not self.printer_stat:

                    # set to True , so  users cannot execute print barcode more than once
                    # just only when self.printer_stat = False, execute all process to print barcode
                    self.printer_stat = True

                    # if server not connect
                    if not self.conn_server_stat:
                        self.logger.debug("server putus")

                        try:
                            time_now = datetime.now().strftime("%H%M%S")

                            self.print_barcode(str(time_now) ,status_online=False)
                            self.logger.debug("by pass print here .... ")
                        except Exception as e:
                            self.logger.info("==> error", str(e))


                    # if server connect
                    elif self.conn_server_stat:
                        time_now = datetime.now().strftime("%Y%m%d%H%M%S")

                        self.barcode = int(time_now[0:7]) - int(time_now[7:14])
                        if self.barcode<0 : self.barcode=self.barcode * -1

                        dict_txt = 'pushButton#{ "barcode":"'+str(self.barcode)+'", "time":"'+time_now+'", "gate":'+self.config['GATE']['NOMOR']+',"jns_kendaraan":"'+self.config['POSISI']['KENDARAAN']+'", "ip_raspi":"'+self.config['GATE']['IP']+'", "ip_cam":['+self.config['IP_CAM']['IP']+'] }#end'
                        self.logger.debug(dict_txt)

                        try:
                            self.s.sendall( bytes(dict_txt, 'utf-8') )
                            sleep(0.5)
                        except Exception as e:
                            self.logger.info(str(e))

                # reset printer_stat
                elif GPIO.input(self.loop1) and self.printer_stat:
                    self.printer_stat = False

                # ================ btn shutdown/reboot/restart APP ==============
                if GPIO.input(self.shutdown) == GPIO.HIGH:
                    counter_down += 1
                    press_down = True
                    print("press down")
                elif GPIO.input(self.shutdown) == GPIO.LOW:

                    if press_down:
                        press_down = False #reset
                        print("press up")
                        press_up = True

                if press_up:
                    press_up = False #reset

                    # if press time more than 3 seconds
                    if counter_down > 6:
                        print("shutdown RASPI")
                        os.system( self.config['APP']['POWEROFF_CMD'] )

                    # if press time less than 3 seconds
                    elif counter_down < 6:
                        # restart APP
                        print("reboot RASPI")
                        os.system(self.config['APP']['REBOOT_CMD'])

                    counter_down = 0
                # =============== end btn shutdown/reboot/ restart APP ==========

                sleep(gpio_sleep)

        else:
            while True:

                # kondisi masuk
                if GPIO.input(self.button) == GPIO.LOW and not self.printer_stat:

                    # set to True , so  users cannot execute print barcode more than once
                    # just only when self.printer_stat = False, execute all process to print barcode
                    self.printer_stat = True

                    # if server not connect
                    if not self.conn_server_stat:
                        self.logger.debug("server putus")

                        try:
                            time_now = datetime.now().strftime("%H%M%S")

                            self.print_barcode(str(time_now) ,status_online=False)
                            self.logger.debug("by pass print here .... ")
                        except Exception as e:
                            self.logger.info("==> error", str(e))


                    # if server connect
                    elif self.conn_server_stat:
                        time_now = datetime.now().strftime("%Y%m%d%H%M%S")

                        self.barcode = int(time_now[0:7]) - int(time_now[7:14])
                        if self.barcode<0 : self.barcode=self.barcode * -1

                        dict_txt = 'pushButton#{ "barcode":"'+str(self.barcode)+'", "time":"'+time_now+'", "gate":'+self.config['GATE']['NOMOR']+',"jns_kendaraan":"'+self.config['POSISI']['KENDARAAN']+'", "ip_raspi":"'+self.config['GATE']['IP']+'", "ip_cam":['+self.config['IP_CAM']['IP']+'] }#end'
                        self.logger.debug(dict_txt)

                        try:
                            self.s.sendall( bytes(dict_txt, 'utf-8') )
                            sleep(0.5)
                        except Exception as e:
                            self.logger.info("==> error", str(e))

                # reset printer_stat
                elif self.printer_stat:
                    self.printer_stat = False

                # ================ btn shutdown /restart ==============
                if GPIO.input(self.shutdown) == GPIO.HIGH:
                    counter_down += 1
                    press_down = True
                    print("press down")
                elif GPIO.input(self.shutdown) == GPIO.LOW:

                    if press_down:
                        press_down = False #reset
                        print("press up")
                        press_up = True

                if press_up:
                    press_up = False #reset

                    # if press time more than 3 seconds
                    if counter_down > 6:
                        print("shutdown")
                        os.system( self.config['APP']['POWEROFF_CMD'] )

                    # if press time less than 3 seconds
                    elif counter_down < 6:
                        # restart APP
                        print("restart APP")
                        os.system(self.config['APP']['RESTART_APP_CMD'])

                    counter_down = 0
                # =============== end btn shutdown/reboot ==========

                sleep(gpio_sleep)

    def network_ping(self, ping_cmd, server_ip, mt_sleep):
        
        while True:
            try:
                # 1. send ping -> always send each ping couple of seconds
                response = os.system(ping_cmd+ " " + server_ip + " > /dev/null 2>&1")

                if response != 0:
                    print("\n\n=========network ping None==========")
                    self.s = None
                    print("============************===============\n\n")

            except Exception as e:
                self.logger.debug("NETWORK PING ERROR: \n")
                self.logger.debug(str(e) + "\n\n")

            # network ping run first -5 seconds before send `SOCKET-PING` data to server
            sleep(mt_sleep-5)

    def rfid_input(self):
        print("===> run rfid thread")
        # rfid_sleep = float(self.config['APP']['RFID_THREAD_SLEEP'])
        filter_rfid = int(self.config['APP']['FILTER_RFID'])
        
        if filter_rfid:
            while True:
                print("rfid thread ... ")
                rfid = input("input RFID: ")

                if rfid != "":
                    print("==> nilai rfid: ", rfid)

                    # send to server
                    try:
                        print("===> server stat: ", self.conn_server_stat)

                        if self.conn_server_stat:
                            self.s.sendall( bytes(f"rfid#{rfid}#end", 'utf-8') )

                        elif not self.conn_server_stat:
                            # still open gate if fail
                            GPIO.output(self.gate,GPIO.HIGH)
                            sleep(1)
                            GPIO.output(self.gate,GPIO.LOW)

                    except Exception as e:
                        self.logger.info("send RFID to server fail")
                        self.logger.error(str(e))

        else:
            while True:
                print("rfid thread ... ")
                rfid = input("input RFID: ")

                if rfid != "":
                    print("==> nilai rfid: ", rfid)
                    self.logger.info("open Gate Utk Karyawan\n\n")

                    GPIO.output(self.gate,GPIO.HIGH)
                    sleep(1)
                    GPIO.output(self.gate,GPIO.LOW)
            

                # sleep(rfid_sleep)

    def recv_server(self):
        print("===> run recv server thread")
        recv_server_sleep = float(self.config['APP']['RECV_SERVER_THREAD_SLEEP'])
        while True:

            # maintains a list of possible input streams
            sockets_list = [sys.stdin, self.s]

            print("\n\n======socket list==========")
            # [
            # <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>, 
            # <socket.socket fd=11, 
                # family=AddressFamily.AF_INET, 
                # type=SocketKind.SOCK_STREAM, 
                # proto=0, 
                # laddr=('192.168.100.173', 51196), 
                # raddr=('192.168.100.171', 65430)
            # >
            # ]
            print(sockets_list)
            print("======end socket list==========\n\n")

            read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
            
            print("\n\n======read_sockets==========")
            print(sockets_list)
            print("======end read_sockets ==========\n\n")

            for socks in read_sockets:
                print("\n\n======checking sockets==========")
                print("socks: ", socks)
                print("self.s: ", self.s)
                print("======end checking sockets ==========\n\n")

                if socks == self.s:
                    try:
                        message = socks.recv(1024 * int(self.config['APP']['BUFFER_MULTIPLY']))
                        message = message.decode("utf-8")

                        print("\n\n\n=message recv=")
                        print(message)
                        print("=====================\n\n\n")

                        if message == "rfid-true":
                            self.logger.info("open Gate Utk Karyawan")

                            GPIO.output(self.gate,GPIO.HIGH)
                            sleep(1)
                            GPIO.output(self.gate,GPIO.LOW)

                        elif message == "rfid-false":
                            self.logger.debug("RFID not match !")

                        elif message == "printer-true":
                            # ubah disini
                            print("\n\n data diterima \n\n")
                            self.logger.debug("\n\n print struct here ...\n\n")

                            # disini bro
                            self.print_barcode(str(self.barcode))
                            self.logger.info("BUTTON ON (Printing Ticket)")

                            self.stateButton = True
                            self.stateGate = True
                            GPIO.output(self.led2,GPIO.HIGH)
                            self.logger.info("RELAY ON (Gate Open)")
                            GPIO.output(self.gate,GPIO.HIGH)
                            sleep(0.5)
                            GPIO.output(self.gate,GPIO.LOW)
                            self.logger.info("RELAY OFF")
                            #self.printer_stat = False


                        elif "config#" in message :
                            print("========== change config =============")
                            self.logger.debug("get message ...")
                            message = re.search('config#(.+?)#end', message).group(1)
                            message = json.loads(message)
                            self.logger.debug(message)

                            self.logger.info("write to file ... ")

                            self.config['ID']['LOKASI'] = message['tempat']
                            self.config['KARCIS']['FOOTER1'] = message['footer1']
                            self.config['KARCIS']['FOOTER2'] = message['footer2']
                            self.config['KARCIS']['FOOTER3'] = message['footer3']

                            with open('config.cfg', 'w') as configfile:
                                self.config.write(configfile)

                            print("==> nama lokasi: ", self.config['ID']['LOKASI'])
                            print("=====================================")

                        elif "date#" in message :
                            date_time = re.search('date#(.+?)#end', message).group(1)
                            print("get-set date from server ...")
                            # print(f"date -s '{date_time}'")

                            # set raspi date
                            os.system(f"{self.config['APP']['SET_DATE_CMD']} '{date_time}'")
                            self.setDate = True
                            sleep(3)
                            self.blinking_flag = False

                    except Exception as e:
                        self.logger.error(str(e))

            sleep(recv_server_sleep)

obj = GPIOHandler()