import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "libary"))
import glm

from graphics import Window, Bar, Label, UI_Label, Point


window = Window()

bar = Bar()
bar.mesh.updateColors([[1, 0, 0, 1] for _ in range(4)])
window.enableMovement(bar)

table = Label("wood.jpg")
# build matrix and get positions:
matrix = glm.mat4()
scale = 4
matrix = glm.scale(matrix, glm.vec3(scale, scale, scale))
matrix = glm.rotate(matrix, glm.radians(-90.0), glm.vec3(1, 0, 0))
glm_positions = Point.Utils.to_glm_vec4_list(table.mesh.positions)

# apply transformation:
new_glm_positions = []
for glm_position in glm_positions:
    new_glm_positions.append(matrix * glm_position)
new_positions = Point.Utils.to_points_list(new_glm_positions)
table.mesh.updatePositions(new_positions)

logo = UI_Label("somap.png")
logo.move(0.75, 0.75)
# set the function which should be executed on click:
logo.onClick(lambda: print("Somap stands for soft matter physics!"))
window.enableClickDetection(logo)

#######################################
# TODO: switching between mouse visibility on/off will fuck up camera view, fix that!

while True:
    window.clearBufferBits()

    bar.render(window)
    table.render(window)
    logo.render(window)

    window.handleEvents(["PC", "PT"])
    window.swapBuffers()
