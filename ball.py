import pickle
from typing import Union
import tkinter as tk


class Ball:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_reqwidth()
        self.canvas_height = self.canvas.winfo_reqheight()
        self.radius = 20
        self.x, self.y = 0, 0
        self.vx, self.vy = 0, 0
        self.speed = 0
        self.timer = 0
        self.step = 0.1
        self.id = self.canvas.create_oval(0, 0, 0, 0, fill=None, width=0)
        self.move_history = []

    def check_border_collision(self) -> None:
        # top border collision
        if self.y <= self.radius:
            self.vy = abs(self.vy)  # set positive speed

        # bottom border collision
        elif self.y >= (self.canvas_height - self.radius):
            self.vy = -abs(self.vy)  # set negative speed

    def move(self, acc: int, step: Union[float, int]) -> None:
        self.check_border_collision()

        self.vy += acc * step  # increase the speed by the amount of acceleration

        x = self.x + self.vx * step  # change x coord
        y = self.y + self.vy * step  # change y coord

        self.canvas.move(self.id, x - self.x, y - self.y)  # move ball on delta
        self.x, self.y = x, y  # reset self coordinates
        self.move_history.append([self.x, self.y])  # store coordinates into list

    def game_over(self) -> bool:
        if self.x >= self.canvas_width + self.radius / 2:  # ball crossed the right border
            self.save_history()
            return True
        return False

    def save_history(self) -> None:
        with open('logs/move_history.pkl', 'wb') as f:
            pickle.dump(self.move_history, f)

    # delete and redraw element
    def draw(self) -> int:
        self.canvas.delete(self.id)
        _id = self.canvas.create_oval(self.x - self.radius / 2,
                                      self.y - self.radius / 2,
                                      self.x + self.radius / 2,
                                      self.y + self.radius / 2, fill="white")
        return _id





