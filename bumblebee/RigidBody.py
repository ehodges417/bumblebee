import math
import pint
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import modern_robotics as mr
from stl.mesh import Mesh
from ipytree import Node

from bumblebee.Frame import Frame
from bumblebee.PlotObj import PlotObj
from numba import njit

class RigidBody(PlotObj):
    """
    A collection of a STL mesh and a number of named frames
    which transform together as a unit.
    """

    @classmethod
    def from_dict(cls, data):

        frames = [Frame.from_dict(node) for node in data['nodes'] if node['type'] == 'Frame']
        body = cls(data['mesh'], units=data['units'], name=data['name'], body_frame=frames[0], visible=data['visible'])
        body.nodes = frames
        return body

    def __init__(self, path, units='mm', name='RigidBody', body_frame:Frame = None, visible=True):
        self.mesh = Mesh.from_file(path)
        self.path = path
        self.name = name
        self.units = pint.Unit(units)

        PlotObj.__init__(self, visible=visible, name=name, icon='cube')
        
        self.body_frame = body_frame if body_frame else Frame(name='Body Frame')        
        self.add_node(self.body_frame)

    @property
    def tf(self):
        return self.body_frame.tf

    @tf.setter
    def tf(self, value):
        self.body_frame.tf = value

    def bind(self, csys, parent=True):
        self.csys = csys

        for frame in self.nodes:
            frame.bind(csys, parent=False)

        if parent:
            self.csys.update()

    def to_dict(self):
        return {
            'type': 'RigidBody',
            'name': self.name,
            'mesh': self.path,
            'visible': self.visible,
            'units': f'{self.units:~}',
            'nodes': [node.to_dict() for node in self.nodes],
        }

    def scale(self, scale_factor:float, fp:np.array=None):
        """
        scale_factor: float (factor to scale by)
        fp: np.array fixed point in 3d space [x,y,z]
        """

        if fp is None:
            fp = self.origin[3, 0:3]

        disp = -(scale_factor*fp - fp) #get displacement due to scale to find translation
        self.vectors *= scale_factor
        self.translate(disp)

    def change_units(self, new_unit):

        conversion = ((1*self.units).to(pint.Unit(new_unit))).m
        self.units = pint.Unit(new_unit)

        self.scale(conversion)

    def duplicate(self, inplace=False, name='RigidBody'):
        newbody = RigidBody(self.path, self.units, name)
        if inplace:
            newbody.body_frame.tf = self.body_frame.tf.copy()

        return newbody

    @PlotObj.tree_update
    def translate(self, translation):

        # translate attached frames
        for frame in self.nodes:
            frame.translate(translation, inner=True)

        # TODO more elegant workaround
        if hasattr(self, 'parent'):
            self.parent.init_rel_pose([self])

    @PlotObj.tree_update
    def _rotate(self, R, about='origin', sweep=False):
        for frame in self.nodes:
            frame._rotate(R, about, sweep, inner=True)

        # TODO more elegant workaround
        if hasattr(self, 'parent'):
            self.parent.init_rel_pose([self])

    @PlotObj.tree_update
    def transform(self, matrix):

        # translate attached frames
        for frame in self.nodes:
            frame.transform(matrix, inner=True)

        # TODO more elegant workaround
        if hasattr(self, 'parent'):
            self.parent.init_rel_pose([self])

    def add_frame(self, frame:Frame):
        self.add_node(frame)

    def plot(self, ax):
        self.plot_body(ax)

        for frame in self.nodes:
            frame.plot(ax)

    @staticmethod
    @njit
    def get_triangles(vectors, tf):
        new_ts=[]
        for i in range(len(vectors)):
            new_t = np.ones((4,3))
            new_t[0:3,0:3] = vectors[i].T
            new_t = (tf @ new_t).T
            new_ts.append(new_t[:,0:3])

        return new_ts

    def plot_body(self, ax, colorscale=None):

        new_ts = self.get_triangles(self.mesh.vectors, self.body_frame.tf)

        if self.visible:
            self.trace = ax.add_collection3d(mplot3d.art3d.Poly3DCollection(new_ts, edgecolors='Black', facecolors = 'Grey', linewidths=0.1, alpha=0.2))
        # TODO wireframe
        # ax.add_collection3d(mplot3d.art3d.Line3DCollection(new_ts, edgecolors='Black'))
    
    @PlotObj.bound_update
    def set_vis(self, vis):
        self.visible = vis
        if hasattr(self, 'trace'):
            self.trace._visible = vis

        # set visiblity of attached frames
        for frame in self.nodes:
            frame.set_vis(vis, inner=True)

    @PlotObj.bound_update
    def update(self):

        for frame in self.nodes:
            frame.update(inner=True)

        if hasattr(self, 'trace'):
            self.trace.remove()
            self.plot_body(self.csys.ax)