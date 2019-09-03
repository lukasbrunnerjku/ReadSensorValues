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
    Contains 3 shaders to render 3 different Mesh "types":
    shaderPC - Mesh with position and color attributes
    shaderPT - Mesh with position and texture
    shaderPCT - Mesh with position, color and texture
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

        self.oldX = None
        self.oldY = None

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
                        pygame.mouse.set_pos([self.oldX, self.oldY])
                        x, y = pygame.mouse.get_rel()
                        pygame.event.set_allowed(MOUSEMOTION)
                    else:
                        self.oldX, self.oldY = pygame.mouse.get_pos()
                        pygame.event.set_blocked(MOUSEMOTION)
                        pygame.mouse.set_visible(True)
                        self.mouse_is_visible = True
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
        self.mesh = Mesh(positions, indices, colors=colors)
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


class Axis(object):
    def __init__(self, start_point, end_point, ticks=5):
        positions = [start_point, end_point]
        self.ticks = ticks
        length = (end_point - start_point).abs
        tick_space = length / ticks
        unit_vec = (end_point - start_point) / length
        self.length = length
        self.tick_positions = []
        p = start_point
        for _ in range(ticks):
            p = p + unit_vec * tick_space
            self.tick_positions.append(p)

        colors = [[0.0, 0.0, 0.0, 1.0] for _ in positions]
        indices = [0, 1]
        # positions, indices and colors - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, colors=colors)

    def draw(self):
        self.mesh.draw(GL_LINES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PC")


class Tick(object):
    def __init__(self, length=0.2, oriantation="vertical"):
        self.length = length
        self.oriantation = oriantation
        if oriantation == "vertical":
            positions = [Point(0, length/2, 0) , Point(0, -length/2, 0)]
        elif oriantation == "horizontal":
            positions = [Point(length/2, 0, 0) , Point(-length/2, 0, 0)]
        else:
            raise NameError("Tick.oriantation must be either vertical or horizontal!")

        colors = [[0.0, 0.0, 0.0, 1.0] for _ in positions]
        indices = [0, 1]
        # positions, indices and colors - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, colors=colors)

    def draw(self):
        self.mesh.draw(GL_LINES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PC")


class Bar(object):
    def __init__(self, r=0.5, g=0.5, b=0.5, width=0.1, height=1.0):
        self.width = width
        self.height = height
        positions = [Point(-width/2, 0, 0),
                     Point(width/2, 0, 0),
                     Point(-width/2, height, 0),
                     Point(width/2, height, 0)]

        colors = [[r, g, b, 1.0] for _ in positions]
        indices = [0, 1, 2,
                   3, 2, 1]
        # positions, indices and colors - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, colors=colors)

    def draw(self):
        self.mesh.draw(GL_TRIANGLES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PC")


class Label(object):
    def __init__(self, imgName, width=0.5, height=0.5):
        self.width = width
        self.height = height
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


class UI_Label(Label):
    def __init__(self, imgName, width=0.5, height=0.5):
        Label.__init__(self, imgName, width=width, height=height)
        self.screen_posX = 0
        self.screen_posY = 0
        self.function = None

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "GUI")

    def move(self, x, y):
        self.mesh.move(x, y, 0)
        self.screen_posX = x
        self.screen_posY = y

    def gotClicked(self, x, y):
        """
        Return True if the mouse click is detected inside the
        Label or False otherwise!
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



class BarPlot(object):
    def __init__(self, originPoint, xLength, yLength, nbars, maxHeight):
        self.xTick = Tick()
        self.yTick = Tick(oriantation="horizontal")

        xEndPoint = Point(originPoint.x + xLength, originPoint.y, originPoint.z)
        yEndPoint = Point(originPoint.x, originPoint.y + yLength, originPoint.z)
        self.xAxis = Axis(originPoint, xEndPoint, ticks=nbars)
        self.yAxis = Axis(originPoint, yEndPoint)

        self.bar = Bar()

        self.barHeights = [0 for _ in range(nbars)]
        self.nbars = nbars
        self.maxHeight = maxHeight

    def update(self, new_barHeights):
        self.barHeights = new_barHeights

    def render(self, window):
        renderer = window.getRenderer()
        for xtp, bh in zip(self.xAxis.tick_positions, self.barHeights):
            model = glm.mat4()
            model = glm.translate(model, xtp.toGlmVec3())
            renderer.updateModelMatrix(model, "PC")
            renderer.render(self.xTick, "PC")
            bar_height = self.yAxis.length * bh / self.maxHeight
            model = glm.scale(model, glm.vec3(1, bar_height, 1))
            renderer.updateModelMatrix(model, "PC")
            renderer.render(self.bar, "PC")

        model = glm.mat4()
        renderer.updateModelMatrix(model, "PC")
        renderer.render(self.xAxis, "PC")
        renderer.render(self.yAxis, "PC")

        for ytp in self.yAxis.tick_positions:
            model = glm.mat4()
            model = glm.translate(model, ytp.toGlmVec3())
            renderer.updateModelMatrix(model, "PC")
            renderer.render(self.yTick, "PC")
