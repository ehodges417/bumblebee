import setuptools

setuptools.setup(
    name="bumblebee",
    version="0.0.1",
    author="Elijah Hodges",
    description="A robotics plotting and development library",
    packages=['bumblebee'],
    python_requires='>=3.6',
    install_requires=[
        'modern_robotics',
        'numpy',
        'numpy-stl',
        'pint',
        'plotly',
        'scipy',
    ],
    extras_require = {
        'tutorials':  ["jupyter"]
    }
)