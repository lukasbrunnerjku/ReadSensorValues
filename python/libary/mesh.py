from OpenGL.GL import *
from OpenGL.GLU import *
from ctypes import c_void_p
import numpy as np
from PIL import Image

from utils import fullpath

class Mesh():

    def __init__(self, positions, indices, colors=None, textures=None, imgName=None):
        """
        Create a Mesh which contains vertices, each vertex must have a
        position and indices to draw, optional are color and/or texture attribute
        The color/texture attribute can be set over colors/textures kwargs!
        (For the texture we have to specify an image as well using imgName)

        The position attribute must be in [x, y, z] format!
        The color attribute must be in [r, g, b, a] format!
        The texture attribute must be in [s, t] format!

        All information is stored in lists, e.g: Mesh.positions and so on...
        """
        self.positions = positions
        self.indices = indices
        self.colors = colors
        self.textures = textures

        positions = np.array(positions, dtype=np.float32)
        poffset = 0 # c_void_p will throw errors here!!!
        psize = positions.nbytes

        if self.colors != None and self.textures != None:
            colors = np.array(colors, dtype=np.float32)
            coffset = psize # c_void_p will throw errors here!!!
            csize = colors.nbytes

            textures = np.array(textures, dtype=np.float32)
            toffset = psize + csize # c_void_p will throw errors here!!!
            tsize = textures.nbytes
            data_size = psize + csize + tsize

        elif self.colors != None:
            colors = np.array(colors, dtype=np.float32)
            coffset = psize # c_void_p will throw errors here!!!
            csize = colors.nbytes
            data_size = psize + csize

        elif self.textures != None:
            textures = np.array(textures, dtype=np.float32)
            toffset = psize # c_void_p will throw errors here!!!
            tsize = textures.nbytes
            data_size = psize + tsize

        indices = np.array(indices, dtype=np.uint32)
        self.indices = indices # save indices as numpy array for drawing

        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, data_size, None, GL_STATIC_DRAW)

        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glBufferSubData(GL_ARRAY_BUFFER, poffset, psize, positions)

        # positions:
        offset = c_void_p(0)
        glEnableVertexAttribArray(0) # layout(location = 0)
        stride = 3 * positions.itemsize
        glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, offset)

        if self.colors != None and textures != None:
            glBufferSubData(GL_ARRAY_BUFFER, coffset, csize, colors)
            glBufferSubData(GL_ARRAY_BUFFER, toffset, tsize, textures)

            # colors:
            offset = c_void_p(psize)
            glEnableVertexAttribArray(1) # layout(location = 1)
            stride = 4 * colors.itemsize
            glVertexAttribPointer(1, 4, GL_FLOAT, False, stride, offset)

            # textures:
            offset = c_void_p(psize + csize)
            glEnableVertexAttribArray(2) # layout(location = 2)
            stride = 2 * textures.itemsize
            glVertexAttribPointer(2, 2, GL_FLOAT, False, stride, offset)


        elif self.colors != None:
            glBufferSubData(GL_ARRAY_BUFFER, coffset, csize, colors)

            # colors:
            offset = c_void_p(psize)
            glEnableVertexAttribArray(1) # layout(location = 1)
            stride = 4 * colors.itemsize
            glVertexAttribPointer(1, 4, GL_FLOAT, False, stride, offset)

        elif self.textures != None:
            glBufferSubData(GL_ARRAY_BUFFER, toffset, tsize, textures)

            # textures:
            offset = c_void_p(psize)
            glEnableVertexAttribArray(2) # layout(location = 2)
            stride = 2 * textures.itemsize
            glVertexAttribPointer(2, 2, GL_FLOAT, False, stride, offset)

        if self.textures != None:
            imgPath = fullpath(imgName)
            img = Image.open(imgPath).transpose(Image.FLIP_TOP_BOTTOM)
            imgData = np.fromstring(img.tobytes(), np.uint8)

            glEnable(GL_TEXTURE_2D)
            self.textureID = glGenTextures(1)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glBindTexture(GL_TEXTURE_2D, self.textureID)
            # set texture wrapping parameters
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            # set texture filtering parameters
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, img.size[0], img.size[1], GL_RGB, GL_UNSIGNED_BYTE, imgData)

        self.poffset = poffset
        self.psize = psize

        if self.colors != None:
            self.coffset = coffset
            self.csize = csize

        if self.textures != None:
            self.toffset = toffset
            self.tsize = tsize

        # unbind buffers:
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        if self.textures:
            glBindTexture(GL_TEXTURE_2D, 0)

    def draw(self, mode, size, offset):
        # bind the VAO, it contains all info about the buffers and attributes:
        glBindVertexArray(self.VAO)
        if self.textures:
            glBindTexture(GL_TEXTURE_2D, self.textureID)
        # to calculate the offset in bytes as required:
        offset = c_void_p(offset * self.indices.itemsize)
        # draw the data with the help of the indices:
        glDrawElements(mode, size, GL_UNSIGNED_INT, offset)

    def updatePositions(self, positions):
        self.positions = positions
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        positions = np.array(positions, dtype=np.float32)
        glBufferSubData(GL_ARRAY_BUFFER, self.poffset, self.psize, positions)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def move(self, x, y, z):
        new_positions = []
        for position in self.positions:
            position[0] += x
            position[1] += y
            position[2] += z
            new_positions.append(position)
        self.updatePositions(new_positions)

    def updateColors(self, colors):
        self.colors = colors
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        colors = np.array(colors, dtype=np.float32)
        glBufferSubData(GL_ARRAY_BUFFER, self.coffset, self.csize, colors)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def __repr__(self):
        return "data:\n{}\nindices:\n{}\n".format(self.data, self.indices)
