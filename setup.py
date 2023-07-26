'''
Setup for my_package that describes it's contents and how to install it.
'''
from setuptools import setup, find_packages

# List of dependencies for the package
# >= Can be used to specify a minimum version
# >=,< Can be used to specify a minimum and maximum version e.g. 'numpy>=1.15,<1.20',
dependencies = [
        'numpy',
        'scipy',
        'pyvisa',
        'matplotlib',
]

setup(
    # Name of the repository
    name='TechConnect',
    # Version of the software (keep this up to date with git tags/releases)
    version='0.0.1',
    # Short description of the package
    description='...',
    # Update this with your github URL
    url='https://github.com/hockijo/TechConnect',
    # Minimum version of python required
    python_requires='>=3.6',
    # Name of your package, should be the same as the name of the directory
    packages=['techconnect'],
    # Any data files that need to be included with the package (non python files)
    # package_data={'TechConnect':['data/*.csv']},
    # Dependencies for the package
    install_requires=dependencies,
    # Scripts that will be run on the command line
    #entry_points={
    #    'console_scripts': [
    #        # Make a hello_world command that runs the main function in hello_world.py script located in my_package/scripts
    #       'hello_world=my_package.scripts.hello_world:main',
    #    ],
    #},
)