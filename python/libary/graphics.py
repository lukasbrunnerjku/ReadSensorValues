import pygame
from pygame.locals import *

import sys, os
import glm
import time
import math
import numpy as np

from OpenGL.GL import *

"""-----------Custom imports------------"""
from mesh import Mesh
from shader import Shader
from camera import Camera


class Renderer(object):
    def __init__(self, width, height):
        """---------Create Camera--------"""
        camera = Camera()
        self.camera = camera

        """-------Create Matricies-------"""
        model = glm.mat4()
        view = camera.getViewMatrix()
        projection = glm.perspective(glm.radians(45.0), width/height, 0.1, 100.0)

        """--------------Compile Shaders--------------"""
        def fullpath(filename):
            return os.path.join(os.path.dirname(sys.path[0]), "libary", filename)

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

    def selectShader(self, type):
        if type == "PC":
            return self.shaderPC
        elif type == "PT":
            return self.shaderPT
        elif type == "PCT":
            return self.shaderPCT

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
    def __init__(self, width, height):
        pygame.init()
        pygame.display.set_mode((width, height), flags=DOUBLEBUF|OPENGL)

        glViewport(0, 0, width, height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(4)
        glPointSize(8)

        self.last_frame_time = time.time()
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False

        self.renderer = Renderer(width, height)

    def getRenderer(self):
        return self.renderer

    def clearBufferBits(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    def swapBuffers(self):
        pygame.display.flip()

    def handleEvents(self):
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
                if event.key == K_w:
                    self.w_pressed = True
                if event.key == K_a:
                    self.a_pressed = True
                if event.key == K_s:
                    self.s_pressed = True
                if event.key == K_d:
                    self.d_pressed = True
            elif event.type == KEYUP:
                if event.key == K_w:
                    self.w_pressed = False
                if event.key == K_a:
                    self.a_pressed = False
                if event.key == K_s:
                    self.s_pressed = False
                if event.key == K_d:
                    self.d_pressed = False
            elif event.type == MOUSEMOTION:
                # virtual input mode (see pygame):
                x, y = pygame.mouse.get_rel()
                self.renderer.camera.processMouseMovement(x, -y)

        if self.w_pressed:
            self.renderer.camera.processKeyboard("forward", deltaTime)
        if self.a_pressed:
            self.renderer.camera.processKeyboard("left", deltaTime)
        if self.s_pressed:
            self.renderer.camera.processKeyboard("backward", deltaTime)
        if self.d_pressed:
            self.renderer.camera.processKeyboard("right", deltaTime)

        view = self.renderer.camera.getViewMatrix()
        self.renderer.updateViewMatrix(view, "PC")


class Point(list):
    def __init__(self, x, y, z):
        list.__init__(self, [x, y, z])

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

    def __repr__(self):
        return f"({self.x}|{self.y}|{self.z})"


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
    def __init__(self, width=0.5, height=0.5):
        self.width = width
        self.height = height
        positions = [Point(-width/2, 0, 0),
                     Point(width/2, 0, 0),
                     Point(-width/2, height, 0),
                     Point(width/2, height, 0)]
        textures = [[0, 0],
                    [1, 0],
                    [0, 1],
                    [1, 1]]
        indices = [0, 1, 2,
                   3, 2, 1]
        # positions, indices and textures - lists can be accessed over the mesh
        self.mesh = Mesh(positions, indices, textures=textures)

    def draw(self):
        self.mesh.draw(GL_TRIANGLES, len(self.mesh.indices), 0)

    def render(self, window):
        renderer = window.getRenderer()
        renderer.render(self, "PT")


class BarPlot(object):
    def __init__(self, originPoint, xEndPoint, yEndPoint, nbars, maxHeight):
        self.xTick = Tick()
        self.yTick = Tick(oriantation="horizontal")

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
