from bumblebee.Frame import Frame
from bumblebee.RigidBody import RigidBody
from bumblebee.RigidCollection import RigidCollection

from ipywidgets import HBox, Layout
from ipytree import Tree, Node
import plotly.graph_objects as go

class PlotWidget:

    def __init__(self, layout=None):
        
        self.part_tree = Tree()
        self.origin = Frame(name="Origin")

        self.part_tree.add_node(self.origin.node)

        self.layout = go.Layout(
            scene = dict(aspectmode='data'),
            scene_xaxis_visible=False,
            scene_yaxis_visible=False,
            scene_zaxis_visible=False,
            showlegend=False
        )
        self.fig = go.FigureWidget(layout=self.layout)

        for vector in self.origin.plot():
            self.fig.add_trace(vector)
            self.origin.node.uids.append(self.fig.data[-1].uid)

        self.plot_objs = {}
        self.trace_registry = {}

    def add(self, plot_obj):
        self.plot_objs[plot_obj.name] = plot_obj
        self.part_tree.add_node(plot_obj.node)

        if isinstance(plot_obj, Frame):
            for vector in plot_obj.plot():
                self.fig.add_trace(vector)
                self.plot_objs[plot_obj.name].node.uids.append(self.fig.data[-1].uid)
        
        elif isinstance(plot_obj, RigidBody):
            self.fig.add_trace(plot_obj.plot_body())
            self.plot_objs[plot_obj.name].node.uids.append(self.fig.data[-1].uid)

            for vector in plot_obj.plot_origin():
                self.fig.add_trace(vector)
                self.plot_objs[plot_obj.name].body_frame.node.uids.append(self.fig.data[-1].uid)

            for name, frame in plot_obj.frames.items():
                for vector in frame.plot():
                    self.fig.add_trace(vector)
                    self.plot_objs[plot_obj.name].frames[name].node.uids.append(self.fig.data[-1].uid)
        
        elif isinstance(plot_obj, RigidCollection):
            self.fig.add_trace(plot_obj)

        else:
            raise Exception('Type Not supported!')

        self.register_traces()

    def register_traces(self):
        registry = {}
        for i, entry in enumerate(self.fig.data):
            registry[entry.uid] = i

        self.trace_registry = registry

    def plot(self):
        return HBox([self.part_tree, self.fig])
