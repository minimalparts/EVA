.. IdealWords documentation master file, created by
   sphinx-quickstart on Mon May  1 14:34:25 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for the Ideal Words project
=========================================

Run with

`python ./mk_world.py [test_species]`

For instance:

`python ./mk_world.py cobra`

The test species is a species that the hearer has only 'heard' about, but never seen.

The program will:

*    create a world

*    create situations in that world

*    sample situations that speaker S1 has experienced

*    make speaker S1 utter some simple sentences about those situations

*    make speaker S2 listen

*    make speaker S2 perform a mapping between things they have heard and things they know, as expressed in vector form.

*    make speaker S2 infer things about the test species.





Contents:

.. toctree::
   :maxdepth: 2

   model
   grammar
   speaker
   world
   distributional_semantics


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

