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

        collections = [RigidCollection.from_dict(node) for node in data['nodes'] if node['type'] == 'RigidCollection']
        bodies= [RigidBody.from_dict(node) for node in data['nodes'] if node['type'] == 'RigidBody']
        frames = [Frame.from_dict(node) for node in data['nodes'] if node['type'] == 'Frame']

        collection = cls(units=data['units'], name=data['name'], body_frame=frames[0])

        collection.nodes = frames+bodies+collections
        collection.init_rel_pose(collection.nodes)
        collection.rel_pose.pop(collection.body_frame)

        return collection

    def __init__(self, units='mm', name='RigidCollection', body_frame:Frame = None):

        self.name = name
        self.units = pint.Unit(units)

        PlotObj.__init__(self, name=name, icon='cubes')
        
        self.body_frame = body_frame if body_frame else Frame(name='Body Frame')        
        self.add_node(self.body_frame)

        self.rel_pose = {}

    @property
    def tf(self):
        return self.body_frame.tf

    @tf.setter
    def tf(self, value):
        self.body_frame.tf = value

    def bind(self, figure):

        for plot_obj in self.nodes:
            plot_obj.bind(figure)

    def add(self, plot_obj):
        self.add_node(plot_obj)
        self.init_rel_pose([plot_obj])

    def init_rel_pose(self, nodes):
        inv = self.body_frame.inv_tf.copy()
        for node in nodes:
            self.rel_pose[node] = inv @ node.tf

    def to_dict(self):
        return {
            'type': 'RigidCollection',
            'name': self.name,
            'units': f'{self.units:~}',
            'nodes': [node.to_dict() for node in self.nodes],
        }

    def duplicate(self, name=None):
        new_collection = RigidCollection.from_dict(self.to_dict())
        if name:
            new_collection.name = name
        return new_collection

    def translate(self, translation):
        
        self.body_frame.translate(translation)
        self.update_children()

    def _rotate(self, R, about, sweep):

        self.body_frame._rotate(R, about, sweep)
        self.update_children()
        self.body_frame.update_plot()

    def transform(self, matrix):

        self.body_frame.transform(matrix)
        self.update_children()

    def update_children(self):

        for node in self.nodes[1:]:
            node.tf = self.body_frame.tf @ self.rel_pose[node]
            node.update_plot()

        self.body_frame.update_plot()

    def update_plot(self):

        self.update_children()

    def set_vis(self, vis):
        self.visibility = vis
        for plot_obj in self.nodes:
            plot_obj.set_vis(vis)
