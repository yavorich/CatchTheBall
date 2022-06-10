import sys
import pickle
import numpy
import numpy as np
from scipy.linalg import lstsq
from PIL import ImageGrab
import cv2 as cv
import asyncio
from typing import Tuple, List

from pad import Pad


class Agent:
    def __init__(self, bbox: Tuple, width: int, height: int) -> None:
        self.bbox = bbox
        self.width = width
        self.height = height
        self.reset()  # set initial values

    def reset(self) -> None:
        self.frame_sequence = []  # list for screenshots
        self.circle_sequence = []  # list for detected circles
        self.simulate_history = []  # list of simulated moving coordinates
        self.ball_radius = None
        self.x, self.y = None, None  # ball coordinates (will be simulated)
        self.vx, self.vy = None, None  # ball speed projections
        self.acc = None  # acceleration
        self.wait = True  # waiting for the ball to hit the area
        self.stop = False  # left the ball area or not

    def process_screen(self) -> None:
        if self.wait or not self.stop:
            frame = np.array(ImageGrab.grab(bbox=self.bbox))  # making a screenshot of predetermined area
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # convert to grayscale
            blur_frame = cv.GaussianBlur(gray_frame, (17, 17), 0)  # bluring image
            ret, thresh_frame = cv.threshold(blur_frame, 127, 255, cv.THRESH_BINARY)  # binary threshold
            circles = self.detect_circles(thresh_frame)  # detecting ball on image

            if circles is not None:
                self.circle_sequence.append(circles[0][0])  # write into circle list
                self.frame_sequence.append(frame)

                if self.wait:
                    self.wait = False  # ball already hit the area

            elif not self.wait:  # ball is not detected, but already hit the area
                self.stop = True  # ball left the area
                self.circle_sequence = np.array(self.circle_sequence, dtype='float')
                self.ball_radius = self.circle_sequence[:, -1].mean()  # set radius as mean of recognized values

    # gets value of parabola function
    def get_value(self, cf: Tuple[float], x: float) -> float:
        value = cf[0] * x**2 + cf[1] * x + cf[2]
        return value

    # gets coefficients of parabola equation using the least squares method
    def get_equation_cf(self, circles: numpy.ndarray):
        # center coords of detected circles
        x = circles[:, 0]
        y = circles[:, 1]

        # create a wireframe array to run the least squares method
        m = np.vstack((x**2, x, np.ones(x.shape[0]))).T
        cf = lstsq(m, y)[0]
        return cf

    def simulate(self) -> None:
        start, end = self.find_max_segment()  # find the longest interval
        circles = self.circle_sequence[start:end]  # limit the list of circles by interval
        cf = self.get_equation_cf(circles)  # get coefs of parabola equation

        self.acc = cf[0] * 2  # acceleration as second derivative of equation
        self.x = circles[-1, 0]  # set start x as last circle x
        self.y = self.get_value(cf, self.x)  # count start y
        self.vx = 1  # const x speed
        self.vy = self.get_value(cf, self.x + self.vx) - self.y  # count y speed

        self.move()  # simulate the moving of the ball

    def detect_circles(self, frame: numpy.ndarray) -> numpy.ndarray:
        circles = cv.HoughCircles(frame, cv.HOUGH_GRADIENT, 1, 100, param1=6, param2=6, minRadius=5,
                                  maxRadius=20)  # OpenCV circle detection function
        if circles is not None:
            circles = np.uint16(np.around(circles))  # round and convert to numpy array
        return circles

    # find the longest interval between bounces (so that it can be described by a single parabola)
    def find_max_segment(self) -> List[int]:
        # catch bounces
        bounces = list(np.where((self.circle_sequence[:, 1] < self.ball_radius * 2) |
                                (self.circle_sequence[:, 1] > self.height - self.ball_radius * 2))[0])
        bounces = [0] + bounces + [len(self.circle_sequence)]  # add first and last index
        distance = np.diff(bounces)  # count lengths of intervals split by bounces
        max_distance_idx = np.where(distance == max(distance))[0][0]  # get longest interval
        max_segment = bounces[max_distance_idx: max_distance_idx + 2]  # get boundaries of interval
        return max_segment

    def game_over(self) -> bool:
        if self.x >= 2 * self.width / 3 - self.ball_radius:  # out of bounds, counting from the tracked frame
            return True
        return False

    # same method as in Ball class, but for simulation
    def check_border_collision(self) -> None:
        if self.y <= self.ball_radius:
            self.vy = abs(self.vy)
        elif self.y >= (self.height - self.ball_radius):
            self.vy = -abs(self.vy)

    # quanted step of full move
    def move_step(self) -> None:
        self.check_border_collision()

        self.vy += self.acc  # increase y speed by acceleration
        x = self.x + self.vx  # increase x coord by x speed
        y = self.y + self.vy  # increase x coord by y speed

        self.x, self.y = x, y  # update self coordinates
        self.simulate_history.append([self.x, self.y])  # store to list

    # move simulation
    def move(self) -> None:
        while not self.game_over():
            self.move_step()

    # async pad control by agent
    async def control_pad(self, pad: Pad, interval: int = 0.05, steps: int = 10) -> None:
        distance_per_step = (self.y - pad.y) / steps
        for i in range(steps):
            pad.move(distance_per_step)
            await asyncio.sleep(interval)

    # release a video of tracked frame
    def make_video(self) -> None:
        size = (int(self.bbox[2]-self.bbox[0]), int(self.bbox[3]-self.bbox[1]))  # we need to specify the size
        out = cv.VideoWriter('logs/cv_record.avi', cv.VideoWriter_fourcc(*'DIVX'), 30, size)  # 30 fps, may be more

        for i in range(len(self.frame_sequence)):
            out.write(self.frame_sequence[i])
        out.release()

    # save action logs
    def save_history(self) -> None:
        with open('logs/circles.pkl', 'wb') as f1:
            pickle.dump(self.circle_sequence, f1)
        with open('logs/simulate_history.pkl', 'wb') as f2:
            pickle.dump(self.simulate_history, f2)
