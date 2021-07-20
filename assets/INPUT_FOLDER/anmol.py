#!/usr/bin/env python

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
import numpy as np
import pandas as pd

stop_words = set(stopwords.words("english"))
stemmer = SnowballStemmer("english")  # PorterStemmer()
lemmatizer = WordNetLemmatizer()
tokenizer = nltk.RegexpTokenizer(r"\w+")


def remove_num_abb(wrd):
    """Checks that the word is a numeric or shorter than 3 characters

    :wrd: string
    :returns: Boolean

    """
    # TODO: Remove any value which has a number

    if len(wrd) < 3 or '_' in wrd:
        return True

    for char in wrd:
        try:
            int(char)
            return True
        except ValueError:
            continue
    return False


def keywords(text):
    """Return keywords after removing list of not required words."""
    text = text.replace("*", "").replace("\n", " ")
    words = [word for word in [stemmer.stem(word.lower()) for word in tokenizer.tokenize(
        text) if word.casefold() not in stop_words] if not remove_num_abb(word)]
    return words


def summariser(merged_text):
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
