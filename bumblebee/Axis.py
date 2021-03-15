import numpy as np
import plotly.graph_objects as go

from bumblebee.PlotObj import PlotObj
from ipytree import Node

class Axis(PlotObj):
    """
    A vector in 2D space.
    """

    def __init__(
        self,
        name,
        start,
        end,
        color,
        linewidth = 6
    ):
        """
        Takes a start point and end point in 3D space
        """
        self.name = name
        self.start = start
        self.end = end
        self.color = color
        self.linewidth = linewidth

        PlotObj.__init__(self, name=name, icon='line')

    def bind(self, figure):
        figure.add_trace(self.plot())
        self.trace = figure.data[-1]

    def to_dict(self):
        pass

    def plot(self):
        x,y,z = zip(self.start, self.end)
        marker = dict(size=1, color=self.color)
        line = dict(color=self.color, width=self.linewidth)
        trace = go.Scatter3d(x=x, y=y, z=z, marker=marker, line=line)
        return trace

    def set_vis(self, vis):
        self.visable = vis
        if hasattr(self, 'trace'):
            self.trace.visible = vis

    def update_plot(self):
        x,y,z = zip(self.start, self.end)

        if hasattr(self, 'trace'):
            self.trace.x = list(x)
            self.trace.y = list(y)
            self.trace.z = list(z)