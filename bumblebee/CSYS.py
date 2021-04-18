from bumblebee.Frame import Frame
from bumblebee.RigidBody import RigidBody
from bumblebee.RigidCollection import RigidCollection

from IPython.display import display
from ipywidgets import HBox, Layout, Output
from ipytree import Tree, Node
from matplotlib import pyplot as plt
from matplotlib import rc
import json, re
import numpy as np
from copy import deepcopy
import pickle
import io

#sets matplotlib to run as widget if in jupyter env
ipython = True
try:
    get_ipython().magic('matplotlib widget')
except:
    ipython = False
    pass

class CSYS:
    """
    Coordinate SYStem. Is the global coordinate system intended to 
    contain all objects. Also functions as a plotting widget
    which automatically updates.
    """

    def __init__(self, layout=None):
        """
        Set default plot layout, add part tree,
        add plot (fig)
        """

        self.tree = Tree()
        
        self.new_fig()
        
        self.add(Frame(name="Origin"))

    def new_fig(self):

        old_fig = getattr(self, 'fig', None)
        self.fig = None

        # catch jupyter output from creating figure
        if ipython:
            output = Output()
            with output:
                self.fig = plt.figure(figsize=(8,8))
        else:
            self.fig = plt.figure()

        # catch the current interactive plot
        self.output = Output()

        plt.axis('off')
        plt.margins(0, x=None, y=None, tight=True)
        rc('axes',edgecolor=(1,1,1,0))

        old_ax = getattr(self, 'ax', None)
        self.ax = self.fig.add_subplot(111, projection='3d')

        if old_fig is not None:
            self.fig.canvas.toolbar_visible = old_fig.canvas.toolbar_visible
            self.fig.canvas.header_visible = old_fig.canvas.header_visible
            self.fig.canvas.footer_visible = old_fig.canvas.footer_visible
        else:
            self.fig.canvas.toolbar_visible = False
            self.fig.canvas.header_visible = False
            self.fig.canvas.footer_visible = False

        if old_ax is not None:
            self.ax.set_position(old_ax.get_position())
            self.ax.grid(old_ax.grid)
            self.ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_zticks([])
            self.ax.set_xlim(old_ax.get_xlim())
            self.ax.set_ylim(old_ax.get_ylim())
            self.ax.set_zlim(old_ax.get_zlim())
        else:
            self.ax.set_position([0,0,1,1])
            self.ax.grid(False)
            self.ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_zticks([])

    def add(self, plot_obj):
        """
        Adds any plot object (RigidCollection, RigidBody, Frame, Axis) 
        to the coordinate system. Binds any updates to these parts
        to the plot so that it automatically updates.
        """
        self.tree.add_node(plot_obj)
        plot_obj.bind(self)
        plot_obj.plot(self.ax)

    def save(self, path):
        data = {}
        data['nodes'] = [node.to_dict() for node in self.tree.nodes]

        with open(f'{path}.json', 'w') as outfile:
            json.dump(data, outfile, indent=2)

        # rewrites the file after collapsing transforms. Makes save files human readable.
        with open(f'{path}.json', 'r+') as f:
            text = re.sub('(\[)\s*([0-9.e-]+,)\s*([0-9.e-]+,)\s*([0-9.e-]+,)\s*([0-9.e-]+)\s*(\])', r'\1\2 \3 \4 \5\6', f.read())
            f.seek(0)
            f.write(text)
            f.truncate()

    def open(self, path):
        # clear the object
        self.tree = Tree()
        self.fig = go.FigureWidget(layout=self.layout)

        with open(path) as f:
            data = json.load(f)

        for node in data['nodes']:
            if node['type'] == 'RigidCollection':
                plot_obj = RigidCollection.from_dict(node)
            elif node['type'] == 'RigidBody':
                plot_obj = RigidBody.from_dict(node)
            elif node['type'] == 'Frame':
                plot_obj = Frame.from_dict(node)
            else:
                raise Exception('UH OH')

            plot_obj.opened = False #collapse the tree
            self.add(plot_obj)

    def update(self):

        self.fig.canvas.draw_idle()

    def copy_fig(self):
        buf = io.BytesIO()
        pickle.dump(self.fig, buf)
        buf.seek(0)
        self.fig = pickle.load(buf) 

    def plot(self, new=True):
        """
        Returns a widget of the part tree and 3D figure combined.
        """

        if new:
            self.new_fig()
            for node in self.tree.nodes:
                node.plot(self.ax)
                node.update()

        return HBox([self.tree, self.fig.canvas])
