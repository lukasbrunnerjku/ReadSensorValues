import time
import random

"""-----------Custom imports------------"""
from graphics import Window, BarPlot, Point

window = Window(600, 400)
barplot = BarPlot(Point(0, 0, 0),
                  Point(2, 0, 0),
                  Point(0, 1, 0),
                  8)

last_update_time = time.time()

while True:
    window.clearBufferBits()

    if time.time() - last_update_time  > 0.5:
        last_update_time = time.time()
        barplot.update([random.random() for _ in range(barplot.nbars)])

    barplot.render(window)

    window.handleEvents()
    window.swapBuffers()
