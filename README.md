# Ideal Words

This repo computes truth-theoretic semantic spaces as described in the paper 'Ideal Words'.

## Installation

First, you should download and unzip the file [http://clic.cimec.unitn.it/~aurelie.herbelot/ideallanguage.zip](http://clic.cimec.unitn.it/~aurelie.herbelot/ideallanguage.zip) (38M zipped) to your data/ directory. This file contains a representation of the [Visual Genome](http://visualgenome.org/) entities, attributes and relationships which we will use to produce a basic entity matrix.

Gather all the stats we'll need for building the matrices:

    python3 preprocessing/stats.py


## Make the semantic spaces

The following matrices will be produced: entity matrix, predicate matrix, probabilistic version of the predicate matrix. Run:

    python3 mk_scottish_space.py 
