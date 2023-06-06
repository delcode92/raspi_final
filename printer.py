import os, time
from escpos.printer import Usb
from configparser import ConfigParser
from datetime import datetime




def getPath(fileName):
    path = os.path.dirname(os.path.realpath(__file__))
    
    return '/'.join([path, fileName])


def ticket():
    file = getPath("config.cfg")
    config = ConfigParser()
    config.read(file)

    vid = 0x0483
    pid = 0x5840
    in_ep = 0x81
    out_ep = 0x03
    location = config['ID']['LOKASI']
    company = config['ID']['PERUSAHAAN']
    gate_num = config['POSISI']['PINTU']
    gate_name = config['POSISI']['NAMA']
    vehicle_type = config['POSISI']['KENDARAAN']
    footer1 = config['KARCIS']['FOOTER1']
    footer2 = config['KARCIS']['FOOTER2']
    footer3 = config['KARCIS']['FOOTER3']
    footer4 = config['KARCIS']['FOOTER4']

    new_time_text = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    p = Usb(idVendor=vid, idProduct=pid, in_ep=in_ep ,out_ep=out_ep)
    # not minified = 0.12198305130004883
    # minified = 0.11823105812072754

    p.set('center')
    p.text(location + "\n" + company + "\n" + "------------------------------------\n\n" + gate_name + " " + gate_num + "\n" + vehicle_type + "\n" + new_time_text + "\n" + "\n" + "\n------------------------------------\n" + footer1 + "\n" + footer2 + "\n" + footer3 + "\n" + footer4 + "\n")
    # p.barcode("{B" + str(1123123123), "UPC-A", height=80, width=2 ,function_type="A")
    p.barcode('1324354657687', 'EAN13', 64, 2, '', '')
    
    # Cut paper
    p.cut()
    p.close()

start_time = time.time()
ticket()
end_time = time.time()
elapsed_time = end_time - start_time

# Print the execution time
print("Execution time: "+elapsed_time +"seconds")


# time_now = datetime.now().strftime("%d%m%Y%H%M%S%f")
# time_now = datetime.now().strftime("%d%m%Y")
# ticket(time_now)
# print(time_now)
