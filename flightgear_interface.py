from _socket import SO_REUSEADDR, SOL_SOCKET
from libs.FlightGear import FlightGear
import sys
from libs.SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import subprocess
from threading import Thread, Event
from multiprocessing import Process, freeze_support
import http.server
import socketserver
import os,time
from datetime import datetime
import shutil

flightgear_cc_port = 8888
flightgear_ws_port = 8778
flightgear_server = "127.0.0.1"
flightgear_server_port = 5555
flightgear_process = None
log = False
fg = None
fg_connected = False
child_process = None
what_to_log = ""
log_filename = "log.csv"
flightgear_path = "C:\Program Files\FlightGear 2020.3"
cancel_logger_instance = None

# orientation = fg['/orientation[0]/alpha-deg']
# self.sendMessage "Alpha Deg %.5f" % (fg['/orientation[0]/alpha-deg'])

def get(parent, property):
    return str(fg["/" + parent + "[0]/" + property])


def handle_request(what):
    #
    # POSITION & GPS
    #
    if what == "altitude":
        return get("position", "altitude-ft")
    elif what == "odometer":
        return get("instrumentation[0]/gps", "odometer")
    #
    # ORIENTATION
    #
    elif what == "pitch":
        return get("orientation", "pitch-deg")
    elif what == "heading":
        return get("orientation", "heading-deg")
    elif what == "roll":
        return get("orientation", "roll-deg")
    elif what == "alpha":
        return get("orientation", "alpha-deg")
    elif what == "beta":
        return get("orientation", "beta-deg")
    elif what == "yaw":
        return get("orientation", "yaw-deg")
    elif what == "path":
        return get("orientation", "path-deg")
    elif what == "roll-rate":
        return get("orientation", "roll-rate-degps")
    elif what == "pitch-rate":
        return get("orientation", "pitch-rate-degps")
    elif what == "yaw-rate":
        return get("orientation", "yaw-rate-degps")
    elif what == "side-slip":
        return get("orientation", "side-slip-deg")
    elif what == "track":
        return get("orientation", "track-deg")
    elif what == "p-body":
        return get("orientation", "p-body")
    elif what == "q-body":
        return get("orientation", "p-body")
    elif what == "r-body":
        return get("orientation", "p-body")
    #
    # CONTROL SURFACES
    #
    elif what == "aileron":
        return get("controls[0]/flight", "aileron")
    elif what == "aileron-trim":
        return get("controls[0]/flight", "aileron-trim")
    elif what == "elevator":
        return get("controls[0]/flight", "elevator")
    elif what == "elevator-trim":
        return get("controls[0]/flight", "elevator-trim")
    elif what == "rudder":
        return get("controls[0]/flight", "rudder")
    elif what == "rudder-trim":
        return get("controls[0]/flight", "rudder-trim")
    elif what == "flaps":
        return get("controls[0]/flight", "flaps")
    elif what == "wing-sweep":
        return get("controls[0]/flight", "wing-sweep")
    #
    # VELOCITIES
    #
    elif what == "vertical-speed":
        return get("velocities", "vertical-speed-fps")
    elif what == "airspeed":
        return get("velocities", "airspeed-kt")
    elif what == "groundspeed":
        return get("velocities", "groundspeed-kt")
    elif what == "glideslope":
        return get("velocities", "glideslope")
    elif what == "mach":
        return get("velocities", "mach")
    elif what == "u":
        return get("fdm[0]/jsbsim[0]/velocities", "u-fps")
    elif what == "v":
        return get("fdm[0]/jsbsim[0]/velocities", "v-fps")
    elif what == "w":
        return get("fdm[0]/jsbsim[0]/velocities", "w-fps")
    elif what == "p":
        return get("fdm[0]/jsbsim[0]/velocities", "p-rad_sec")
    elif what == "q":
        return get("fdm[0]/jsbsim[0]/velocities", "q-rad_sec")
    elif what == "r":
        return get("fdm[0]/jsbsim[0]/velocities", "r-rad_sec")
    #
    # ACCELERATIONS
    elif what == "u-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "udot-ft_sec2")
    elif what == "v-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "vdot-ft_sec2")
    elif what == "w-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "wdot-ft_sec2")
    elif what == "p-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "pdot-rad_sec2")
    elif what == "q-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "qdot-rad_sec2")
    elif what == "r-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "rdot-rad_sec2")
    #
    #
    # ENGINE, THRUST & WEIGHT
    #
    elif what == "rpm":
        return get("engines[0]/engine", "rpm")
    elif what == "prop-thrust":
        return get("engines[0]/engine", "prop-thrust")
    elif what == "thrust":
        return get("engines[0]/engine", "thrust-lbs")
    elif what == "torque":
        return get("engines[0]/engine", "torque-ftlb")
    elif what == "fuel-consumed":
        return get("engines[0]/engine", "fuel-consumed-lbs")
    elif what == "weight":
        return get("fdm[0]/jsbsim[0]/inertia", "weight-lbs")
    #
    # AERODYNAMIC COEFFICIENTS
    #
    elif what == "CDo":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDo")
    elif what == "CDDf":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDDf")
    elif what == "CDwbh":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDwbh")
    elif what == "CDDe":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDDe")
    elif what == "CDbeta":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDbeta")
    elif what == "CLwbh":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLwbh")
    elif what == "CLDf":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLDf")
    elif what == "CLDe":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLDe")
    elif what == "CLadot":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLadot")
    elif what == "CLq":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLq")
    elif what == "cl-squared":
        return get("fdm[0]/jsbsim[0]/aero", "cl-squared")
    elif what == "kCDge":
        return get("fdm[0]/jsbsim[0]/aero[0]/function", "kCDge")
    elif what == "kCLge":
        return get("fdm[0]/jsbsim[0]/aero[0]/function", "kCLge")
    #
    # FUEL WEIGHT
    #
    elif what == "fuel-tank-1":
        return str(fg["/fdm[0]/jsbsim[0]/propulsion[0]/tank[0]/" + "contents-lbs"])
    elif what == "fuel-tank-2":
        return str(fg["/fdm[0]/jsbsim[0]/propulsion[0]/tank[1]/" + "contents-lbs"])
    #
    # DEFAULT - NOT FOUND
    #
    else:
        return str("error:Requested parameter not found")


def handle_log(interval, csv):
    global log_filename

    if fg_connected is not None and fg_connected:

        #
        # SET FUEL VALUE
        #
        fg["/fdm[0]/jsbsim[0]/propulsion[0]/tank[0]/" + "contents-lbs"] = 160
        fg["/fdm[0]/jsbsim[0]/propulsion[0]/tank[1]/" + "contents-lbs"] = 160

        ##
        log_filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S') + ".csv"
        csv = "".join(csv.split())
        parameters = csv.split(",")
        logging_worker(interval, csv, parameters)
        values = []
        for what in parameters:
            values.append(str(handle_request(what)))
        print("Logging_started" + ",".join(values))
        return str("Parameter logging started.")
    else:
        return str("error:Please connect to FlightGear before sending commands")

def call_repeatedly(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)

    Thread(target=loop).start()
    return stopped.set


def write_param_to_file(parameters):
    global log_filename
    values = []
    for what in parameters:
        values.append(str(handle_request(what)))
    with open(log_filename, "a") as log_file:
        param_str = ",".join(values)
        # self.sendMessage "[INFO] Written to log:" + param_str
        log_file.write(param_str + "\n")


def logging_worker(interval, csv, parameters):
    global what_to_log
    global log_filename
    global cancel_logger_instance
    print('Starting to log')
    if not os.path.exists("logs"):
        os.makedirs("logs")
    os.chdir("logs")
    with open(log_filename, "a") as log_file:
        log_file.write(csv + "\n")
    cancel_logger_instance = call_repeatedly(float(interval), write_param_to_file, parameters)


def cancel_logger():
    cancel_logger_instance()
    return str("Logging has been terminated")

class FG_com():
    def __init__(self,debug=True):
        self.debug=debug

    def sendMessage(self,msg):
        if self.debug==True:
            print(msg)
    
    def get_param(self,param):
        try:
            res=handle_request(param)
        except WindowsError as err:
            if err.winerror==10054:
                sys.exit()
        except Exception as err:
            self.sendMessage(err)
            res=None
        
        return res

    def start(self):
        self.handle_message("start fg")
    
    def quit(self):
        fg.quit()
        sys.exit()
    def connect(self):
        self.handle_message("connect fg")

    def connect_and_wait_until_ready(self):
        global fg_connected
        ready=False
        while not fg_connected:
            self.connect()
        while not ready:
            res=self.get_param("roll")
            if res:
                ready=True


    def handle_message(self,data):
        global fg
        global child_process
        global flightgear_path
        global fg_connected
        fg_connected = fg is not None and fg_connected
        
        if data == "connect fg":
            if not fg_connected:
                try:
                    fg = FlightGear(flightgear_server, flightgear_server_port)
                    self.sendMessage('Connected to FlightGear via telnet on port ' + str(flightgear_server_port))
                    self.sendMessage(str("Connected to FlightGear via telnet on port 9000"))
                    fg_connected = True
                except Exception as e:
                    self.sendMessage(e)
                    self.sendMessage(str("error:Cannot connect to FlightGear. Try the start command."))
            else:
                self.sendMessage(str("Already connected to FlightGear"))
                fg_connected = True
        
        elif data == "disconnect fg":
            fg.quit()
            fg_connected = False
            self.sendMessage('Disconnected from FlightGear ')
            self.sendMessage(str("Disconnected from FlightGear"))
        
        elif data == "exit":
            #http_process.terminate()
            #ws_process.terminate()
            sys.exit()
        
        elif data.startswith("set_path:"):
            try:
                input_cmd_str = data.replace("set_path:", "")
                if input_cmd_str is not None:
                    if input_cmd_str != "":
                        flightgear_path = input_cmd_str
                try:
                    os.remove(flightgear_path + "\\data\\Aircraft\\c172p\\splash.png")
                except Exception:
                    pass

                shutil.copy("splash.png", flightgear_path + "\\data\\Aircraft\\c172p\\")
                self.sendMessage(str("FlightGear path has been set."))
            except Exception as err:
                self.sendMessage(type(err))
                self.sendMessage(err.args)
                self.sendMessage(err)
                pass
        
        elif data == "start fg":
            # command = '"' + flightgear_path + '\\bin\\fgfs.exe" --fg-root="' + flightgear_path +'\data" --fg-scenery="' + flightgear_path + '\data\Scenery"; --aircraft=Cub --disable-random-objects --prop:/sim/rendering/random-vegetation=false --disable-ai-models --disable-ai-traffic --disable-real-weather-fetch --geometry=800x600 --bpp=32 --disable-terrasync --timeofday=noon --disable-fgcom --telnet=socket,out,30,localhost,5555,udp;'
            try:
                subprocess.Popen([flightgear_path + '\\bin\\fgfs.exe',
                                  '--fg-root=' + flightgear_path + '\\data',
                                  '--fg-scenery=' + flightgear_path + '\\data\\Scenery',
                                  '--aircraft=c172p',
                                  '--disable-random-objects',
                                  '--prop:/sim/rendering/random-vegetation=false',
                                  '--disable-ai-models',
                                  '--disable-ai-traffic',
                                  '--disable-real-weather-fetch',
                                  '--geometry=800x600',  # DISPLAY RESOLUTION
                                  '--model-hz=120'  # FREQUENCY OF THE FDM
                                  '--bpp=32',
                                  '--wind=0@0',  # WIND SPEED AND DIRECTION
                                  '--fog-fastest',
                                  '--turbulence=0',
                                  '--disable-terrasync',
                                  '--timeofday=noon',
                                  '--disable-fgcom',
                                  '--telnet=socket,out,60,localhost,5555,udp'  # TELNET SERVER CONFIGURATION
                                  ])
            except Exception as err:
                self.sendMessage(type(err))
                self.sendMessage(err.args)
                self.sendMessage(err)
            self.sendMessage(str("FlightGear has been started."))
        
        elif data.startswith("log:"):
            if fg_connected:
                input_cmd_str = data.replace("log:", "")
                input_cmd_str = input_cmd_str.split(":")
                self.sendMessage(handle_log(input_cmd_str[0], input_cmd_str[1]))
            else:
                self.sendMessage(str("error:Please connect to FlightGear before sending commands"))
        
        elif data == "stop_log":
            self.sendMessage(cancel_logger())
        else:
            if fg_connected:
                self.sendMessage(handle_request(data))
            else:
                self.sendMessage(str("error:Please connect to FlightGear before sending commands"))





if __name__ == "__main__":
    fgcom=FG_com()
    fgcom.handle_message("start fg")
    time.sleep(40)
    fgcom.handle_message("connect fg")
    while(True):
        print(fgcom.get_param("roll-rate"))







