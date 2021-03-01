import numpy as np
import plotly.graph_objects as go

from bumblebee.PlotObj import PlotObj
from ipytree import Node

class Frame(PlotObj):

    def __init__(
        self, 
        tf:np.array = np.eye(4),
        name:str = 'Frame',
        xcolor:str = 'rgb(128,0,0)',
        ycolor:str = 'rgb(0,128,0)',
        zcolor:str = 'rgb(0,0,128)',
        linewidth = 6,
        scale = 1,
    ):
        """
        tf: 4x4 np.array transformation matrix
        """
        self.tf = tf
        self.name = name
        self.xcolor = xcolor
        self.ycolor = ycolor
        self.zcolor = zcolor
        self.linewidth = linewidth
        self.scale = scale
        self.node = Node(name, icon='crosshairs')
        self.node.uids = []

    def translate(self, transform):
        self.tf[3,0] += transform[0]
        self.tf[3,1] += transform[1]
        self.tf[3,2] += transform[2]

    def rotate(self, rotation):
        self.tf[0:3, 0:3] = self.tf[0:3, 0:3] @ rotation 

    def transform(self, transform):
        self.tf = tf @ transform

    # to adjust individual colors use x,y,z color properties
    def fill(self, color):
        self.xcolor = color
        self.ycolor = color
        self.zcolor = color

    def _plot_vector3d(self, start, end, color):
        x,y,z = zip(start, end)
        marker = dict(size=1, color=color)
        line = dict(color=color, width=self.linewidth)
        trace = go.Scatter3d(x=x, y=y, z=z, marker=marker, line=line)
        return trace

    def plot(self):
        origin = self.tf[0:3,3]
        x_end = origin + self.scale*self.tf[0:3,0]
        y_end = origin + self.scale*self.tf[0:3,1]
        z_end = origin + self.scale*self.tf[0:3,2]
        xvector = self._plot_vector3d(origin, x_end, color=self.xcolor)
        yvector = self._plot_vector3d(origin, y_end, color=self.ycolor)
        zvector = self._plot_vector3d(origin, z_end, color=self.zcolor)
        return [xvector, yvector, zvector]
    