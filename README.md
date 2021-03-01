# Bumblebee

## What is Bumblebee?

In many applications, CAD packages like Inventor, SolidWorks, and NX do a great job in assisting the design of 3D rigid bodies with a wide range of polished GUI tools. However, once the geometry is designed, it is often difficult, if not impossible, to validate kinematics of the system within a CAD program due to the constrains of GUI tools. Many turn to coding languages like Matlab or Python, only to have to rebuild the system from the ground up in a series of matricies with little to no visual assistance and many custom graphs.

Bumblebee is a package designed to assist in developing kinematic simulations by providing a common framework for building robotic systems in code. For easy tinkering and documentation it is designed around use in the iPython (Jupyter) environment. Interactive plots allowing zoom and 3D rotation are made possible with plotly and numpy-stl, while backend calculations based on numpy and numba keep the library fast.

## Install

This package is not currently registered with PyPi. To install it use the command

```
pip install git+https://github.com/ehodges417/bumblebee.git
```

## Getting Started

It is our goal to host the documentation on an online notebook service like Binder. However, while in development, interactive documentation can be found in the `tutorials` folder. Simply clone the repository and install the package, and then begin using the notebooks to learn!