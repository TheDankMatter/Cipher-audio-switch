import board
import asyncio
import foamyguy_nvm_helper as nvm_helper
from app.web_server import WebServer
from app.relay import LatchingRelay
from app.button import Button
from app.leds import NeopixelController
from WIFI_CONFIG import credentials

class AudioSwitch:
    def __init__(self):
        self._initialize_variables()
        self._initialize_buttons()
        self._initialize_relays()
        self._initialize_leds()
        #self.reset_settings()
        self.read_state_from_nvm()
        #self.set_relays()
        #status led pin = board.IO1

    def _initialize_buttons(self):
        button_pins = [board.IO39, board.IO37, board.IO3]
        self.buttons = [Button(pin) for pin in button_pins]
        self.button1 = self.buttons[0]
        self.button2 = self.buttons[1]
        self.button3 = self.buttons[2]

    def _initialize_variables(self):
        self.server = None
        if credentials["ssid"] != "put your ssid here" and credentials["password"] != "put your WIFI password here":
            self.server = WebServer(self,credentials["ssid"], credentials["password"])
        self.button_actions = {
            0 : lambda: None,
            1 : self.switch_relays,
            2 : self.switch_headphones,
            3 : self.switch_microphone
        }
    
    def _initialize_leds(self):
        self.indicator_leds = NeopixelController(board.IO12, 4)

    def _initialize_relays(self):
        self.relays = []
        self.relays.append(LatchingRelay(board.IO5, board.IO7, group = 0))
        self.relays.append(LatchingRelay(board.IO9, board.IO11, group = 0))
        self.relays.append(LatchingRelay(board.IO33, board.IO35, group = 1))
        self.relays.append(LatchingRelay(board.IO16, board.IO18, group = 1))

    def set_relays(self):
        for relay in self.relays:
            relay.set()
    
    def rst_relays(self):
        for relay in self.relays:
            relay.rst()

    def switch_relays(self):
        for relay in self.relays:
            relay.switch()

    def button_disabled(self):
        return
    
    def switch_headphones(self):
        for relay in self.relays:
            if relay.group == 0:
                relay.switch()
    
    def switch_microphone(self):
        for relay in self.relays:
            if relay.group == 1:
                relay.switch()

    def change_indicator_leds_color(self, color):
        self.indicator_leds.set_color(color)
        self.save_state_to_nvm()
    
    def get_indicator_leds_color(self):
        return self.indicator_leds.get_color()
    
    def get_indicator_leds_brightness(self):
        return self.indicator_leds.get_brightness()
    
    def get_indicator_leds_mode(self):
        return self.indicator_leds.get_mode()
    
    def get_side_button_mode(self):
        return self.button3.get_mode()
    
    def get_button1_mode(self):
        return self.button1.get_mode()
    
    def get_button2_mode(self):
        return self.button2.get_mode()

    def reset_settings(self):
        self.status_led_on = True
        self.status_led_brightness = 1
        self.indicator_leds.set_brightness(1)
        self.indicator_leds.set_color("cyan")
        #(disabled = 0, always on = 1, turn off after a delay = 2
        self.indicator_leds.set_mode(2)
        #(disabled = 0, switch all = 1, switch headphones = 2, switch microphone = 3)
        self.button1.set_mode(1)
        self.button2.set_mode(1)
        self.button3.set_mode(1)
        self.save_state_to_nvm()

    def save_state_to_nvm(self):
        data = {
            "sts_led_on": self.status_led_on,
            "sts_led_brightness": self.status_led_brightness,
            "leds_brightness": self.indicator_leds.get_brightness(),
            "leds_color": self.indicator_leds.get_color(),
            "leds_mode": self.indicator_leds.get_mode(),
            "button1": self.button1.get_mode(),
            "button2": self.button2.get_mode(),
            "button3": self.button3.get_mode()
        }
        nvm_helper.save_data(data, test_run=False, verbose=True)

    def read_state_from_nvm(self):
        try:
            data = nvm_helper.read_data()
            self.status_led_on          = data["sts_led_on"]
            self.status_led_brightness  = data["sts_led_brightness"]
            self.indicator_leds.set_brightness(data["leds_brightness"])
            self.indicator_leds.set_color(data["leds_color"])
            self.indicator_leds.set_mode(data["leds_mode"])
            self.button1.set_mode(data["button1"])
            self.button2.set_mode(data["button2"])
            self.button3.set_mode(data["button3"])
        except Exception as e:
            print(e)
            self.reset_settings()

    def set_data(self, leds_color, leds_brightness, leds_mode, side_button_mode, remote_button1_mode, remote_button2_mode):
        self.indicator_leds.set_color(leds_color)
        self.indicator_leds.set_brightness(leds_brightness)
        self.indicator_leds.set_mode(leds_mode)
        self.button1.set_mode(remote_button1_mode)
        self.button2.set_mode(remote_button2_mode)
        self.button3.set_mode(side_button_mode)
        self.save_state_to_nvm()

    async def _subroutine(self):
        headphone_relays_state = self.relays[0].is_set
        mic_relays_state = self.relays[2].is_set
        while True:
            #scan buttons
            for button in self.buttons:
                button.update()
                if button.pressed:
                    self.button_actions[button.action]()
            
            #manage leds
            if self.relays[0].is_set != headphone_relays_state:
                if self.relays[0].is_set:
                    self.indicator_leds.set_headphone_led()
                    print("set headphone led triggered ")
                else: 
                    self.indicator_leds.rst_headphone_led()
                    print("rst headphone led triggered ")
            headphone_relays_state = self.relays[0].is_set

            if self.relays[2].is_set != mic_relays_state:
                if self.relays[2].is_set:
                    self.indicator_leds.set_mic_led()
                else:
                    self.indicator_leds.rst_mic_led()
            mic_relays_state = self.relays[2].is_set
            await asyncio.sleep_ms(1)

    async def run(self):
        tasks = []
        for relay in self.relays:
            tasks.append(asyncio.create_task(relay.run()))
        tasks.append(asyncio.create_task(self.indicator_leds.run()))
        tasks.append(asyncio.create_task(self._subroutine()))
        try:
            tasks.append(asyncio.create_task(self.server.run()))
        except:
            pass
        await asyncio.gather(*tasks)