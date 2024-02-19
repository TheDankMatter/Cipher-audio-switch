import asyncio
import socketpool
import wifi
from adafruit_httpserver import Server, Request, JSONResponse, FileResponse, GET, POST, PUT, DELETE

class WebServer:
    def __init__(self, audio_switch, ssid, password):
        self.audio_switch = audio_switch
        print("Connecting to", ssid)
        wifi.radio.connect(ssid, password)
        print("Connected to", ssid)
        self.pool = socketpool.SocketPool(wifi.radio)
        self.server = Server(self.pool, "/app/web", debug=True)
        self.define_routes()
        self.server.start(str(wifi.radio.ipv4_address))

    def define_routes(self):
        self.server.route("/")(self.base)
        self.server.route("/switch_relays")(self.switch_relays)
        self.server.route("/switch_headphones")(self.switch_headphones)
        self.server.route("/switch_mic")(self.switch_mic)
        self.server.route("/save_data", methods=[POST])(self.save_data)
        self.server.route("/get_data")(self.get_data)

    def base(self, request: Request):
        """
        Serve the default index.html file.
        """
        return FileResponse(request, "index.html")
    
    def switch_relays(self, request: Request):
        self.audio_switch.switch_relays()
        return JSONResponse(request, {"message": "Relays switched"})
    
    def switch_headphones(self, request: Request):
        self.audio_switch.switch_headphones()
        return JSONResponse(request, {"message": "Headphones switched"})
    
    def switch_mic(self, request: Request):
        self.audio_switch.switch_microphone()
        return JSONResponse(request, {"message": "Mic switched"})
    
    def save_data(self, request: Request):
        data = request.json()
        if data is not None:
            print(data)
            self.audio_switch.set_data(data["ledsColor"],
                                       data["ledsBrightness"],
                                       data["ledsMode"],
                                       data["sideButtonMode"],
                                       data["remoteButton1Mode"],
                                       data["remoteButton2Mode"])
            return JSONResponse(request, {"status": "success"})
        else:
            return JSONResponse(request, {"status": "error", "message": "Invalid data"})
    
    def get_data(self, request: Request):
        data = {"ledsColor":self.audio_switch.get_indicator_leds_color(),
                "ledsBrightness":self.audio_switch.get_indicator_leds_brightness(),
                "ledsMode":self.audio_switch.get_indicator_leds_mode(),
                "sideButtonMode":self.audio_switch.get_side_button_mode(),
                "remoteButton1Mode":self.audio_switch.get_button1_mode(),
                "remoteButton2Mode":self.audio_switch.get_button2_mode()}
        print(data)
        return JSONResponse(request, data)

    async def run(self):
        while True:
            try:
                self.server.poll()
            except OSError as error:
                print(error)
                continue
            await asyncio.sleep(0)
