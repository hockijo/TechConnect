.. TechConnect documentation master file, created by
   sphinx-quickstart on Fri Jul 21 16:44:26 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TechConnect!
=======================

Introduction
------------
This is a python library written to help control instruments over VISA/GPIB. Below you will find Installation instructions. Please keep in mind that this package is still in heavy development and there may be large refactoring/changes that could break code. I will try to maintain up-to-date documentation.
However, if you see a bug, or any missed/out-of-date documentation please feel free to contact me at
joseph.hocking@uwa.edu.au
   
Installation 
------------
Due to the dev state of this package, currently the preferred method of installation is github cloning, and installation through pip. To do this first clone the github repo by:
```
git clone https://github.com/hockijo/TechConnect
```
Then navigate to the cloned directory in your preferred prompt for installing python packages(should be called TechConnect) and run the following:
```
pip install .
```

API
===
.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   source/_instrument
   source/oscilloscope
   source/signal_generators
   source/examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`