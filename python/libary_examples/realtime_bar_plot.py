import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "libary"))

from graphics import Window, BarPlot, Point
from utils import Port

import time

port = Port("COM5", baudrate=19200)

window = Window()
barplot = BarPlot(Point(-1, -1, 0), 2, 2, 8, 1000)

last_update_time = time.time()

# every 160ms the arduino sends 8 sensor values
arduino_update_time = 0.16

while True:
    window.clearBufferBits()

    if time.time() - last_update_time  > arduino_update_time:
        last_update_time = time.time()
        port.read_csv_for_bar(barplot.barHeights, barplot.nbars)

    barplot.render(window)

    window.handleEvents(["PC"]) # use arg: ["PC"] then keyboard/mouse to look around
    window.swapBuffers()
