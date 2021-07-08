###############################################################################
# Description
#   Python interface to ERASynth Micro signal generator
###############################################################################
import serial
from serial.tools.list_ports import comports
import time
from colorama import init, Fore, Back, Style
init(autoreset=True)

class PyErasynth(object):

    def __init__(self,com_port=64):
        super().__init__()
        self.com_port  = com_port
        self.serif     = -1
        self.freq_hz   = -1
        self.level_dbm = 0xFFFF
        self.is_rf_on  = -1
        # __init__


    def list_com_ports(self):
        '''
        list of currently attached com ports
        this method just returns a list of com ports, but it cannot determine for sure 
        if erasynth device is connected to it
        '''

        if comports:
            com_ports_list = list(comports())
        else:
            print(Fore.RED + 'error:no attached com ports found')
            return []

        print('number of com ports found: %d' % len(com_ports_list))

        com_ports = []

        for port in com_ports_list:
            print('device:"{}" description: "{}"'.format(port.device,port))
            com_ports.append(int(port.device[3:]))

        return com_ports
        # list_com_ports



    def connect(self):

        print('connecting to erasynth at com_port=%d' % self.com_port)

        try:
            self.serif = serial.Serial()

            self.serif.port     = 'COM%d' % self.com_port
            self.serif.timeout  = 10 
            self.serif.baudrate = 9600
            self.rtscts         = True  # enable RTS/CTS flow control per erasynth documentation

            self.serif.open()
            print("serif.open: ",self.serif.isOpen())

            self.serif.write(b'>GH\r\n')

        except Exception as e:
          print(Fore.RED + 'ser_connect exception: {}'.format(e))
          self.serif = -1
          return 1

        return 0
        # connect


    def disconnect(self):

        print('disconnecting erasynth com_port=%d' % self.com_port)

        if self.serif != -1:
            self.serif.close()
            self.serif = -1
            return 0

        return 1
        # disconnect


    def get_freq(self):

        if self.freq_hz == -1:
            print(Fore.RED + 'error getting erasynth freq: not set')
            return -1

        freq_mhz = self.freq_hz/1000000
        print('getting erasynth freq=%d mhz' % (freq_mhz))

        return 0
        # get_freq



    def set_freq(self,freq_mhz):

        self.freq_hz = int(1000000*freq_mhz)
        print('setting erasynth freq=%d mhz' % (freq_mhz))
        self.serif.write(b'>F%d\r\n'  % self.freq_hz)

        time.sleep(0.1)
        # print('update home page')
        self.serif.write(b'>GH\r\n')
        return 0


    # need to turn on 'rf output' before accessing level / amplitude
    def get_level(self):

        if self.level_dbm == 0xFFFF:
            # not sure if can read curent level settings
            print(Fore.RED + 'error getting erasynth level: not set')
            return -1

        print('getting erasynth level=%d dbm' % (self.level_dbm))

        return 0


    def set_level(self,level_dbm):

        self.level_dbm = int(level_dbm)
        print('setting level=%d dbm' % (self.level_dbm))

        self.serif.write(b'>SA%d\r\n' % self.level_dbm)

        time.sleep(0.1)
        # print('update home page')
        self.serif.write(b'>GH\r\n')
        return 0
        # set_level


    # need to turn on 'rf output' before accessing level / amplitude
    def set_rf_output(self,is_rf_on):

        self.is_rf_on = is_rf_on

        if is_rf_on:
            print('rf=on')
            self.serif.write(b'>SF1\r\n')
        else:
            print('rf=off')
            self.serif.write(b'>SF0\r\n')

        time.sleep(1.0)
        # print('update home page')
        self.serif.write(b'>GH\r\n')
             
        return 0
        # set_rf_output


    def get_rf_output(self):

        if self.is_rf_on == -1:
            # not sure if can read curent rf_on settings
            print(Fore.RED + 'error getting erasynth rf_on: not set')
            return -1

        print('getting erasynth rf_on=%d' % (self.is_rf_on))

        return 0
        # get_rf_output


    def vibrate_and_get_temperature(self):

        print('updating device home page')
        self.serif.write(b'>GH\r\n')

        print('testing vibration...')
        for ix in range(10):
            self.serif.write(b'>GV\r\n')
            time.sleep(0.2)

        print('reading temperature')
        self.serif.write(b'>RT\r\n')
        time.sleep(0.1)

        num_waiting = self.serif.inWaiting()

        if num_waiting:
            read_data = self.serif.read(num_waiting)
            print('num_read_bytes {}; data: {}'.format(num_waiting,read_data))

            str1 = read_data.splitlines(False)
            print(str1)
        else:
            print(Fore.RED + 'error: read temperature - zero data')

        # vibrate_and_get_temperature

    # PyErasynth


def test_erasynth_access(com_port):

    print('testing access to erasynth...')

    sg = PyErasynth(com_port)

    detected_com_ports = sg.list_com_ports()

    for detected_com_port in detected_com_ports:
        
        sg.com_port = detected_com_port
        print('\ntesting access to erasynth at com_port=%d ...' % sg.com_port)

        status = sg.connect()
        if status != 0:
            print(Fore.RED + 'connection to erasynth at com[%d] failed' % sg.com_port)
            continue

        sg.vibrate_and_get_temperature()

        for freq in (2400.0, 2500.0): 
            sg.set_freq(freq)
            sg.get_freq()
            time.sleep(1.5)

        print('toggling rf output...')
        for rf_out in (0,1,0,1):
            sg.set_rf_output(rf_out)
            sg.get_rf_output()
            time.sleep(1.5)

        print('toggling rf output...')
        for power in (-10,-50):
            sg.get_level()
            sg.set_level(power)
            time.sleep(1.5)

        print('turning off rf power')
        sg.set_rf_output(0)
        sg.disconnect()


    print(Fore.GREEN + 'test_erasynth_access is complete')
    return 0
    # test_erasynth_access


if __name__ == "__main__":
    com_port = 26
    test_erasynth_access(com_port)


