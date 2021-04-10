from ipytree import Node
from scipy.spatial.transform import Rotation
import json, re
import uuid

class PlotObj(Node):
    """
    A parent class for RigidCollection, RigidBody,
    Frame, and Axis. Forces each class to inherit from Node,
    as well as contain bind/plot methods.
    """

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            data = json.load(f)

        return cls.from_dict(data)

    def __init__(self, visible=True, **kwargs):
        """
        Enforce inheritance from Node in child classes of PlotObj.
        This assists in generating the part tree.
        """
        Node.__init__(self, **kwargs)
        # self.uid = uuid.uuid4()
        self.opened = False #default to collapsed in tree
        self.visible = visible #default to visible in plot

    def set_vis(self, vis): raise Exception('set_vis method not overriden in child class!')
    def bind(self, figure): raise Exception('bind method not overriden in child class!')
    def to_dict(self): raise Exception('to_dict method not overriden in child class!')
    def plot(self): raise Exception('plot method not overriden in child class!')  

    # support scipy rotation inputs
    def _rotate(self, R, about, sweep): raise Exception('_rotate method not overriden in child class!')
    def rotate_from_quat(self, *args, about='origin', sweep=False, **kwargs): 
        self._rotate(Rotation.from_quat(*args, **kwargs), about, sweep)
    def rotate_from_matrix(self, *args, about='origin', sweep=False, **kwargs): 
        self._rotate(Rotation.from_matrix(*args, **kwargs), about, sweep)
    def rotate_from_rotvec(self, *args, about='origin', sweep=False, **kwargs): 
        self._rotate(Rotation.from_rotvec(*args, **kwargs), about, sweep)
    def rotate_from_euler(self, *args, about='origin', sweep=False, **kwargs): 
        self._rotate(Rotation.from_euler(*args, **kwargs), about, sweep)

    def toggle_vis(self):
        self.visible = not self.visible
        self.set_vis(self.visible)

    def to_json(self, path):

        with open(f'{path}.json', 'w') as outfile:
            json.dump(self.to_dict(), outfile, indent=2)

        # rewrites the file after collapsing transforms. Makes save files human readable.
        with open(f'{path}.json', 'r+') as f:
            text = re.sub('(\[)\s*([0-9.e-]+,)\s*([0-9.e-]+,)\s*([0-9.e-]+,)\s*([0-9.e-]+)\s*(\])', r'\1\2 \3 \4 \5\6', f.read())
            f.seek(0)
            f.write(text)
            f.truncate()

    # Think this is handled by node class
    # def __hash__(self):
    #     return hash(self.uid)

    # def __eq__(self, other):
    #     return self.__class__ == other.__class__ and self.uid == other.uid
