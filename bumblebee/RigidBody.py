import math
import pint
import numpy as np
import plotly.graph_objects as go
import modern_robotics as mr
from stl.stl import BaseStl
from stl.base import BaseMesh
from ipytree import Node

from bumblebee.Frame import Frame
from bumblebee.PlotObj import PlotObj

class RigidBody(BaseStl, PlotObj):

    def __init__(self, path, units='mm', name='RigidBody'):
        BaseMesh.__init__(self, BaseStl.from_file(path).data)
        self.path = path
        self.name = name
        self.units = pint.Unit(units)
        self.shape = self.vectors.shape

        self.node = Node(name=name, icon='cube')
        self.node.uids = []
        self.body_frame = Frame(name='Body Frame')
        self.node.add_node(self.body_frame.node)
        self.frames = {}

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

    def translate(self, translation):
        
        super().translate(translation)
        
        tf = mr.RpToTrans(np.eye(3),translation)

        self.body_frame.tf = self.body_frame.tf @ tf
        for name, frame in self.frames.items():
            self.frames[name].tf = frame.tf @ tf

    def transform(self, matrix):

        super().transform(matrix)

        self.body_frame = matrix @ self.body_frame
        for name, frame in self.frames.items():
            self.frames[name] = matrix @ frame.tf

    def add_frame(self, frame:Frame):
        self.frames[frame.node.name] = frame
        self.node.add_node(frame.node)

    def plot_frame(self, name):
        return self.frames[name].plot()

    def plot_frames(self):
        return [vector for frame in self.frames.values() for vector in frame.plot()]

    def plot_origin(self):
        return self.body_frame.plot()

    def plot_body(self, colorscale=None):

        if colorscale is None: 
            colorscale=[0, 'rgb(153, 153, 153)'], [1., 'rgb(255,255,255)']

        return go.Mesh3d(
            x=np.concatenate(self.x),
            y=np.concatenate(self.y),
            z=np.concatenate(self.z),
            colorscale=colorscale, 
            intensity= np.concatenate(self.z),
            flatshading=True,
            i = list(range(0,self.shape[0]*3,3)),
            j = list(range(1,self.shape[0]*3,3)),
            k = list(range(2,self.shape[0]*3,3)),
            name=self.name,
            showscale=False,
            lighting=dict(ambient=0.18,
                                diffuse=1,
                                fresnel=0.1,
                                specular=1,
                                roughness=0.05,
                                facenormalsepsilon=1e-15,
                                vertexnormalsepsilon=1e-15),
            lightposition=dict(x=100,
                                y=200,
                                z=0
                                )
        )

    def plot(self):       
        return self.plot_frames() + self.plot_origin() + [self.plot_body()]