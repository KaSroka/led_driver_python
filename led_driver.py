import asyncio

ESCAPE_BACKGROUND_TEMPLATE = "\x01\x1b[48;2;{};{};{}m\x02"
ESCAPE_RESET = "\x01\x1b[0m\x02"

def print_intensity(intensity):
    intensity = round(intensity * 255)
    print(f"New intensity {ESCAPE_BACKGROUND_TEMPLATE.format(intensity, intensity, 0)}  {ESCAPE_RESET} = {intensity}")

class PulseEffect:
    def __init__(self, off, period, repeat):
        self.refresh_interval = 0.1
        self.on_time = off
        self.off_time = period - off
        self.on_ticks = round(self.on_time / self.refresh_interval)
        self.off_ticks = round(self.off_time / self.refresh_interval)
        self.repeat = repeat
        self.handle = None

    def start(self):
        self.handle = asyncio.create_task(self.run())

    async def run(self):
        while True:
            for i in range(1, self.on_ticks + 1):
                print_intensity(i * self.refresh_interval / self.on_time)
                await asyncio.sleep(self.refresh_interval)
            for i in range(1, self.off_ticks + 1):
                print_intensity(1 - i * self.refresh_interval / self.off_time)
                await asyncio.sleep(self.refresh_interval)
            if not self.repeat:
                return

    async def stop(self):
        if self.handle:
            self.handle.cancel()
            try:
                await self.handle
            except asyncio.CancelledError:
                pass

class BlinkEffect:
    def __init__(self, off, period, repeat):
        self.on_time = off
        self.off_time = period - off
        self.repeat = repeat
        self.handle = None

    def start(self):
        self.handle = asyncio.create_task(self.run())

    async def run(self):
        while True:
            print_intensity(1.0)
            await asyncio.sleep(self.on_time)

            print_intensity(0.0)
            await asyncio.sleep(self.off_time)

            if not self.repeat:
                return

    async def stop(self):
        if self.handle:
            self.handle.cancel()
            try:
                await self.handle
            except asyncio.CancelledError:
                pass

class LedEffectProcessor:
    def __init__(self):
        self.curr_eff = None

    async def start_effect(self, new_effect):
        if self.curr_eff:
            await self.curr_eff.stop()

        self.curr_eff = new_effect
        self.curr_eff.start()

async def main():
    p = LedEffectProcessor()
    await p.start_effect(BlinkEffect(1, 2, False))
    await asyncio.sleep(5)
    await p.start_effect(PulseEffect(1, 2, True))
    await asyncio.sleep(5)
    await p.start_effect(PulseEffect(0.1, 0.2, False))
    await asyncio.sleep(1)
    await p.start_effect(PulseEffect(1, 1, False))
    await asyncio.sleep(5)
    await p.start_effect(PulseEffect(0, 1, False))
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())