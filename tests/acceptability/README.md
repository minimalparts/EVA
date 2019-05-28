## Acceptability judgments

### The data

The Karma Police file is extracted from the data associated with the following paper:


Guenther, F., and Marelli, M. (2016). *[Understanding Karma Police: The Perceived Plausibility of Noun Compounds as Predicted by Distributional Models of Semantic Representation](http://www.marcomarelli.net/goog_854812211)*. PloS one, 11(10).

Full data available at [https://figshare.com/articles/KarmaPolice_zip/3824148](https://figshare.com/articles/KarmaPolice_zip/3824148).


### Vectors from FastText and BERT

For convenience, we include vectors for all single words in the Karma Police dataset, as extracted from the pre-trained [FastText](https://fasttext.cc/docs/en/english-vectors.html) system, and from [BERT BASE](https://github.com/huggingface/pytorch-pretrained-BERT). The BERT vectors were obtained by summing the last four hidden layers for the input word in the encoding stack. Vectors are contained in the *data/models/* directory.


### How to train the system(s)

We release pretrained models for all three systems in the *checkpoints/pretrained* directory. If you want to perform your own optimisation and / or reproduce the pipeline from the paper, you can use the following scripts:

* optimise_nn_acceptability.py: runs Bayesian optimisation for the hyperparameter ranges provided in the script. Results are stored in a json file, e.g. *eva.optimisation_logs.r1.json*. 
* read_logs.py: reads the optimisation json file and returns the 20 best hyperparameter sets.
* nn_acceptability.py: runs training directly. Use with the best hyperparameter sets you found in the previous step.
* nn_acceptability_test.py: runs best stored model on test set. 
