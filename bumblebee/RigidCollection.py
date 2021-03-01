import pint
from ipytree import Node

from bumblebee.RigidBody import RigidBody
from bumblebee.PlotObj import PlotObj
from bumblebee.Frame import Frame

class RigidCollection(PlotObj):

    def __init__(self, units='mm', name='RigidCollection'):

        self.name = name
        self.units = pint.Unit(units)

        self.node = Node(name=name, icon='cubes')
        self.body_frame = Frame(name='Collection Frame')
        self.node.add_node(self.body_frame.node)
        self.bodies = {}
        self.frames = {}

    def translate(self):
        pass

    def rotate(self):
        pass

    def transform(self):
        pass

    def add_frame(self):
        pass

    def add_body(self):
        pass

    def plot_frames(self):
        pass

    def plot_bodies(self):
        pass

    def plot(self):
        pass
