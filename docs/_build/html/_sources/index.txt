.. IdealWords documentation master file, created by
   sphinx-quickstart on Mon May  1 14:34:25 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for the Ideal Words project
=========================================

This is a simulation of a toy animal world, and of the interaction of two
speakers about this world. Run with

python ./mk_world.py

The program will:

* create a world

* create situations in that world

* sample situations that speaker S1 has experienced

* make speaker S1 utter some simple sentences  about those situations

* make speaker S2 listen

* make speaker S2 perform a mapping between things they have heard and things they know, as expressed in vector form.

WARNING: at this time (May 1st, 2017), the mapping (linear regression) is bugged!



Contents:

.. toctree::
   :maxdepth: 2

   speaker
   world
   distributional_semantics


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

