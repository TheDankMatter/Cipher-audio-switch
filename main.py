import asyncio
from app.audio_switch import AudioSwitch

global audio_switch
audio_switch = AudioSwitch()

asyncio.run(audio_switch.run())