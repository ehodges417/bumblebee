import numpy as np
from matplotlib import pyplot as plt

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
        linewidth = 6,
        visible = True
    ):
        """
        Takes a start point and end point in 3D space
        """
        self.name = name
        self.start = start
        self.end = end
        self.color = color
        self.linewidth = linewidth

        PlotObj.__init__(self, visible=visible, name=name, icon='line')

    def to_dict(self):
        pass

    def plot(self, ax):
        x,y,z = zip(self.start, self.end)
        if self.visible:
            self.trace, = ax.plot(x, y, z, self.color)

    @PlotObj.bound_update
    def set_vis(self, vis):
        self.visible = vis
        if hasattr(self, 'trace'):
            self.trace._visible=vis