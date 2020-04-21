# Ideal Words

This repo computes truth-theoretic semantic spaces as described in the draft paper *'Ideal Words: a vector-based formalisation of semantic competence'* (Herbelot and Copestake, in prep).

## Installation

First, you should download and unzip the file [http://aurelieherbelot.net/resources/data/ideallanguage.zip](http://aurelieherbelot.net/resources/data/ideallanguage.zip) (38M zipped) to your data/ directory. This file contains a representation of the [Visual Genome](http://visualgenome.org/) entities, attributes and relationships which we will use to produce a basic entity matrix. Should you want to re-generate this data, you can do so using the script in *utils/parse.py* (you will need the original Visual Genome json files -- see code for detail).

Gather all the stats we'll need for building the matrices:

    cd utils; python3 stats.py


## Generate the semantic spaces

The following matrices will be produced: entity matrix, predicate matrix, probabilistic version of the predicate matrix. Run:

    python3 extract.py [--att] [--rel] [--sit]

The flags are optional and process relations, attributes and situations in the Visual Genome, in addition to objects. Spaces are produced for the raw cooccurrence matrix, as well as its probabilistic version. In addition, PPMI and PCA-reduced versions are generated. If you're getting started, the combination of *--att* and *--rel* should give you a fairly rounded model.

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


## Run Ext2Vec

The ext2vec model is an 'extensional' version of the famous Word2Vec model. It produces vectors at reduced dimensionality from a raw (extensional) co-occurrence matrix. In a nutshell, *ext2vec* re-uses the 'context prediction' task of the original skip-gram model, but porting it to a formal semantics setting. Specifically, the task consists in predicting whether a 'target' predicate (from the rows of the predicate matrix) and a 'context' predicate (from the columns of the matrix) have been seen together in the description of a unique, grounded entity. 

Run *ext2vec* with:

    python3 embed_model.py [--att] [--rel] [--sit]

(where the flags should be the same as those you used earlier with the *extract.py* script).

This will run on the *predicate_matrix.dm* file contained in the relevant folder of your data/ directory.





## Evaluate spaces on MEN and SimLex-999

Spaces can be evaluated on the standard relatedness and similarity test sets MEN and SimLex-999. To do so, go to *tests/MEN* or *tests/SimLex*. Evaluation can be performed on count spaces (with or without PPMI and PCA), on the output space of ext2vec, or on external vectors for comparison. For instance:

    python3 spearman.py ext2vec --att --rel

It is possible to choose the space that is evaluated by using the flags *--att* and *--rel* (to include attribute and relations dimensions). Adding the flag *--ppmi* will run on the PPMI version of the predicate matrix, similarly with the *--pca* flag. So for example:

    python3 spearman.py count --rel --ppmi --pca

would run on a count space with relation dimensions, with PPMI weighting and PCA.

To run a comparison with FastText VG:

    python3 spearman.py compare --file=data/MEN_fasttext_vg_desc_vecs.txt

(The data folder also contains the pretrained FastText and BERT vectors, issued from large corpora.)




## Generate standard similarity measures

To obtain standard similarity and nearest neighbours information on the created space, do:

    python3 similarity.py

Warning: the pairwise cosine computation takes a little while. All similarity files will be stored in the *data/* directory.



## Play with the spaces

The spaces can be inspected from the point of view of various aspects of semantic competence: a) the ability to refer; b) mastery of lexical relations; c) the ability to make graded semantic acceptability judgements with respect to 'normal use'. All code for this is to be found in the *tests* directory, under the re


### Reference

Run from the *truth* directory. To retrieve the extension of a particular constituent in the Visual Genome, run the following (with the appropriate flag):

    python3 composition.py --att

and input a phrase, e.g. *black teddy bear*.

NB: the code involves a toy grammar linked to an interpretation function, and performs semantic space expansion / retraction as explained in the paper. For now, the grammar only implements bare NPs with adjectives and nouns (of any length). So in practice, you should run with the --att flag.


### Lexical relations

Run from the *lexrel* and *incompatibility* directories.

First, prepare the data in the relevant data/ directory by running *preprocess.py*. Then, to train, do for instance:

    python3 nn_lexrel.py --batch=700 --epochs=400 --hidden=300 --lr=0.001 --wdecay=0.001 --ext=data/models/lexrel_fasttext_vecs.txt --checkpoint=checkpoints/fasttext/check1


### Acceptability judgements

Run from the *acceptability* directory.

First, prepare the data in the *data/* directory by running *preprocess.py*. Then, to train:

    python3 nn_acceptability.py

