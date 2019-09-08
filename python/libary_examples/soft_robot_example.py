import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "libary"))
import glm
import time
import threading
from threading import Thread

from graphics import Window, BarPlot, SoftRobot, Label, UI_Label, Point
from utils import Port


class Fifo:
    """FIFO ... First In First Out buffer
    in such a buffer the threads will temporaly store the data
    the access is synchronized wich is needed when multiple threads accessing it
    with Lock.acquire() and Lock.release() used internally we ensure that only
    one thread at a time can access the fifo buffer -> no data corruption possible
    """
    def __init__(self):
        self.data = []
        self.lock = threading.Lock()

    def has_item(self) -> bool:
        return len(self.data) > 0

    # a higher order function that executes an access function synchronized:
    def synchronized_access(self, access_function, *args):
        obj = None
        try:
            self.lock.acquire()
            # here an error could be raised!
            obj = access_function(*args)
        except Exception as e:
            print(e)
        finally:
            # make sure to release the lock even in error case or it will block forever!
            self.lock.release()
        return obj

    def _clear_data(self):
        self.data.clear()

    def clear_data(self):
        self.synchronized_access(self._clear_data)

    def _push(self, data):
        self.data.append(data)

    def push(self, data):
        self.synchronized_access(self._push, data)

    def _pop(self):
        return self.data.pop(0)

    def pop(self) -> object:
        return self.synchronized_access(self._pop)


class ArduinoThread(Thread):
    def __init__(self, buffer, port="COM3", baudrate=19200, nbars=8):
        Thread.__init__ (self)
        self.port = Port(port, baudrate=baudrate)
        self.running = True
        self.buffer = buffer
        self.nbars = nbars
        self.temp = [0 for _ in range(nbars)]

    def run(self):
        last_update_time = time.time()
        # every 160ms the arduino sends 8 sensor values
        arduino_update_time = 0.16

        while self.running:
            start = time.time()
            self.port.read_csv_for_bar(self.temp, self.nbars)
            self.buffer.push(self.temp[:])
            print("Aquisition time:", time.time() - start)
            if (time.time() - last_update_time) > arduino_update_time:
                continue
            else:
                time.sleep(arduino_update_time - (time.time() - last_update_time))

    def stop(self):
        self.running = False


window = Window()


#-------------create the barplot and label it----------------
barplot = BarPlot(Point(-0.9, 0.4, 0), 0.5, 0.5, 8, 1023)

x_labels = []
x_labels.append(UI_Label("sensor.png", 0.1, 0.1))
x_labels[0].move(-0.95, 0.3)
for i in range(8):
    x_labels.append(UI_Label(f"{i}.png", 0.08, 0.08))
    if i == 0:
        x_labels[-1].move(-0.9 + 0.06, 0.3)
    elif i >= 4:
        x_labels[-1].move(-0.9 + 0.06 * (i + 1) + 0.01 * (i - 3), 0.3)
    else:
        x_labels[-1].move(-0.9 + 0.06 * (i + 1), 0.3)

y_labels = [UI_Label("200.png", 0.06, 0.06),
            UI_Label("400.png", 0.06, 0.06),
            UI_Label("600.png", 0.06, 0.06),
            UI_Label("800.png", 0.06, 0.06),
            UI_Label("1000.png", 0.06, 0.06)]

y_labels[0].move(-0.96, 0.3 + 0.20)
for i in range(1, 5):
    y_labels[i].move(-0.96, 0.3 + 0.10 * (i + 2))
#------------------------------------------------------------

softrobot = SoftRobot(10, 1.5, 0.3)

table = Label("wood.jpg", 2, 2)
# build matrix and get positions:
matrix = glm.mat4()
matrix = glm.rotate(matrix, glm.radians(-90.0), glm.vec3(1, 0, 0))
# get rid of depth fighting of the table with the SoftRobot's bottom,
# not visible for the but for the depth testing:
matrix = glm.translate(matrix, glm.vec3(0, 0, -0.001))
glm_positions = Point.Utils.to_glm_vec4_list(table.mesh.positions)

# apply transformation:
new_glm_positions = []
for glm_position in glm_positions:
    new_glm_positions.append(matrix * glm_position)
new_positions = Point.Utils.to_points_list(new_glm_positions)
table.mesh.updatePositions(new_positions)

logo = UI_Label("somap.png", 0.2, 0.2)
logo.move(0.9, 0.9)
# set the function which should be executed on click:
logo.onClick(lambda: print("Somap stands for soft matter physics!"))
window.enableClickDetection(logo)

p = 0
step = 0.01
flag = True

buffer = Fifo()
arduinoThread = ArduinoThread(buffer)

start = UI_Label("start.png", 0.2, 0.2)
start.move(-0.9, -0.9)
start.onClick(arduinoThread.start)
window.enableClickDetection(start)

stop = UI_Label("stop.png", 0.2, 0.2)
stop.move(-0.7, -0.9)
stop.onClick(arduinoThread.stop)
window.enableClickDetection(stop)

hide = UI_Label("hide.png", 0.2, 0.2)
class myFlag(object):
    def __init__(self, state):
        self.state = state

    def flip(self):
        self.state = not self.state

draw_flag = myFlag(True)

hide.move(-0.5, -0.9)
hide.onClick(draw_flag.flip)
window.enableClickDetection(hide)

sensor_values = [0 for _ in range(barplot.nbars)]
old_sensor_values = sensor_values
values_have_changed = False

while True:
    window.clearBufferBits()

    try:
        sensor_values = buffer.pop()
        for sensor_value, old_sensor_value in zip(sensor_values, old_sensor_values):
            if sensor_value != old_sensor_value:
                values_have_changed = True
                break
    except Exception as e:
        pass

    if values_have_changed:
        print(sensor_values)
        barplot.updateBarHeights(sensor_values)
        softrobot.updateColors(barplot.normalizeValues(sensor_values))
        old_sensor_values = sensor_values
        values_have_changed = False

    if draw_flag.state:
        barplot.render(window)

        for label in x_labels:
            label.render(window)
        for label in y_labels:
            label.render(window)

    softrobot.updateSkinVertices(p)
    softrobot.render(window)

    if p <= 0:
        flag = True
        p += step
    elif p >= 1:
        flag = False
        p -= step
    else:
        if flag:
            p += step
        else:
            p -= step

    table.render(window)
    logo.render(window)
    start.render(window)
    stop.render(window)
    hide.render(window)

    window.handleEvents(["PC", "PT"])
    window.swapBuffers()
