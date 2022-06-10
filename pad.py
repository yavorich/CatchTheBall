import tkinter as tk


class Pad:
    def __init__(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas
        self.canvas_width = self.canvas.winfo_reqwidth()
        self.canvas_height = self.canvas.winfo_reqheight()
        self.width = 15
        self.height = 40
        self.id = self.canvas.create_line(self.canvas_width-self.width/2, 0, self.canvas_width-self.width/2,
                                          self.height, width=self.width, fill="yellow")

        self.y = self.height // 2  # allocate in center

    def move(self, y: float) -> None:
        if self.y + y > self.canvas_height - self.height // 2:  # check bottom border
            self.canvas.move(self.id, 0, self.canvas_height - self.height // 2 - self.y)
            self.y = self.canvas_height - self.height // 2

        elif self.y + y < self.height // 2:  # check top border
            self.canvas.move(self.id, 0, self.y - self.height // 2)
            self.y = self.height // 2

        else:
            self.canvas.move(self.id, 0, y)
            self.y += y



