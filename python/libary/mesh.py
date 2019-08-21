from OpenGL.GL import *
from ctypes import c_void_p
import numpy as np

class Mesh():

    def __init__(self, positions, indices, colors=None, textures=None):
        """
        Create a Mesh which contains vertices, each vertex must have a
        position and indices to draw, optional are color and/or texture attribute
        The color/texture attribute can be set over colors/textures kwargs!

        The position attribute must be in [x, y, z] format!
        The color attribute must be in [r, g, b, a] format!
        The texture attribute must be in [s, t] format!

        All information is stored in the Mesh.data structured numpy array,
        or access the lists of attributes individually e.g: Mesh.positions and so on
        """
        self.positions = positions
        self.indices = indices
        self.colors = colors
        self.textures = textures

        if colors and textures:
            # use numpy to structure the data (memory layout is sequential):
            data = np.zeros(len(positions), [("position", np.float32, 3),
                                             ("color",    np.float32, 4),
                                             ("texture",  np.float32, 2)])
            data["position"] = positions
            data["color"] = colors
            data["texture"] = textures

        if colors:
            # use numpy to structure the data (memory layout is sequential):
            data = np.zeros(len(positions), [("position", np.float32, 3),
                                             ("color",    np.float32, 4)])
            data["position"] = positions
            data["color"] = colors

        if textures:
            # use numpy to structure the data (memory layout is sequential):
            data = np.zeros(len(positions), [("position", np.float32, 3),
                                             ("texture",  np.float32, 2)])
            data["position"] = positions
            data["texture"] = textures

        indices = np.array(indices, dtype=np.uint32)

        self.data = data
        self.indices = indices
        # vertex array object:
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # vertex buffer object:
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.data.nbytes, self.data, GL_STATIC_DRAW)

        # element buffer object:
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # number of bytes to go from one vertex to the next:
        self.stride = self.data.strides[0]

        if colors and textures:
            # positions:
            offset = c_void_p(0)
            glEnableVertexAttribArray(0) # layout(location = 0)
            glVertexAttribPointer(0, 3, GL_FLOAT, False, self.stride, offset)

            # colors:
            offset = c_void_p(self.data.dtype["position"].itemsize)
            glEnableVertexAttribArray(1) # layout(location = 1)
            glVertexAttribPointer(1, 4, GL_FLOAT, False, self.stride, offset)

            # textures:
            offset = c_void_p(self.data.dtype["position"].itemsize + self.data.dtype["color"].itemsize)
            glEnableVertexAttribArray(2) # layout(location = 2)
            glVertexAttribPointer(2, 2, GL_FLOAT, False, self.stride, offset)

        if colors:
            # positions:
            offset = c_void_p(0)
            glEnableVertexAttribArray(0) # layout(location = 0)
            glVertexAttribPointer(0, 3, GL_FLOAT, False, self.stride, offset)

            # colors:
            offset = c_void_p(self.data.dtype["position"].itemsize)
            glEnableVertexAttribArray(1) # layout(location = 1)
            glVertexAttribPointer(1, 4, GL_FLOAT, False, self.stride, offset)

        if textures:
            # positions:
            offset = c_void_p(0)
            glEnableVertexAttribArray(0) # layout(location = 0)
            glVertexAttribPointer(0, 3, GL_FLOAT, False, self.stride, offset)

            # textures:
            offset = c_void_p(self.data.dtype["position"].itemsize)
            glEnableVertexAttribArray(2) # layout(location = 2)
            glVertexAttribPointer(2, 2, GL_FLOAT, False, self.stride, offset)

        # unbind buffers:
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def draw(self, mode, size, offset):
        # bind the VAO, it contains all info about the buffers and attributes:
        glBindVertexArray(self.VAO)
        # to calculate the offset in bytes as required:
        offset = c_void_p(offset * self.indices.itemsize)
        # draw the data with the help of the indices:
        glDrawElements(mode, size, GL_UNSIGNED_INT, offset)

    def __repr__(self):
        return "data:\n{}\nindices:\n{}\n".format(self.data, self.indices)
