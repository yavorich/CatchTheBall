import math
import numpy as np
import tkinter as tk

from ball import Ball


class Cannon:
    def __init__(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_reqwidth()
        self.canvas_height = self.canvas.winfo_reqheight()
        self.width = 40
        self.height = 20
        self.angle = 0
        self.color = '#FD5E53'
        self.coords = [(self.height, self.canvas_height - self.height / 2),
                       (self.height, self.canvas_height + self.height / 2),
                       (self.height + self.width, self.canvas_height + self.height / 2),
                       (self.height + self.width, self.canvas_height - self.height / 2)]  # set rectangle coords
        self.id = self.canvas.create_polygon(self.coords, fill=self.color)  # allocate cannon on canvas

    # rotates cannon on required angle
    def rotate(self, root: tk.Tk, angle: int) -> None:
        steps = 40
        for i in np.linspace(self.angle, angle, steps):
            root.after(1, self.rotate_step(i))
            self.canvas.configure(bg="#003300")
            root.update()
        self.angle = angle

    # makes quanted step of rotation
    def rotate_step(self, angle: int) -> None:
        sin = math.sin(math.radians(angle))
        cos = math.cos(math.radians(angle))
        x0 = (self.height / 2) * (1 + sin)
        y0 = self.canvas_height / 2 - (self.height / 2) * cos
        x1 = (self.height / 2) * (1 - sin)
        y1 = self.canvas_height / 2 + (self.height / 2) * cos
        x2 = x1 + self.width * cos
        y2 = y1 + self.width * sin
        x3 = x0 + self.width * cos
        y3 = y0 + self.width * sin
        self.coords = [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
        self.canvas.delete(self.id)
        self.id = self.canvas.create_polygon(self.coords, fill=self.color)

    # makes shot with setting ball coords
    def shot(self, ball: Ball, speed: int) -> None:
        (x0, y0), (x1, y1) = self.coords[2:]
        ball.x, ball.y = (x0 + x1) / 2, (y0 + y1) / 2

        sin = math.sin(math.radians(self.angle))
        cos = math.cos(math.radians(self.angle))

        ball.vx = speed * cos
        ball.vy = speed * sin

        ball.id = ball.draw()
