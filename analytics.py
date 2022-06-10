import matplotlib.pyplot as plt
import pickle
import numpy as np
import sys

with open('logs/move_history', 'rb') as f1:
    move_history = pickle.load(f1)
    sys.stdout.write(f'{move_history[0]}\n')

with open('logs/circles', 'rb') as f2:
    circles = pickle.load(f2)
    sys.stdout.write(f'{circles[0]}\n\n')

with open('logs/simulate_history', 'rb') as f3:
    simulate_history = pickle.load(f3)


move_history = np.array(move_history)
simulate_history = np.array(simulate_history)
circles = np.array(circles, dtype='float')

plt.plot(move_history[:, 0], move_history[:, 1])
plt.plot(circles[:, 0], circles[:, 1], 'r.')
plt.plot(simulate_history[:, 0] + 334, simulate_history[:, 1], 'g')
plt.show()
