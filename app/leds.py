import asyncio
import time
import neopixel

class NeopixelController:
    def __init__(self, pin, num_pixels):
        self.pixels = neopixel.NeoPixel(pin, num_pixels)
        self.num_pixels = num_pixels
        self.colors = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta':(255,	0, 255)
        }
        self.current_color = "red"
        self._set_headphones_flag = False
        self._rst_headphones_flag = False
        self._set_mic_flag = False
        self._rst_mic_flag = False
        self._heaphone_led_timer = 0
        self._mic_led_timer = 0
        self.mode = 2
        self.delay = 1
    
    def toggle(self):
        if self.pixels[0] == (0, 0, 0):
            self.pixels.fill(self.colors[self.current_color])
        else:
            self.pixels.fill((0, 0, 0))
            
    def change_color(self):
        color_names = list(self.colors.keys())
        current_color_index = color_names.index(self.current_color)
        next_color_index = (current_color_index + 1) % len(self.colors)
        self.current_color = color_names[next_color_index]
        self.pixels.fill(self.colors[self.current_color])

    def set_headphone_led(self):
        self._set_headphones_flag = True
    
    def rst_headphone_led(self):
        self._rst_headphones_flag = True

    def set_mic_led(self):
        self._set_mic_flag = True
    
    def rst_mic_led(self):
        self._rst_mic_flag = True

    def set_brightness(self, brightness):
        self.pixels.brightness = float(brightness)
    
    def get_brightness(self):
        return self.pixels.brightness
        
    def off(self):
        self.pixels.fill((0, 0, 0))
        
    def on(self):
        self.pixels.fill(self.colors[self.current_color])

    def set_color(self, color):
        self.current_color = color
    
    def get_color(self):
        return self.current_color
    
    def set_mode(self, mode):
        self.mode = int(mode)

    def get_mode(self):
        return self.mode
    
    async def run(self):
        while True:

            if self.mode == 0:
                self._set_headphones_flag = False
                self._rst_headphones_flag = False
                self._set_mic_flag = False
                self._rst_mic_flag = False

            if self._set_headphones_flag:
                self._heaphone_led_timer = time.monotonic()
                self.pixels[0] = (0, 0, 0)
                self.pixels[1] = self.colors[self.current_color]
                self._set_headphones_flag = False
            
            if self._rst_headphones_flag:
                self._heaphone_led_timer = time.monotonic()
                self.pixels[1] = (0, 0, 0)
                self.pixels[0] = self.colors[self.current_color]
                self._rst_headphones_flag = False

            if self._set_mic_flag:
                self._mic_led_timer = time.monotonic()
                self.pixels[3] = (0, 0, 0)
                self.pixels[2] = self.colors[self.current_color]
                self._set_mic_flag = False
            
            if self._rst_mic_flag:
                self._mic_led_timer = time.monotonic()
                self.pixels[2] = (0, 0, 0)
                self.pixels[3] = self.colors[self.current_color]
                self._rst_mic_flag = False

            if self.mode == 2:
                if (self._heaphone_led_timer + self.delay) <  time.monotonic():
                    self.pixels[0] = (0, 0, 0)
                    self.pixels[1] = (0, 0, 0)

                if (self._mic_led_timer + self.delay) < time.monotonic():
                    self.pixels[2] = (0, 0, 0)
                    self.pixels[3] = (0, 0, 0)

            await asyncio.sleep_ms(1)