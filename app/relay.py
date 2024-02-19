import digitalio
import asyncio

class LatchingRelay:
    def __init__(self, pin_set, pin_rst, delay = 0.004, group = 0):
        #delay 0.004
        self._pin_set = digitalio.DigitalInOut(pin_set)
        self._pin_rst = digitalio.DigitalInOut(pin_rst)
        self._pin_set.direction = digitalio.Direction.OUTPUT
        self._pin_rst.direction = digitalio.Direction.OUTPUT
        self._pin_set.value = False
        self._pin_rst.value = False
        self.delay = delay 
        self.group = group
        self.is_set = False
        self._set_flag = False
        self._rst_flag = False
    
    def set(self):
        self._set_flag = True
        #self._set_flag = False
    
    async def _set(self):
        self._pin_set.value = True
        print("_set before delay")
        await asyncio.sleep(self.delay)
        print("_set after delay")
        self._pin_set.value = False
        self.is_set = True
    
    def rst(self):
        self._rst_flag = True

    async def _rst(self):
        self._pin_rst.value = True
        await asyncio.sleep(self.delay)
        self._pin_rst.value = False
        self.is_set = False
    
    def switch(self):
        #print("Switch relay triggered")
        if (self.is_set == True):
            print("rst triggered")
            self.rst()
        else:
            print("set triggered")
            self.set()

    async def run(self):
        while True:
            if self._set_flag:
                self._set_flag = False
                self._pin_set.value = True
                await asyncio.sleep_ms(4)
                self._pin_set.value = False
                self.is_set = True
            if self._rst_flag:
                self._rst_flag = False
                self._pin_rst.value = True
                await asyncio.sleep_ms(4)
                self._pin_rst.value = False
                self.is_set = False
            await asyncio.sleep_ms(1)