import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "libary"))

import time

from graphics import Window, Bar, Label, Point


window = Window()
labels = []
for i in range(10):
    labels.append(Label(f"{i}.png"))


i = 0
last_update_time = time.time()
update_interval = 1

while True:
    window.clearBufferBits()

    if time.time() - last_update_time  > update_interval:
        last_update_time = time.time()
        if i < 9:
            i += 1
        else:
            i = 0

    labels[i].render(window)

    window.handleEvents()
    window.swapBuffers()
