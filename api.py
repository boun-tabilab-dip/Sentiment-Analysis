#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Cem Rıfkı Aydın
"""
import argparse
import os
import sys
import warnings

import constants
import pickle
import preprocessing
import svm
from flask import Flask, json, g, request, jsonify, json

warnings.filterwarnings("ignore")


def create_parser():
    """
    This function takes the inputs from terminal through the use of parser.

    :return: Argument parser. 
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="turkish", required=True,
                        choices=["english", "turkish"])
    parser.add_argument("--embedding_type", default="corpus_svd", required=True,
                        choices=["corpus_svd", "lexical_svd", "supervised",
                                 "ensemble", "clustering", "word2vec"],
                        help="The type of embedding")
    parser.add_argument("--embedding_size", type=int,
                        default=100,
                        help='The length of embeddings.')
    parser.add_argument("--cv_number", type=int, default=10,
                        help="The number of folds for cross-validation")
    parser.add_argument("--use_3_review_polarities", action='store_true',
                        default=True,
                        help='The Boolean value deciding whether three polarity scores'
                             'per review are used')
    parser.add_argument("--file_path", default=os.path.join("input", "Sentiment_dataset_turk.csv"),
                        help='The path to the sentiment file for cross-validation')
    parser.add_argument("--training_path", default=os.path.join("input", "Sentiment_dataset_turk.csv"),
                        help='The path to the training data file if the module '
                             '\"training and test files are provided\" is used')
    parser.add_argument("--test_path", default=os.path.join("input", "test_tr.csv"),
                        help='The path to the test data file if the module \"training'
                             ' and test files are provided\" is used')
    parser.add_argument("--model_path", default=constants.MODEL_FILE_NAME,
                        help='The path to the model trained. This should be used only when'
                             'all the essential parameter types or sizes given above must'
                             'be the same for both the training and test data. Otherwise, '
                             'this is going to produce an error')

    return parser

app = Flask(__name__)
    

@app.route("/evaluate", methods=["POST"])
def evaluate():
    json_data = json.loads(request.data)
    input_text = json_data["textarea"]
    line = input_text.strip("\n")
    line = pre.preprocess_one_line(line)
    sentiment = svm.test_model(model, sf, tr_vecs, imp, line)[0][0]
    sentiment = "Positive" if sentiment == "P" else "Negative"
    # print(sentiment)
    result = {"text": sentiment}
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":
    # Four example commands on the terminal would be as follows:
    # python3 runner.py --command cross_validate --language turkish --embedding_type corpus_svd --embedding_size 50 --file_path input/Sentiment_dataset_turk.csv
    # python3 runner.py --command predict --language turkish --embedding_type ensemble --file_path input/Sentiment_dataset_turk.csv
    # python3 runner.py --command train_and_test_separately --language turkish --embedding_type ensemble --embedding_size 200 --training_path input/Turkish_twitter_train.csv --test_path input/Turkish_twitter_test.csv
    # python3 runner.py --command cross_validate --language english --embedding_type supervised --file_path input/Sentiment_dataset_eng.csv
    parser_ = create_parser()
    args = parser_.parse_args()

    constants.LANG = args.language
    constants.EMBEDDING_TYPE = args.embedding_type
    constants.EMBEDDING_SIZE = args.embedding_size
    constants.CV_NUMBER = args.cv_number
    constants.USE_3_REV_POL_SCORES = args.use_3_review_polarities
    constants.DATASET_PATH = args.file_path

    constants.TRAINING_FILE = args.training_path
    constants.TEST_FILE = args.test_path

    constants.MODEL_FILE_NAME = args.model_path


    pre = preprocessing.Preprocessing()
    reviews, labels = pre.get_data(constants.DATASET_PATH)
    model, sf, tr_vecs, imp = svm.generate_model(reviews, labels)
    app.run(host='0.0.0.0')
    # main()
