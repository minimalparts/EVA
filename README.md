# IdealWords


This repo will contain code to generate mini-worlds and simulate some speakers
experiencing a number of situations in those worlds, and talking about them.

This is work in progress! Current project status is to be found below.

### Current status

A number of tests are implemented in the test folder. More are coming.

* *denotation.py* is a sanity check: creates a world, and checks whether the denotation function works by picking out all entities corresponding to a particular predicate *P*.

* *generate.py* tests the generation function. For a particular grammar (composition rules and vocabulary), generate all possible sentences for that grammar. Then, according to a generated world, pick those sentences that are True.

* *gods_refer.py* tests the alignment between two omniscient speakers (and the same grammar). Vishnu utters things that are true according to his model of the world (i.e. a subset of the sentences he could generate -- see *generate.py*. Artemis evaluates the truth of Vishnu's sentences and a) finds them all true; b) returns the non-empty set that makes the sentence true.

* *humans_refer.py* tests the alignment between two speakers who have experienced different parts of the world (represented as two different models). This shows that without extra inference, reference fails for some sentences that speaker *S1* holds true, but do not correspond to anything in *S2*'s model.
