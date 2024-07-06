import uasyncio as asyncio
from machine import Pin, ADC
from time import sleep

DEBOUNCE = 1000
MAX_VALUE = 4095  # equivalent to 3.3 v
TOLERANCE_RANGE = 4

class potenciometer_async():
    def __init__(self, buttonpin = None, enable = True):
        if enable is False:
            self.enabled = False
            return
        else: 
            self.enabled = True
        self.pin = buttonpin

        self.pot = ADC(Pin(buttonpin))
        self.pot.atten(ADC.ATTN_11DB)

        self.pot_value = False
        self._was_pressed = False

        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    async def run(self):
        if not self.enabled:
            return
        while True:
            new_value = int(self.pot.read())
            normalized_value = int(new_value * 100 / MAX_VALUE)
            if self.pin is None or self._are_values_different_enough(new = normalized_value, previous = self.pot_value):
                await asyncio.sleep_ms(10)
                continue

            self.pot_value = normalized_value
            await asyncio.sleep_ms(DEBOUNCE)

            self._was_pressed = True

    def was_pressed(self):
        if not self.enabled:
            return
        if self._was_pressed:
            return True
        return False

    def reset_press(self):
        if not self.enabled:
            return
        self._was_pressed = False

    def _are_values_different_enough(self, new : int, previous : int, tolerance : int =TOLERANCE_RANGE) -> bool :
        if not self.enabled:
            return
        start = previous - tolerance
        end = previous + tolerance
        tolerance_list = list(range(start, end))
        return new in tolerance_list


    async def wait_for_press(self):
        if not self.enabled:
            return
        self.reset_press()
        while True:
            if self.was_pressed():
                self.reset_press()
                break
            else:
                await asyncio.sleep_ms(10)
