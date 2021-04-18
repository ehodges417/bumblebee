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

        collection = cls(units=data['units'], name=data['name'], body_frame=frames[0], visible=data['visible'])

        collection.nodes = frames+bodies+collections
        collection.init_rel_pose(collection.nodes)
        collection.rel_pose.pop(collection.body_frame)

        return collection

    def __init__(self, units='mm', name='RigidCollection', body_frame:Frame = None, visible=True):

        self.name = name
        self.units = pint.Unit(units)

        PlotObj.__init__(self, visible=visible, name=name, icon='cubes')
        
        self.body_frame = body_frame if body_frame else Frame(name='Body Frame')        
        self.add_node(self.body_frame)

        self.rel_pose = {}

    @property
    def tf(self):
        return self.body_frame.tf

    @tf.setter
    def tf(self, value):
        self.body_frame.tf = value
        self.update()

    def bind(self, csys, parent=True):
        self.csys = csys
        for plot_obj in self.nodes:
            plot_obj.bind(csys, parent=False)

        if parent:
            self.csys.update()   

    def add(self, plot_obj):
        self.add_node(plot_obj)
        if hasattr(self, 'csys'):
            plot_obj.bind(self.csys, parent=False)
            plot_obj.plot(self.csys.ax)
        self.init_rel_pose([plot_obj])

    def init_rel_pose(self, nodes):
        inv = self.body_frame.inv_tf.copy()
        for node in nodes:
            self.rel_pose[node] = inv @ node.tf
            node.parent = self

    def to_dict(self):
        return {
            'type': 'RigidCollection',
            'name': self.name,
            'visible': self.visible,
            'units': f'{self.units:~}',
            'nodes': [node.to_dict() for node in self.nodes],
        }

    def duplicate(self, name=None):
        new_collection = RigidCollection.from_dict(self.to_dict())
        if name:
            new_collection.name = name
        return new_collection

    @PlotObj.tree_update
    def translate(self, translation):        
        self.body_frame.translate(translation, inner=True)

        # TODO more elegant workaround
        if hasattr(self, 'parent'):
            self.parent.init_rel_pose([self])

    @PlotObj.tree_update
    def _rotate(self, R, about, sweep):
        self.body_frame._rotate(R, about, sweep, inner=True)

        # TODO more elegant workaround
        if hasattr(self, 'parent'):
            self.parent.init_rel_pose([self])

    @PlotObj.tree_update
    def transform(self, matrix):
        self.body_frame.transform(matrix, inner=True)

        # TODO more elegant workaround
        if hasattr(self, 'parent'):
            self.parent.init_rel_pose([self])

    @PlotObj.bound_update
    def update(self, inner=False):

        for node in self.nodes[1:]:
            node.tf = self.body_frame.tf @ self.rel_pose[node]
            node.update(inner=True)

        self.body_frame.update(inner=True)

    def plot(self, ax):
        for node in self.nodes:
            node.plot(ax)
     
    @PlotObj.bound_update
    def set_vis(self, vis):
        self.visible = vis
        for plot_obj in self.nodes:
            plot_obj.set_vis(vis, inner=True)
