import uasyncio as asyncio
from machine import Pin, ADC
from time import sleep

DEBOUNCE = 30
MAX_VALUE = 4095  # equivalent to 3.3 v
TOLERANCE_RANGE = 2

class potenciometer_async():
    def __init__(self, buttonpin = None):
        self.pin = buttonpin

        self.pot = ADC(Pin(buttonpin))
        self.pot.atten(ADC.ATTN_11DB)

        self.pot_value = False
        self._was_pressed = False

        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    async def run(self):
        while True:
            new_value = int(self.pot.read() * 100 / MAX_VALUE)
            if self.pin is None or self._are_values_different_enough(new = new_value, previous = self.pot_value):
                await asyncio.sleep_ms(10)
                continue

            self.pot_value = new_value

            await asyncio.sleep_ms(DEBOUNCE)

            await asyncio.sleep_ms(DEBOUNCE)

            self._was_pressed = True

    def was_pressed(self):
        if self._was_pressed:
            return True
        return False

    def reset_press(self):
        self._was_pressed = False

    def _are_values_different_enough(self, new : int, previous : int, tolerance : int =TOLERANCE_RANGE) -> bool :
        start = previous - tolerance
        end = previous + tolerance
        tolerance_list = list(range(start, end))
        return new in tolerance_list


    async def wait_for_press(self):
        self.reset_press()
        while True:
            if self.was_pressed():
                self.reset_press()
                break
            else:
                await asyncio.sleep_ms(10)
