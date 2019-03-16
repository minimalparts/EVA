# Ideal Words

This repo computes truth-theoretic semantic spaces as described in the draft paper *'Ideal Words: a vector-based formalisation of semantic competence'* (Herbelot and Copestake, in prep).

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


## Play with the spaces

The spaces can be inspected from the point of view of various aspects of semantic competence: a) the ability to refer; b) mastery of lexical relations; c) the ability to make graded semantic acceptability judgements with respect to 'normal use'. All code for this is to be found in the *tests* directory, under the re


### Reference

Run from the *truth* directory. To retrieve the extension of a particular constituent in the Visual Genome, run:

    python3 composition.py

and input a phrase, e.g. *black teddy bear*.

NB: the code involves a toy grammar linked to an interpretation function, and performs semantic space expansion / retraction as explained in the paper. For now, the grammar only implements bare NPs with adjectives and nouns (of any length).


### Lexical relations

Run from the *lexsel* directory. To retrieve antonyms from the Visual Genome, do:

    python3 antonymy.py


To run an example of polysemy clustering, do:

    python3 polysemy-clustering.py bear 5


### Acceptability judgements

Run from the *acceptability* directory. This code requires a nearest neighbours file which can be computed from the top directory using *similarity.py* (see instructions above). Run:

    python3 acceptability.py

You can either enter a phrase yourself (e.g. *red flying cookie*) or press 'r' to get a randomly generated one. The system will return an acceptability judgement for the phrase. When you quit (typing 'q'), all inputs will be returned in order of acceptability. 

NB: this code is not integrated with the grammar, so you can type anything in any order...
