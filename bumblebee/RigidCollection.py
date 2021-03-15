import pint
from ipytree import Node

from bumblebee.RigidBody import RigidBody
from bumblebee.PlotObj import PlotObj
from bumblebee.Frame import Frame

class RigidCollection(PlotObj):
    """
    A collection of RigidBody and Frame objects that
    are transformed as a single unit.
    """

    @classmethod
    def from_dict(cls, data):

        bodies= [RigidBody.from_dict(node) for node in data['nodes'] if node['type'] == 'RigidBody']
        frames = [Frame.from_dict(node) for node in data['nodes'] if node['type'] == 'Frame']


        collection = cls(units=data['units'], name=data['name'], body_frame=frames[0])

        collection.nodes = frames+bodies

        return collection

    def __init__(self, units='mm', name='RigidCollection', body_frame:Frame = None):

        self.name = name
        self.units = pint.Unit(units)

        PlotObj.__init__(self, name=name, icon='cubes')
        
        self.body_frame = body_frame if body_frame else Frame(name='Body Frame')        
        self.add_node(self.body_frame)

    def bind(self, figure):

        for plot_obj in self.nodes:
            plot_obj.bind(figure)

    def add(self, plot_obj):
        self.add_node(plot_obj)

    def to_dict(self):
        return {
            'type': 'RigidCollection',
            'name': self.name,
            'units': f'{self.units:~}',
            'nodes': [node.to_dict() for node in self.nodes],
        }

    def translate(self, translation):
        
        for plot_obj in self.nodes:
            plot_obj.translate(translation)

    def _rotate(self, R, about='origin', sweep=True):

        for plot_obj in self.nodes:
            plot_obj._rotate(R, sweep=True)

    def transform(self, matrix):

        for plot_obj in self.nodes:
            plot_obj.transform(matrix)

    def set_vis(self, vis):
        self.visibility = vis
        for plot_obj in self.nodes:
            plot_obj.set_vis()
