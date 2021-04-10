import math
import pint
import numpy as np
import plotly.graph_objects as go
import modern_robotics as mr
from stl.mesh import Mesh
from ipytree import Node

from bumblebee.Frame import Frame
from bumblebee.PlotObj import PlotObj

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
        self.init_points(Mesh.from_file(path))
        self.path = path
        self.name = name
        self.units = pint.Unit(units)

        PlotObj.__init__(self, visible=visible, name=name, icon='cube')
        
        self.body_frame = body_frame if body_frame else Frame(name='Body Frame')        
        self.add_node(self.body_frame)

    def init_points(self, mesh):
        self.pts = np.vstack((
            np.concatenate(mesh.x),
            np.concatenate(mesh.y),
            np.concatenate(mesh.z),
            np.ones(mesh.x.size)
        ))
        self.num_pts = mesh.vectors.shape[0]*3

    @property
    def tf(self):
        return self.body_frame.tf

    @tf.setter
    def tf(self, value):
        self.body_frame.tf = value

    def bind(self, figure):
        figure.add_trace(self.plot_body())
        self.trace = figure.data[-1]

        for frame in self.nodes:
            frame.bind(figure)

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

    def translate(self, translation):

        # translate attached frames
        for frame in self.nodes:
            frame.translate(translation)

        self.update_plot()

    def _rotate(self, R, about='origin', sweep=False):
        for frame in self.nodes:
            frame._rotate(R, about, sweep)

        self.update_plot()

    def transform(self, matrix):

        # translate attached frames
        for frame in self.nodes:
            frame.transform(matrix)

        self.update_plot()

    def add_frame(self, frame:Frame):
        self.add_node(frame)

    def plot_body(self, colorscale=None):

        pts = self.body_frame.tf @ self.pts

        trace = go.Mesh3d(
            x=pts[0],
            y=pts[1],
            z=pts[2],
            colorscale=colorscale if colorscale else ([0, 'rgb(153, 153, 153)'], [1., 'rgb(255,255,255)']), 
            intensity= pts[2],
            flatshading=True,
            i = list(range(0,self.num_pts,3)),
            j = list(range(1,self.num_pts,3)),
            k = list(range(2,self.num_pts,3)),
            name=self.name,
            showscale=False,
            lighting=dict(ambient=0.18, diffuse=1, fresnel=0.1, specular=1, roughness=0.05, facenormalsepsilon=1e-15,
                                vertexnormalsepsilon=1e-15),
        )

        trace.visible = self.visible
        return trace
    
    def set_vis(self, vis):
        self.visible = vis

        if vis:
            self.update_mesh()

        # set visiblity of attached frames
        for frame in self.nodes:
            frame.set_vis(vis)

        # set visibility of body mesh
        if hasattr(self, 'trace'):
            self.trace.visible = vis

    def update_mesh(self):
        if self.visible:
            if hasattr(self, 'trace'):
                pts = self.body_frame.tf @ self.pts
                self.trace.x = list(pts[0])
                self.trace.y = list(pts[1])
                self.trace.z = list(pts[2])

    def update_plot(self):
        
        self.update_mesh()

        for frame in self.nodes:
            frame.update_plot()