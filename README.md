# Ideal Words

This repo computes truth-theoretic semantic spaces as described in the paper 'Ideal Words'.

## Installation

First, you should download and unzip the file [http://clic.cimec.unitn.it/~aurelie.herbelot/ideallanguage.zip](http://clic.cimec.unitn.it/~aurelie.herbelot/ideallanguage.zip) (38M zipped) to your data/ directory. This file contains a representation of the [Visual Genome](http://visualgenome.org/) entities, attributes and relationships which we will use to produce a basic entity matrix. Should you want to re-generate this data, you can do so using the script in *utils/parse.py* (you will need the original Visual Genome json files -- see code for detail).

Gather all the stats we'll need for building the matrices:

    python3 utils/stats.py


## Generate the semantic spaces

The following matrices will be produced: entity matrix, predicate matrix, probabilistic version of the predicate matrix. Run:

    python3 extraction-aggregation.py

All space files will be stored in the *spaces/* directory. Formats are as follows:

**The entity matrix**

Each relation / attribute is shown, followed by the IDs of the entities that instantiate it. E.g.

    has(-,jersey.n.03) 145052 145052 145052 ...
    on(ice.n.01,-) 1564869 1564872 1073295 ...
    in(-,mouth.n.01) 1066577 1571546 1580146 ...
    on(visor.n.01,-) 1574593 1589180 307104 ...
    on|top|of(-,food.n.01) 148294 337935 1113534 ...
    on|top|of(sunglasses.n.01,-) 1580964 358974 1618779 ...
    of(-,bathroom.n.01) 1543891 1546177 1075545 ...
    has(ring.n.02,-) 156638 156638 156638 ...


**Inverse entity matrix**

For each entity, the predicates applicable to that entity are shown. E.g.

    2258167 land.n.04
    519773 chest_of_drawers.n.01 next|to(bag.n.01,-)
    3265447 sweatshirt.n.01 white with(-,band.n.04)
    175702 person.n.01
    3506270 window.n.01 on|a(-,building.n.01)
    943446 people.n.01 on(-,land.n.04) in(-,plaza.n.02)
    2931124 man.n.01
    3132144 hand.n.01 of(-,guy.n.01)



## Generate standard similarity measures

To obtain standard similarity and nearest neighbours information on the created space, do:

    python3 similarity.py

Warning: the pairwise cosine computation takes a little while. All similarity files will be stored in the *data/* directory.


## Test the spaces

To run an example of polysemy clustering, do:

    python3 polysemy-clustering.py bear 5
