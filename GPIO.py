import RPi.GPIO as GPIO
import sys, socket, select, random, os, re, json, logging

from logging.handlers import TimedRotatingFileHandler
from time import sleep
from datetime import datetime
from _thread import start_new_thread
from escpos.printer import Usb
from configparser import ConfigParser


class GPIOHandler:
    def __init__(self) -> None:
        
        # init for debug
        self.initDebug()
        
        # global variable
        self.led1, self.led2, self.led3, self.gate = 8,10,11,18
        self.loop1, self.loop2, self.button = 12,13,7

        self.stateLoop1, self.stateLoop2, self.stateButton, self.stateGate, self.setDate, self.bypass_print = False, False, False, False, False, False
        
        # read config file
        # file = self.getPath("config.cfg")
        self.config = ConfigParser()
        self.config.read("/home/pi/config.cfg")

        # buat koneksi socket utk GPIO
        host = sys.argv[1]
        port = int(sys.argv[2])
        
        self.gpio_stat = False
        self.conn_server_stat = False
        # start_new_thread( self.run_GPIO,() )
        
        # self.run_GPIO()
        print("==> run main thread")
        while True:
            if not self.gpio_stat:
                start_new_thread( self.run_GPIO,() )
                start_new_thread( self.rfid_input,() )
                self.gpio_stat = True

            try:
                self.s.sendall( bytes(f"client({host}) connected", 'utf-8') )
            except:
                self.logger.debug("GPIO handshake fail")
                self.conn_server_stat = False
                try:
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.s.connect((host, port))

                    self.s.sendall( bytes(f"GPIO handshake from {host}:{port}", 'utf-8') )
                    self.logger.info("GPIO handshake success")
                    
                    # standby data yg dikirim dari server disini
                    start_new_thread( self.recv_server,() )
                    
                    ########### get server date --> if time not set don't start the raspi
                    while self.setDate==False:
                        self.s.sendall( bytes(f"date#getdate#end", 'utf-8') )
                        self.logger.info("get date from server ... ")
                        sleep(5)
                    ###########################

                    # run input RFID thread
                    # start_new_thread( self.rfid_input,() )
                    # self.run_GPIO()
                    self.conn_server_stat = True
                except Exception as e:
                    self.conn_server_stat = False
                    self.logger.info("GPIO handshake fail")
                    self.logger.error(str(e))
        
                sleep(5)

    def initDebug(self):
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)
        self.logfile_path = "/home/pi/log_file.log"

        # our first handler is a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler_format = '%(levelname)s: %(message)s'
        console_handler.setFormatter(logging.Formatter(console_handler_format))

        # start logging and show messages

        # the second handler is a file handler
        file_handler = logging.FileHandler(self.logfile_path)
        file_handler.setLevel(logging.INFO)
        file_handler_format = '%(asctime)s | %(levelname)s | %(lineno)d: %(message)s'
        file_handler.setFormatter(logging.Formatter(file_handler_format))
        
        # clear log file every 1 day
        rotate = TimedRotatingFileHandler('sample.log', when='D', interval=1, backupCount=0, encoding=None, delay=False, utc=False)
        
        self.logger.addHandler(rotate)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def getPath(self,fileName):
        path = os.path.dirname(os.path.realpath(__file__))
        
        return '/'.join([path, fileName])


    def print_barcode(self,barcode, status_online=True):
        
        vid = int( self.config['PRINTER']['VID'], 16 )
        pid = int( self.config['PRINTER']['PID'], 16 )
        in_ep = int( self.config['PRINTER']['IN'], 16 )
        out_ep = int( self.config['PRINTER']['OUT'], 16 )
        location = self.config['ID']['LOKASI']
        company = self.config['ID']['PERUSAHAAN']
        gate_num = self.config['POSISI']['PINTU']
        gate_name = self.config['POSISI']['NAMA']
        vehicle_type = self.config['POSISI']['KENDARAAN']
        footer1 = self.config['KARCIS']['FOOTER1']
        footer2 = self.config['KARCIS']['FOOTER2']
        footer3 = self.config['KARCIS']['FOOTER3']
        footer4 = self.config['KARCIS']['FOOTER4']

        new_time_text = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        p = Usb(vid, pid , timeout = 0, in_ep = in_ep, out_ep = out_ep)
        # Print text
        p.set('center')
        p.text(location + "\n")
        p.text(company + "\n")
        p.text("------------------------------------\n\n")
        
        p.text(gate_name + " " + gate_num + "\n")
        p.text(vehicle_type + "\n")
        p.text(new_time_text + "\n")
        
        if status_online==False:
            p.text("**OFFLINE**\n")
        
        p.text("\n")
        
        p.barcode("{B" + str(barcode), "CODE128", height=128, width=3, function_type="B")
        # p.qr("test", size=5)
        # p.barcode('1324354657687', 'EAN13', 64, 3, '', '')

        p.text("\n------------------------------------\n")
        p.text(footer1 + "\n")
        p.text(footer2 + "\n")
        p.text(footer3 + "\n")
        p.text(footer4 + "\n")

        # Cut paper
        p.cut()
        p.close()

        # if offline still open gate after print struct
        if not status_online:
            self.stateButton = True
            self.stateGate = True
            GPIO.output(self.led2,GPIO.HIGH)
            self.logger.info("RELAY ON (Gate Open)")
            GPIO.output(self.gate,GPIO.HIGH)
            sleep(1)
            GPIO.output(self.gate,GPIO.LOW)
            self.logger.info("RELAY OFF")

    def run_GPIO(self):
        print("==> run GPIO thread")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.loop1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.loop2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led1, GPIO.OUT)
        GPIO.setup(self.led2, GPIO.OUT)
        GPIO.setup(self.led3, GPIO.OUT)
        GPIO.setup(self.gate, GPIO.OUT)
        
        while True:
            if GPIO.input(self.loop1) == GPIO.LOW and not self.stateLoop1:
                self.logger.debug("LOOP 1 ON (Vehicle Incoming)")
                self.stateLoop1 = True
                self.bypass_print = True
                self.bypass_rfid = True
                GPIO.output(self.led1,GPIO.HIGH)
                
            elif GPIO.input(self.loop1) == GPIO.HIGH and self.stateLoop1:  
                self.logger.debug("LOOP 1 OFF (Vehicle Start Moving)")
                self.stateLoop1 = False
                self.stateGate = False
                GPIO.output(self.led1,GPIO.LOW)
                # ERROR: [Errno 32] Broken pipe
                
            if GPIO.input(self.button) == GPIO.LOW and GPIO.input(self.loop1) == GPIO.LOW and not self.stateButton and not self.stateGate:
                
                # send datetime to server & self.time_now save to property --> can be called when print
                time_now = datetime.now().strftime("%Y%m%d%H%M%S")
                
                # send barcode and datetime here
                # barcode --> shorten 
                #  2.023.011  - 2.246.060 = 901501
                self.barcode = int(time_now[0:7]) - int(time_now[7:14])
                if self.barcode<0 : self.barcode=self.barcode * -1
                
                dict_txt = 'pushButton#{ "barcode":"'+str(self.barcode)+'", "time":"'+time_now+'", "gate":'+self.config['GATE']['NOMOR']+',"jns_kendaraan":"'+self.config['POSISI']['KENDARAAN']+'", "ip_raspi":"'+self.config['GATE']['IP']+'", "ip_cam":['+self.config['IP_CAM']['IP']+'] }#end'
                self.logger.debug(dict_txt)  

                try:
                    # komen disini
                    print("==> coba print ... stat server: ", self.conn_server_stat)
                    
                    if not self.conn_server_stat:
                        self.print_barcode(self.barcode ,status_online=False)
                        # self.bypass_print = False
                    
                    elif self.conn_server_stat:
                        self.s.sendall( bytes(dict_txt, 'utf-8') )

                except Exception as e:
                    # print("===>bypass print", self.bypass_print)
                    # call print barcode here , with certain parameter
                    # check jika kendaraan sudah lewat loop 1 atau belum ?
                    # jika belum lewat tidak boleh eksekusi kode dibawah
                    # print("===> self.stateLoop1", self.stateLoop1)
                    # if self.bypass_print:
                    #     self.print_barcode(self.barcode ,status_online=False)
                    #     self.bypass_print = False
                    
                    self.logger.error(str(e))
                
            elif GPIO.input(self.button) == GPIO.HIGH and GPIO.input(self.loop1) == GPIO.LOW and self.stateButton:
                self.logger.info("BUTTON OFF")
                self.stateButton = False
                GPIO.output(self.led2,GPIO.LOW)
                                
            if GPIO.input(self.loop2) == GPIO.LOW and not self.stateLoop2:
                self.logger.info("LOOP 2 ON (Vehicle Moving In)")
                self.stateLoop2 = True
                
            elif GPIO.input(self.loop2) == GPIO.HIGH and self.stateLoop2:
                self.logger.info("LOOP 2 OFF (Vehicle In)")
                self.logger.info(".........(Gate Close)")
                self.stateLoop2 = False 
                self.stateGate = False
                                        
            sleep(0.5)

    def rfid_input(self):
        print("===> run rfid thread")
        while True:
            print("...rfid thread ... ")
            # sleep(0.3)
            rfid = input("input RFID: ")
            print("==> nilai rfid: ", rfid)
            
            if rfid != "":
                
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


    def recv_server(self):
        print("===> run recv server thread")
        while True:
            while True:
    
                # maintains a list of possible input streams
                sockets_list = [sys.stdin, self.s]
            
                read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
            
                for socks in read_sockets:
                    if socks == self.s:
                        try:
                            message = socks.recv(1024)
                            message = message.decode("utf-8")

                            if message == "rfid-true":
                                self.logger.info("open Gate Utk Karyawan")

                                GPIO.output(self.gate,GPIO.HIGH)
                                sleep(1)
                                GPIO.output(self.gate,GPIO.LOW)

                            elif message == "rfid-false":
                                self.logger.debug("RFID not match !")

                            elif message == "printer-true":
                                self.logger.debug("print struct here ...")
                                self.print_barcode(str(self.barcode))

                                self.logger.info("BUTTON ON (Printing Ticket)")
                    
                                self.stateButton = True
                                self.stateGate = True
                                GPIO.output(self.led2,GPIO.HIGH)
                                self.logger.info("RELAY ON (Gate Open)")
                                GPIO.output(self.gate,GPIO.HIGH)
                                sleep(1)
                                GPIO.output(self.gate,GPIO.LOW)
                                self.logger.info("RELAY OFF")

                            elif "config#" in message :
                                print("========== change config =============")
                                self.logger.debug("get message ...")
                                message = re.search('config#(.+?)#end', message).group(1)
                                message = json.loads(message)
                                self.logger.debug(message)
                                
                                self.logger.info("write to file ... ")
                                # config = ConfigParser()
                                # self.config.read('config.cfg')

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
                                print("date from server: ", date_time)
                                print(f"sudo date -s '{date_time}'")
                                
                                # set raspi date
                                os.system(f"sudo date -s '{date_time}'")
                                self.setDate = True
                                
                        except Exception as e:
                            self.logger.error(str(e))
                           

obj = GPIOHandler()