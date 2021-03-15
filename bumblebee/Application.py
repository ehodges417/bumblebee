import tkinter as tk
from tkinter import filedialog as fd

from ipywidgets import Button, HBox, VBox, Checkbox, ToggleButtons, FloatText, RadioButtons, Label, Tab
from ipytree import Tree, Node

from bumblebee.CSYS import CSYS
from bumblebee.RigidBody import RigidBody

class FileTab:
    #_____________________________
    #|_File_|_____________________|
    #|_Open_|_Save_|_Insert_|_____|

    def __init__(self, parent):

        self.parent = parent
        self.open_btn = Button(description='Open', icon='folder-open')
        self.save_btn = Button(description='Save', icon='save')
        self.insert_btn = Button(description='Insert', icon='cube')
        self.insert_btn.on_click(self.select_files)

        self.grid = HBox([self.open_btn, self.save_btn, self.insert_btn])

    def select_files(self, b):
        root = tk.Tk()
        root.withdraw()                                        # Hide the main window.
        root.call('wm', 'attributes', '.', '-topmost', True)   # Raise the root to the top of all windows.
        path = fd.askopenfilename(filetypes=[("stl files","*.stl")])
        self.parent.parent.csys.add(RigidBody(path, name=path.split('/')[-1][:-4]))


class ViewTab:
    #________________________________
    #|______|_View_|______|_______|__|
    #|x_Frames__|                    |
    #|x_Bodies__| Shaded | Wireframe |
    #|x_Origin__|____________________|

    def __init__(self, parent):
        
        self.parent = parent
        self.frames_chk = Checkbox(value=True, description='Frames')
        self.bodies_chk = Checkbox(value=True, description='Bodies')
        self.origin_chk = Checkbox(value=True, description='Origin')

        self.shade_style = ToggleButtons(options=['Shaded', 'Wireframe'], description='Shading:')

        self.vis_toggle = VBox([self.frames_chk, self.bodies_chk, self.origin_chk])
        self.grid = HBox([self.vis_toggle, self.shade_style])

class MoveTab:
    #_________________________________
    #|______|______|_Move_|_____|_____|
    #|Translate  |  Rotate  |         |
    #|X: __      | x X      | Preview |
    #|Y: __      | x Y      | Apply   |
    #|Z: __ _____|_x_Z______|_________|

    def __init__(self, parent):
        
        self.parent = parent
        self.x_trans = FloatText(value=0.0, description='X:', disabled=False)
        self.y_trans = FloatText(value=0.0, description='Y:', disabled=False)
        self.z_trans = FloatText(value=0.0, description='Z:', disabled=False)
        self.trans_box = VBox([Label('Translate'), self.x_trans, self.y_trans, self.z_trans])

        self.rot_axis = RadioButtons(options=['X-axis', 'Y-axis', 'Z-axis'])
        self.rot_mag = FloatText(value=0.0, description='Degrees: ', disabled=False)
        self.rot_box = VBox([Label('Rotate'), self.rot_axis, self.rot_mag])

        self.preview_btn = Button(description='Preview', disabled=False, button_style='')
        self.apply_btn = Button(description='Apply', disabled=False, button_style='')
        self.btn_box = VBox([self.preview_btn, self.apply_btn])

        self.grid = HBox([self.trans_box, self.rot_box, self.btn_box])

class ToolTab:

    def __init__(self,parent):

        self.parent = parent
        self.toggle_vis_btn = Button(description='Toggle-Vis')
        self.toggle_vis_btn.on_click(self.toggle_vis)

        self.grid = self.toggle_vis_btn

    def toggle_vis(self, b):

        for node in self.parent.parent.csys.tree.selected_nodes:
            if node.selected:
                node.toggle_vis()
            else:
                self.walk_subtree(node)
    
    def walk_subtree(self, node):
        
        for node in node.nodes:
            if node.selected:
                node.toggle_vis()
            elif hasattr(node, 'nodes'):
                self.walk_subtree(node)         

class Ribbon:
    #_____________________________
    #|_File_|_View_|_Move_|_Tools_|

    def __init__(self, parent):
        self.parent = parent
        self.file_tab = FileTab(self)
        self.view_tab = ViewTab(self)
        self.move_tab = MoveTab(self)
        self.tool_tab = ToolTab(self)

        self.tabs = Tab()
        self.tabs.children = [self.file_tab.grid, self.view_tab.grid, self.move_tab.grid, self.tool_tab.grid]
        for i, name in enumerate(['File','View','Move','Tools']):
            self.tabs.set_title(i, name)

class Application:

    #__________________________
    #|_________Ribbon_________|
    #|                        |
    #|        CSYS            |
    #|                        |
    #|________________________|

    def __init__(self):
        self.ribbon = Ribbon(self)
        self.csys = CSYS()

        self.grid = VBox([self.ribbon.tabs, self.csys.plot()])