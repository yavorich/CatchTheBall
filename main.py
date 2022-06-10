import platform
import ctypes
import asyncio
from app import App

# this setting will allow the application window to display normally
if platform.system() == 'Windows':
    ctypes.windll.user32.SetProcessDPIAware()

# define global variables
APP_WIDTH = 1000
APP_HEIGHT = 600


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = App(loop, APP_WIDTH, APP_HEIGHT)
    while True:  # will be terminated by "close" app button
        app.run(game_interval=5e-3, agent_interval=1e-2)
