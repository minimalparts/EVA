## Utils for EVA

### Extract BERT vectors for comparison with EVA

We use the extract_features.py script provided by [HuggingFace](https://github.com/huggingface/pytorch-pretrained-BERT/). Run the script to extract the word features you require. For instance, the following would extract the word embeddings for all unique words in the MEN dataset:

    python3 extract_features.py --input_file ../tests/MEN/unique_MEN_words.txt --output_file ../tests/MEN/MEN_bert_out.json --bert_model bert-base-uncased

This will create a json file containing the embedding of each word at each encoder level of BERT (so, 12 different embeddings for BERT base). This file needs to be parse, which can be done using parse_bert_json.py, which returns a sum of [CLS] layers in the BERT output. For instance:

    python3 parse_bert_json.py ../tests/MEN/MEN_bert_out.json --layer=4 > ../tests/MEN/MEN_bert_4l.txt

would return an embeddings file where each word is expressed as the sum of the last 4 hidden layers for the [CLS] token in BERT.
