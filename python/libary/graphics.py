import pygame
from pygame.locals import *

import sys
import glm
import time
import math
import numpy as np

from OpenGL.GL import *

"""-----------Custom imports------------"""
from mesh import Mesh
from shader import Shader
from camera import Camera
from utils import fullpath


class Renderer(object):
    """
    Contain shaders to render different Mesh "types":
    shaderPC - Mesh with position and color attributes
    shaderPT - Mesh with position and texture
    shaderPCT - Mesh with position, color and texture
    GUIshader - Mesh with position and (optional)texture, but without matrices!

    The GUIshader doesn't use model, view or projection matrix, so positions
    should be in range [-1, 1] for x and y, e.g. upper right corner of the
    screen is at (1.0 | 1.0)!

    OpenGL's coordinate system:
                  ^ y = 1.0
                  |
    x = - 1.0 <---|---> x = 1.0
                  |
                  v y = -1.0
    """
    def __init__(self, width, height):
        """---------Create Camera--------"""
        camera = Camera()
        self.camera = camera

        """-------Create Matricies-------"""
        model = glm.mat4()
        view = camera.getViewMatrix()
        projection = glm.perspective(glm.radians(45.0), width/height, 0.1, 100.0)

        """--------------Compile Shaders--------------"""
        shader = Shader(fullpath("shaderPC.vs"), fullpath("shaderPC.fs"))
        shader.use()
        shader.setMatrix("view", view)
        shader.setMatrix("projection", projection)
        shader.setMatrix("model", model)
        # for drawing position and color - data
        self.shaderPC = shader

        shader = Shader(fullpath("shaderPT.vs"), fullpath("shaderPT.fs"))
        shader.use()
        shader.setMatrix("view", view)
        shader.setMatrix("projection", projection)
        shader.setMatrix("model", model)
        # for drawing position and texture - data
        self.shaderPT = shader

        shader = Shader(fullpath("shaderPCT.vs"), fullpath("shaderPCT.fs"))
        shader.use()
        shader.setMatrix("view", view)
        shader.setMatrix("projection", projection)
        shader.setMatrix("model", model)
        # for drawing position, color and texture - data
        self.shaderPCT = shader

        shader = Shader(fullpath("GUIshader.vs"), fullpath("GUIshader.fs"))
        # for drawing GUI elements
        self.GUIshader = shader

    def selectShader(self, type):
        if type == "PC":
            return self.shaderPC
        elif type == "PT":
            return self.shaderPT
        elif type == "PCT":
            return self.shaderPCT
        elif type == "GUI":
            return self.GUIshader

    def render(self, obj, type):
        shader = self.selectShader(type)
        shader.use()
        obj.draw()

    def updateModelMatrix(self, model, type):
        shader = self.selectShader(type)
        shader.use()
        shader.setMatrix("model", model)

    def updateViewMatrix(self, view, type):
        shader = self.selectShader(type)
        shader.use()
        shader.setMatrix("view", view)

    def updateProjectionMatrix(self, projection, type):
        shader = self.selectShader(type)
        shader.use()
        shader.setMatrix("projection", projection)


class Window(object):
    def __init__(self, width=0, height=0):
        pygame.init()
        if width !=0 and height != 0:
            pygame.display.set_mode((width, height), flags=DOUBLEBUF|OPENGL)
        else:
            pygame.display.set_mode((0, 0), flags=DOUBLEBUF|OPENGL|FULLSCREEN)
            width = pygame.display.Info().current_w
            height = pygame.display.Info().current_h

        pygame.mouse.set_pos([width/2, height/2])
        pygame.mouse.set_visible(False)
        self.mouse_is_visible = False
        self.mouse_was_visible = False
        pygame.event.set_grab(True)

        glViewport(0, 0, width, height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(4)
        glPointSize(8)

        self.last_frame_time = time.time()
        # control camera with w, a, s, d keys:
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False
        # control movement with up, left, down, right arrow keys:
        self.up_pressed = False
        self.left_pressed = False
        self.down_pressed = False
        self.right_pressed = False

        self.renderer = Renderer(width, height)

        # if we want to move a graphics object using arrow keys:
        self.moveableObj = None

        # if we want to detect clicks on GUI elements:
        self.clickableObjs = []

        self.width = width
        self.height = height

    def getRenderer(self):
        return self.renderer

    def clearBufferBits(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    def swapBuffers(self):
        pygame.display.flip()

    def enableMovement(self, obj):
        """
        In the handleEvents method arrow keys are used to move the object
        """
        self.moveableObj = obj

    def enableClickDetection(self, obj):
        self.clickableObjs.append(obj)

    def disableClickDetection(self, obj):
        self.clickableObjs.remove(obj)

    def handleEvents(self, types=None):
        """
        Takes a list of shader types as input, e.g: ["PC", "PT", "PTC"]
        or None, the corresponding shaders getting their view matrix update
        according to the mouse and keyboard input!
        """
        current_frame_time = time.time()
        deltaTime = current_frame_time - self.last_frame_time
        self.last_frame_time = current_frame_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_LCTRL:
                    if self.mouse_is_visible:
                        pygame.mouse.set_visible(False)
                        self.mouse_is_visible = False
                        pygame.event.set_allowed(MOUSEMOTION)
                    else:
                        pygame.event.set_blocked(MOUSEMOTION)
                        pygame.mouse.set_visible(True)
                        self.mouse_is_visible = True
                        self.mouse_was_visible = True
                if event.key == K_w:
                    self.w_pressed = True
                if event.key == K_a:
                    self.a_pressed = True
                if event.key == K_s:
                    self.s_pressed = True
                if event.key == K_d:
                    self.d_pressed = True
                if event.key == K_UP:
                    self.up_pressed = True
                if event.key == K_LEFT:
                    self.left_pressed = True
                if event.key == K_DOWN:
                    self.down_pressed = True
                if event.key == K_RIGHT:
                    self.right_pressed = True
            elif event.type == KEYUP:
                if event.key == K_w:
                    self.w_pressed = False
                if event.key == K_a:
                    self.a_pressed = False
                if event.key == K_s:
                    self.s_pressed = False
                if event.key == K_d:
                    self.d_pressed = False
                if event.key == K_UP:
                    self.up_pressed = False
                if event.key == K_LEFT:
                    self.left_pressed = False
                if event.key == K_DOWN:
                    self.down_pressed = False
                if event.key == K_RIGHT:
                    self.right_pressed = False
            elif event.type == MOUSEMOTION:
                x, y = pygame.mouse.get_rel()
                if self.mouse_was_visible:
                    self.mouse_was_visible = False
                else:
                    self.renderer.camera.processMouseMovement(x, -y)
            elif event.type == MOUSEBUTTONUP and len(self.clickableObjs) > 0:
                x, y = pygame.mouse.get_pos()
                """
                Due to the different coordinate systems of OpenGL and pygame we
                have to convert the x, y values we get to OpenGl's
                """
                x = x - self.width/2
                y = -y + self.height/2
                x = x / (self.width/2)
                y = y / (self.height/2)
                for obj in self.clickableObjs:
                    if obj.gotClicked(x, y):
                        obj.execute()


        if self.w_pressed:
            self.renderer.camera.processKeyboard("forward", deltaTime)
        if self.a_pressed:
            self.renderer.camera.processKeyboard("left", deltaTime)
        if self.s_pressed:
            self.renderer.camera.processKeyboard("backward", deltaTime)
        if self.d_pressed:
            self.renderer.camera.processKeyboard("right", deltaTime)

        # if an object is enabled for movement:
        if self.moveableObj:
            if self.up_pressed:
                self.moveableObj.mesh.move(0, 0.1, 0)
            if self.left_pressed:
                self.moveableObj.mesh.move(-0.1, 0, 0)
            if self.down_pressed:
                self.moveableObj.mesh.move(0, -0.1, 0)
            if self.right_pressed:
                self.moveableObj.mesh.move(0.1, 0, 0)

        # apply camera movement to selected shader "types":
        # (if mouse is visible we don't want to change camera view)
        if types and not self.mouse_is_visible:
            view = self.renderer.camera.getViewMatrix()
            for type in types:
                self.renderer.updateViewMatrix(view, type)


class Point(list):
    """
    Point/Vector class
    """
    def __init__(self, x, y, z, r=0.5, g=0.5, b=0.5):
        list.__init__(self, [x, y, z])
        positions = [[x, y, z]]
        colors = [[r, g, b, 1.0]]
        indices = [0]
        # positions, indices and colors - lists can be accessed over the mesh
        #self.mesh = Mesh(positions, indices, colors=colors)
        self.x = x

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, new_x):
        self[0] = new_x

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, new_y):
        self[1] = new_y

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, new_z):
        self[2] = new_z

    def __sub__(self, other):
        return Point(self.x - other.x,
                     self.y - other.y,
                     self.z - other.z)

    def __add__(self, other):
        return Point(self.x + other.x,
                     self.y + other.y,
                     self.z + other.z)

    def __truediv__(self, other):
        return Point(self.x / other,
                     self.y / other,
                     self.z / other)

    def __mul__(self, other):
        return Point(self.x * other,
                     self.y * other,
                     self.z * other)

    @property
    def abs(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def toGlmVec3(self):
        return glm.vec3(self.x, self.y, self.z)

    def toGlmVec4(self):
        return glm.vec4(self.x, self.y, self.z, 1)

    def fromGlmVec4(glm_vec4):
        """
        Class Function to create a Point Instance from glm vec3
        """
        return Point(glm_vec4.x, glm_vec4.y, glm_vec4.z)

    def __repr__(self):
        return f"({self.x}|{self.y}|{self.z})"

    def draw(self):
        self.mesh.draw(GL_POINTS, 1, 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PC")

    class Utils(object):
        def to_glm_vec4_list(points_list):
            glm_vec4_list = []
            for a_point in points_list:
                glm_vec4_list.append(a_point.toGlmVec4())
            return glm_vec4_list

        def to_points_list(glm_vec4_list):
            points_list = []
            for glm_vec4 in glm_vec4_list:
                points_list.append(Point.fromGlmVec4(glm_vec4))
            return points_list


class Label(object):
    def __init__(self, imgName, width, height):
        positions = [Point(-width/2, -height/2, 0),
                     Point(width/2, -height/2, 0),
                     Point(-width/2, height/2, 0),
                     Point(width/2, height/2, 0)]
        textures = [[0, 0],
                    [1, 0],
                    [0, 1],
                    [1, 1]]
        indices = [0, 1, 2,
                   3, 2, 1]
        # positions, indices and textures - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, textures=textures, imgName=imgName)

    def draw(self):
        self.mesh.draw(GL_TRIANGLES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PT")

class UI_Element(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.screen_posX = 0
        self.screen_posY = 0
        self.function = None

    def move(self, x, y):
        self.mesh.move(x, y, 0)
        self.screen_posX = x
        self.screen_posY = y

    def gotClicked(self, x, y):
        """
        Return True if the mouse click is detected inside the
        UI_Element or False otherwise!
        """
        if self.screen_posX - self.width/2 <= x and x <= self.screen_posX + self.width/2:
            if self.screen_posY - self.height/2 <= y and y <= self.screen_posY + self.height/2:
                return True
        return False

    def onClick(self, function):
        """
        Set the function which should be executed if clicked!
        """
        self.function = function

    def execute(self):
        self.function()


class UI_Label(Label, UI_Element):
    def __init__(self, imgName, width, height):
        Label.__init__(self, imgName, width, height)
        UI_Element.__init__(self, width, height)

    def render(self, window):
        renderer = window.getRenderer()
        shader = renderer.selectShader("GUI")
        shader.use()
        shader.setInt("hasTexture", 1)
        renderer.render(self, "GUI")


class UI_Bar(UI_Element):
    def __init__(self, width, height, origin=Point(0, 0, 0)):
        UI_Element.__init__(self, width, height)
        positions = [origin + Point(-width/2, 0, 0),
                     origin + Point(width/2, 0, 0),
                     origin + Point(-width/2, height, 0),
                     origin + Point(width/2, height, 0)]
        indices = [0, 1, 2,
                   3, 2, 1]
        self.mesh = Mesh(positions, indices)
        self.origin = origin

    def draw(self):
        self.mesh.draw(GL_TRIANGLES, len(self.mesh.indices), 0)

    @property
    def barHeight(self):
        return (self.mesh.positions[2].y - self.origin.y)

    @barHeight.setter
    def barHeight(self, new_height):
        positions = [self.origin + Point(-self.width/2, 0, 0),
                     self.origin + Point(self.width/2, 0, 0),
                     self.origin + Point(-self.width/2, new_height, 0),
                     self.origin + Point(self.width/2, new_height, 0)]
        self.mesh.updatePositions(positions)

    def render(self, window):
        renderer = window.getRenderer()
        shader = renderer.selectShader("GUI")
        shader.use()
        shader.setInt("hasTexture", 0)
        renderer.render(self, "GUI")


class UI_Axis(UI_Element):
    def __init__(self, start_point, end_point, ticks):
        UI_Element.__init__(self, None, None) # no need for onClick detection!

        positions = [start_point, end_point]
        self.ticks = ticks
        length = (end_point - start_point).abs
        tick_space = length / ticks
        unit_vec = (end_point - start_point) / length
        self.length = length
        self.tick_origins = []
        p = start_point
        for _ in range(ticks):
            p = p + unit_vec * tick_space
            self.tick_origins.append(p)

        indices = [0, 1]
        self.mesh = Mesh(positions, indices)

    def draw(self):
        self.mesh.draw(GL_LINES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        shader = renderer.selectShader("GUI")
        shader.use()
        shader.setInt("hasTexture", 0)
        renderer.render(self, "GUI")


class UI_Tick(UI_Element):
    def __init__(self, length=0.05, oriantation="vertical", origin=Point(0, 0, 0)):
        UI_Element.__init__(self, None, None) # no need for onClick detection!

        self.length = length
        self.oriantation = oriantation
        if oriantation == "vertical":
            positions = [origin + Point(0, length/2, 0) , origin + Point(0, -length/2, 0)]
        elif oriantation == "horizontal":
            positions = [origin + Point(length/2, 0, 0) , origin + Point(-length/2, 0, 0)]
        else:
            raise NameError("Tick.oriantation must be either vertical or horizontal!")

        indices = [0, 1]
        self.mesh = Mesh(positions, indices)

    def draw(self):
        self.mesh.draw(GL_LINES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        shader = renderer.selectShader("GUI")
        shader.use()
        shader.setInt("hasTexture", 0)
        renderer.render(self, "GUI")


class BarPlot(UI_Element):
    def __init__(self, origin, xLength, yLength, nbars, maxValue):
        UI_Element.__init__(self, None, None) # no need for onClick detection!

        self.objs = []
        xEndPoint = Point(origin.x + xLength, origin.y, origin.z)
        yEndPoint = Point(origin.x, origin.y + yLength, origin.z)
        xAxis = UI_Axis(origin, xEndPoint, nbars)
        self.objs.append(xAxis)
        yAxis = UI_Axis(origin, yEndPoint, 5)
        self.objs.append(yAxis)

        for origin in xAxis.tick_origins:
            self.objs.append(UI_Tick(origin=origin))

        for origin in yAxis.tick_origins:
            self.objs.append(UI_Tick(origin=origin, oriantation="horizontal"))

        self.bars = [UI_Bar(0.05, yLength, origin=origin) for origin in xAxis.tick_origins]
        self.bars[0].mesh.positions[0]
        self.objs.extend(self.bars)

        self.nbars = nbars
        self.yLength = yLength
        self.maxValue = maxValue

    def updateBarHeights(self, new_barHeights):
        for new_barHeight, bar in zip(new_barHeights, self.bars):
            scaled_barHeight = self.yLength * (new_barHeight / self.maxValue)
            bar.barHeight = scaled_barHeight

    def normalizeValues(self, values):
        return [value / self.maxValue for value in values]

    def render(self, window):
        for obj in self.objs:
            obj.render(window)


class Backbone(object):
    """
    The backbones are the core of the bending animation of the SoftRobot class
    """
    def __init__(self, positions, n):
        indices = [i for i in range(n)] # for GL_LINE_STRIP
        colors = [[0.0, 0.0, 0.0, 1.0] for _ in range(n)]
        # positions, indices and colors - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, colors=colors)

    def draw(self):
        self.mesh.draw(GL_LINE_STRIP, len(self.mesh.indices), 0)
        self.mesh.draw(GL_POINTS, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PC")

    def update(self, positions):
        self.mesh.updatePositions(positions)

    def interpolate(p, backbone_start_positions, backbone_end_positions):
        """
        Class Method!
        Interpolate between the backbone start and end positions, e.g. to get
        the backbone positions for 50% of the bending process p must be 0.5
        """
        if p > 1.0:
            p = 1.0
        elif p < 0.0:
            p = 0.0
        backbone_interpolate_positions = []
        t_s = math.pi/2
        is_first = True
        for pos_s, pos_e in zip(backbone_start_positions, backbone_end_positions):
            if is_first:
                is_first = False
                backbone_interpolate_positions.append([0.0, 0.0, 0.0])
                continue
            y_s = pos_s[1]
            x_e = pos_e[0]
            y_e = pos_e[1]
            a = x_e / math.sqrt(y_s**2 - y_e**2)
            t_e = math.asin(y_e / y_s)
            t = t_s + p * (t_e - t_s)
            x_new = a * y_s * math.cos(t)
            y_new = y_s * math.sin(t)
            backbone_interpolate_positions.append([x_new, y_new, 0.0])
        return backbone_interpolate_positions


class SoftRobot(object):
    def __init__(self, n, bending_radius, cylinder_radius, color=[0.5, 0.5, 0.5, 1.0], m=32):
        """
        Create a cylinder shaped soft robot model to visualize sensor data.

        parameter n: number of circles to build the robot skin
        parameter bending_radius: radius of robot backbone fully bent
        parameter cylinder_radius: radius of cylindric robot skin
        parameter color: start color for the whole robot skin
        """
        self.n = n
        self.m = m # blender default value for number of vertices of a circle
        self.default_color = color

        b = bending_radius * 2*math.pi/4
        self.backbone_start_positions = []
        for i in range(n): # 0 to (n-1)
            y = i * b/(n-1)
            self.backbone_start_positions.append([0.0, y, 0.0])

        self.backbone = Backbone(self.backbone_start_positions, self.n)

        self.backbone_end_positions = []
        t0, t1 = 3*math.pi/2, 2*math.pi
        for i in range(n): # 0 to (n-1)
            t = t0 + i * (t1-t0)/(n-1)
            x = bending_radius * math.sin(t) + bending_radius
            y = bending_radius * math.cos(t)
            self.backbone_end_positions.append([x, y, 0.0])

        # by now we have the bones, time for the skin:
        positions, colors, indices = self.createSkinVertices(self.backbone_start_positions, cylinder_radius)

        """
        We use the SoftRobot.base_circle to draw the whole skin from if we
        want the SoftRobot to bend according to the interpolated backbone in
        the SoftRobot.transformSkinVertices method!
        """
        self.base_circle = positions[:self.m + 1]

        self.mantle_indices_offset = len(indices)

        # circle indices are structured like: p_0, p_1, ..., p_m, p_1
        # so from one circle to another we have m + 2 vertices
        self.cirlce_indices_offsets = [i * (self.m + 2) for i in range(self.n)]
        self.circle_indices_size =  self.n * (self.m + 2)

        # indices for the cylinder mantles:
        mantle_indices = []

        for i in range(1, 1 + m):
            mantle_indices.extend([i + m + 1, i]) # order matters (face culling)
        mantle_indices.extend([m + 2, 1]) # to get a closed mantle

        # extend the indices to include the mantle indices:
        indices.extend(mantle_indices)
        for j in range(1, n):
            indices.extend([i + j * (m + 1) for i in mantle_indices])

        self.mantle_indices_size = (n - 1) * len(mantle_indices)

        # positions, indices and colors - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, colors=colors)

    def updateSkinVertices(self, p):
        positions = Backbone.interpolate(p,
                                         self.backbone_start_positions,
                                         self.backbone_end_positions)
        self.backbone.update(positions)

        rms, tms = [], [] # rotation and translation matrices
        v_n0 = glm.vec3(0.0, 1.0, 0.0) # normal vector of first circle area!
        for i in range(self.n): # 0,... (n - 1)
            p_i = positions[i] # position p_i of the backbone
            rm, tm = glm.mat4(), glm.mat4() # initialize unit matrices
            tm = glm.translate(tm, glm.vec3(p_i[0], p_i[1], p_i[2]))

            tms.append(tm)

            # if first backbone position:
            if i == 0:
                rms.append(rm) # append a unit matrix = no rotation
                continue

            # if last backbone position:
            if i == (self.n - 1):
                # position vector p_(i-1):
                p_i_prev = glm.vec3(positions[i-1][0],
                                    positions[i-1][1],
                                    positions[i-1][2])
                # normalized gradient vector at p_i:
                v_ni = glm.normalize(p_i - p_i_prev)

                if v_ni == v_n0:
                    rms.append(rm) # append a unit matrix = no rotation
                    continue

                angle = glm.acos(glm.length(v_n0 * v_ni)) # get the rotation angle
                rot_axis = glm.cross(v_n0, v_ni) # get the rotation axis
                rm = glm.rotate(rm, angle, rot_axis)
                rms.append(rm) # append the rotation matrix
                continue

            # position vector p_(i+1):
            p_i_next = glm.vec3(positions[i+1][0],
                                positions[i+1][1],
                                positions[i+1][2])
            # position vector p_(i-1):
            p_i_prev = glm.vec3(positions[i-1][0],
                                positions[i-1][1],
                                positions[i-1][2])
            # normalized gradient vector at p_i:
            v_ni = glm.normalize(p_i_next - p_i_prev)

            if v_ni == v_n0:
                rms.append(rm) # append a unit matrix = no rotation
                continue

            angle = glm.acos(glm.length(v_n0 * v_ni)) # get the rotation angle
            rot_axis = glm.cross(v_n0, v_ni) # get the rotation axis
            rm = glm.rotate(rm, angle, rot_axis)
            rms.append(rm) # append the rotation matrix

        # use transformation matrices for skin vertices
        new_positions = []
        for tm, rm in zip(tms, rms):
            for position in self.base_circle:
                # we need a glm.vec4 to apply matrix transformations
                vec4_pos = glm.vec4(position[0],
                                    position[1],
                                    position[2],
                                    1.0)
                vec4_pos = tm * rm * vec4_pos # apply translation
                new_positions.append([vec4_pos.x, vec4_pos.y, vec4_pos.z])

        self.mesh.updatePositions(new_positions)

    def updateColors(self, sensor_values, min_color=[0, 1, 0, 1], max_color=[1, 0, 0, 1]):
        """
        parameter sensor_values: normalized sensor values in range [0, 1] where
                                 a 0 is the minimum and 1 the maximum
        parameter min_color: the color for the minimum sensor value
        parameter max_color: the color for the maximum sensor value
        """
        new_colors = self.mesh.colors
        for i, sensor_value in zip(range(1, self.n), sensor_values):
            # calculate color of intersection point based on sensor input:
            intersection_color = [min_color[0] * (1 - sensor_value) + max_color[0] * sensor_value,
                                  min_color[1] * (1 - sensor_value) + max_color[1] * sensor_value,
                                  min_color[2] * (1 - sensor_value) + max_color[2] * sensor_value,
                                  1]
            for j in range(1, (self.m + 1)):
                new_colors[i * (self.m + 1) + j] = intersection_color

        self.mesh.updateColors(new_colors)


    def draw(self):
        # draw the backbone:
        self.backbone.draw()

        # filled circle for bottom:
        self.mesh.draw(GL_TRIANGLE_FAN, self.m + 2, self.cirlce_indices_offsets[0])
        # filled circle for top:
        self.mesh.draw(GL_TRIANGLE_FAN, self.m + 2, self.cirlce_indices_offsets[-1])

        # draw SoftRobot skin out of cylinder mantles:
        self.mesh.draw(GL_TRIANGLE_STRIP, self.mantle_indices_size, self.mantle_indices_offset)

        # draw black circles around the SoftRobot:
        prev_colors = self.mesh.colors
        self.mesh.updateColors([[0, 0, 0, 1] for _ in prev_colors])
        for circle_offset in self.cirlce_indices_offsets:
            self.mesh.draw(GL_LINE_LOOP, self.m, circle_offset + 1)

        # reset colors:
        self.mesh.updateColors(prev_colors)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PC")

    def createSkinVertices(self, backbone_positions, radius):
        positions = []
        colors = []
        indices = []

        # start index
        index = 0

        for position in backbone_positions: # 0 to (n-1)
            y = position[1] # each position has [x, y, z] format
            # for the circle center and GL_TRIANGLE_FAN
            positions.append([0.0, y, 0.0])
            colors.append(self.default_color)
            indices.append(index)
            start_index = index

            # for outer circle vertices
            index += 1
            phi = 0.0
            deltaPhi = 360/self.m
            while phi < 360:
                x = radius * math.cos(math.radians(phi))
                z = radius * math.sin(math.radians(phi))
                positions.append([x, y, z])
                colors.append(self.default_color)
                # indices for GL_TRIANGLE_STRIP or GL_LINE_LOOP:
                indices.append(index)
                phi += deltaPhi
                index += 1

            # for GL_TRIANGLE_FAN to get a fully filled circle
            indices.append(start_index + 1)

        return positions, colors, indices
