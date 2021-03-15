import numpy as np
import plotly.graph_objects as go

from bumblebee.Axis import Axis
from bumblebee.PlotObj import PlotObj
from ipytree import Node

class Frame(PlotObj):
    """
    A transform in 3D space plotted as the unit
    vectors at the transform location.
    """

    @classmethod
    def from_dict(cls, data):       
        return cls(np.array(data['tf']), name=data['name'], scale=data['scale'], linewidth=data['linewidth'])

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
        self.tf = tf.copy()
        self.name = name
        self.linewidth = linewidth
        self.scale = scale

        origin, end_pts = self.axis_pts()
        colors = [xcolor, ycolor, zcolor]
        self.axes = [Axis(name, origin, end_pts[i], colors[i], linewidth) for i, name in enumerate(['x-axis', 'y-axis', 'z-axis'])]
        
        PlotObj.__init__(self, name=name, icon='crosshairs')
        for axis in self.axes:
            self.add_node(axis)

    @property
    def inv_tf(self):
        Rt = self.tf[0:3,0:3].T
        return np.r_[np.c_[Rt, -np.dot(Rt, self.tf[0:3,3])], [[0, 0, 0, 1]]]

    def bind(self, figure):
        for axis in self.axes:
            axis.bind(figure)

    def to_dict(self):
        return {
            'type': 'Frame',
            'name': self.name,
            'tf': self.tf.tolist(),
            'linewidth': self.linewidth,
            'scale': self.scale,
        }

    def translate(self, translation):
        self.tf[0,3] += translation[0]
        self.tf[1,3] += translation[1]
        self.tf[2,3] += translation[2]

        self.update_plot()

    def _rotate(self, R, about='origin', sweep=False):

        if about == 'origin':
            # use origin as reference for x, y, z
            self.tf[0:3, 0:3] = R.as_matrix() @ self.tf[0:3, 0:3]
            if sweep:
                self.tf[0:3, 3] = R.as_matrix() @ self.tf[0:3, 3] 
        elif about == 'body':
            # use body as reference for x, y, z
            self.tf[0:3, 0:3] = self.tf[0:3, 0:3] @ R.as_matrix()
        

        self.update_plot()

    def transform(self, transform):
        self.tf = self.tf @ transform

        self.update_plot()

    def axis_pts(self):
        origin = self.tf[0:3,3]
        x_end = origin + self.scale*self.tf[0:3,0]
        y_end = origin + self.scale*self.tf[0:3,1]
        z_end = origin + self.scale*self.tf[0:3,2]

        return origin, [x_end, y_end, z_end]

    def plot(self):
        return [axis.plot() for axis in self.axes]
    
    def set_vis(self, vis):
        self.visable = vis
        for axis in self.axes:
            axis.set_vis(vis)

    def update_plot(self):
        origin, end_pts = self.axis_pts()
        
        for i, axis in enumerate(self.axes):
            if hasattr(axis, 'trace'):
                axis.start = origin
                axis.end = end_pts[i]
                axis.update_plot()