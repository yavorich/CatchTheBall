import asyncio
import sys
from tkinter import Tk, Canvas, Button
from cannon import Cannon
from ball import Ball
from pad import Pad
from agent import Agent
from random import randint
from typing import Tuple


class App(Tk):
    def __init__(self, loop, width: int, height: int) -> None:
        super().__init__()
        self.loop = loop
        self.width = width
        self.height = height
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.color = "#003300"
        self.bbox = self.get_bbox_coords()  # the area that the agent will track
        self.agent = Agent(self.bbox, self.width, self.height)
        self.init_field()  # initialize game window
        self.set_window_location()  # set window to screen center

    def init_field(self) -> None:
        # set app elements
        self.canvas = Canvas(self, width=self.width, height=self.height, background=self.color)
        self.cannon = Cannon(self.canvas)
        self.ball = Ball(self.canvas)
        self.pad = Pad(self.canvas)

        # create button so we can quit app at any time
        quit_button = Button(self, text="Stop", font=("Comic Sans MS", 14, "bold"), command=self.close)
        quit_button.place(x=10, y=10)

        self.canvas.pack()

        # left line
        self.canvas.create_line(self.cannon.height / 2, 0, self.cannon.height / 2, self.width, fill="white")
        # right line
        self.canvas.create_line(self.width - self.pad.width, 0, self.width - self.pad.width, self.height, fill="white")
        # middle-left line
        self.canvas.create_line(self.width / 3, 0, self.width / 3, self.height, fill="blue", width=5)
        # middle-right line
        self.canvas.create_line(2 * self.width / 3, 0, 2 * self.width / 3, self.height, fill="yellow", width=5)
        # top line
        self.canvas.create_line(0, 0, self.width, 0, fill="black", width=5)
        # bottom line
        self.canvas.create_line(0, self.height, self.width, self.height, fill="black", width=5)

    def set_window_location(self) -> None:
        # left top corner coordinates
        x = (self.screen_width / 2) - (self.width / 2)
        y = (self.screen_height / 2) - (self.height / 2)

        # set window to screen center
        self.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))

        # hide top panel
        self.overrideredirect(True)

    # get coordinates of central third
    def get_bbox_coords(self) -> Tuple:
        x0 = round((self.screen_width / 2) - (self.width / 6))
        y0 = round((self.screen_height / 2) - (self.height / 2))
        x1 = round((self.screen_width / 2) + (self.width / 6))
        y1 = round((self.screen_height / 2) + (self.height / 2))
        return x0, y0, x1, y1

    # async game process
    async def game(self, interval: float) -> None:
        self.cannon.rotate(self, angle=randint(-30, 30))
        self.cannon.shot(self.ball, speed=randint(20, 100))
        while not self.ball.game_over():
            self.ball.move(acc=10, step=0.1)
            self.canvas.configure(bg=self.color)  # reset canvas (otherwise ball is blinking)
            self.update()  # show changes
            await asyncio.sleep(interval)

    # async agent action
    async def process(self, interval: float) -> None:
        while not self.agent.stop:
            self.agent.process_screen()  # analyzing screenshots
            await asyncio.sleep(interval)
        self.agent.simulate()  # calculating final point of ball moving
        asyncio.ensure_future(self.agent.control_pad(self.pad))  # async pad control by agent

    def run(self, game_interval=1e-3, agent_interval=1e-2):
        tasks = [self.loop.create_task(self.game(game_interval)),
                 self.loop.create_task(self.process(agent_interval))]  # game and agent work asynchronously
        wait_tasks = asyncio.wait(tasks)
        self.loop.run_until_complete(wait_tasks)  # run loop
        self.agent.save_history()  # save agent logs
        self.agent.make_video()  # make video from screen images
        self.agent.reset()  # return the agent to its original state

    def close(self):
        self.loop.stop()  # stop loop
        self.destroy()  # quit the tk root
