from bumblebee.Frame import Frame
from bumblebee.RigidBody import RigidBody
from bumblebee.RigidCollection import RigidCollection

from ipywidgets import HBox, Layout
from ipytree import Tree, Node
import plotly.graph_objects as go
import json, re

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
        
        self.layout = go.Layout(
            scene = dict(aspectmode='data'),
            scene_xaxis_visible=False,
            scene_yaxis_visible=False,
            scene_zaxis_visible=False,
            showlegend=False
        )

        self.tree = Tree()
        self.fig = go.FigureWidget(layout=self.layout)
        
        self.add(Frame(name="Origin"))

    def add(self, plot_obj):
        """
        Adds any plot object (RigidCollection, RigidBody, Frame, Axis) 
        to the coordinate system. Binds any updates to these parts
        to the plot so that it automatically updates.
        """
        self.tree.add_node(plot_obj)
        plot_obj.bind(self.fig)

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

    def plot(self):
        """
        Returns a widget of the part tree and 3D figure combined.
        """
        return HBox([self.tree, self.fig])
