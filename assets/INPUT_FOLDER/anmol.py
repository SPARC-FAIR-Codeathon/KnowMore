#!/usr/bin/env python

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.cluster.util import cosine_distance
import networkx as nx
import nltk
import numpy as np
import pandas as pd

import scispacy
import spacy

# NOTE: To install the library
# TODO: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_md-0.4.0.tar.gz

nlp = spacy.load("en_core_sci_md")


stop_words = set(stopwords.words("english"))
stemmer = SnowballStemmer("english")  # PorterStemmer()
lemmatizer = WordNetLemmatizer()
tokenizer = nltk.RegexpTokenizer(r"\w+")


# def remove_num_abb(wrd):
# """Checks that the word is a numeric or shorter than 3 characters

# :wrd: string
# :returns: Boolean

# """
# # TODO: Remove any value which has a number

# if len(wrd) < 3 or '_' in wrd:
# return True

# for char in wrd:
# try:
# int(char)
# return True
# except ValueError:
# continue
# return False


def keywords(text):
    """Return keywords after removing list of not required words."""

    # text = text.replace("*", "").replace("\n", " ")
    # words = [word for word in [stemmer.stem(word.lower()) for word in tokenizer.tokenize(
    # text) if word.casefold() not in stop_words] if not remove_num_abb(word)]
    words = nlp(text).ents
    return words


def NestedDictValues(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from NestedDictValues(v)
        else:
            yield v


# summariser

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(
                sentences[idx1], sentences[idx2], stop_words)
    return similarity_matrix


def summariser(merged_text, top_n=5):
    sentences = sent_tokenize(merged_text)
    stop_words = stopwords.words('english')
    summarize_text = []

    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    ranked_sentence = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    # print("Indexes of top ranked_sentence order are ", ranked_sentence)

    for i in range(top_n):
        summarize_text.append(ranked_sentence[i][1])

    return ". ".join(summarize_text)


def summariser2(merged_text):
    # TODO: Compare sentences and remove duplicates as text are from multiple ids
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(merged_text)
    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word not in freqTable:
            freqTable[word] = 0
        freqTable[word] += 1

    sentences = sent_tokenize(merged_text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence not in sentenceValue:
                    sentenceValue[sentence] = freq
                else:
                    sentenceValue[sentence] += freq

    sumValues = sum(sentenceValue.values())
    average = int(sumValues/len(sentenceValue))
    summary = ""
    for sentence in sentences:
        try:
            if sentenceValue[sentence] > 1.2 * average:
                summary += " "+sentence
        except KeyError:
            continue
    return summary


# summariser2(open("test.txt").read())

# txt = """In an attempt to build an AI-ready workforce, Microsoft announced Intelligent Cloud Hub which has been launched to em>

# print(summariser(txt))


# for key in bhavesh:
# description = {}
# # NOTE: Ingnoring 'protocols link' information for now as I didn't find anything useful there.
# for val in [info for info in bhavesh[key]["description"].replace("*", "").split("\n") if ":" in info]:
# k_list = val.split(":", 1)
# description[k_list[0]] = [word for word in [lemmatizer.lemmatize(word.lower()) for word in tokenizer.tokenize(
# k_list[1].strip()) if word.casefold() not in stop_words] if not remove_num_abb(word)]
# bhavesh[key] = description

# all_fields = set()
# for key in bhavesh:
# all_fields |= set(bhavesh[key].keys())

# fields_df_relatedness = {}
# for field in all_fields:
# fields_df_relatedness[field] = {"start": [], "end": [], "similarity": []}
# for key1 in bhavesh:
# for key2 in bhavesh:
# fields_df_relatedness[field]["start"].append(key1)
# fields_df_relatedness[field]["end"].append(key1)
# if field in bhavesh[key1] and field in bhavesh[key2]:
# sim = len(set(bhavesh[key1][field]) & set(
# bhavesh[key2][field]))*1./len(set(bhavesh[key1][field]) | set(bhavesh[key2][field]))
# fields_df_relatedness[field]["similarity"].append(sim)
# pass
# else:
# fields_df_relatedness[field]["similarity"].append(np.nan)


# print(fields_df_relatedness)
