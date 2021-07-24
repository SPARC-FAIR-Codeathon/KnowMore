from PIL import Image
import os
import re
import io
import seaborn as sns
import numpy as np
import pandas as pd
import json
import requests
import matplotlib
import shutil
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.cluster.util import cosine_distance
import networkx as nx
import spacy
import xlsxwriter

# NOTE: To install the library
# TODO: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_md-0.4.0.tar.gz
matplotlib.use('Agg')


# define parameters depending on if you are running the code
# on osparc or locally
if "INPUT_FOLDER" in os.environ:
    # In o²S²PARC, INPUT_FOLDER and OUTPUT_FOLDER are environment variables
    # that map to the service input/output ports, respectively
    input_dir = os.environ["INPUT_FOLDER"]
    output_dir = os.environ["OUTPUT_FOLDER"]
else:
    # local input/output folders
    current_folder = os.getcwd()
    input_dir = os.path.join(current_folder, 'tmp',
                             'fake-uuid-for-sample-data', 'INPUT_FOLDER')
    output_dir = os.path.join(current_folder, 'tmp',
                              'fake-uuid-for-sample-data', 'OUTPUT_FOLDER')
matlab_input_folder_name = 'matlab-input-folder'
matlab_input_save_folder = os.path.join(output_dir, matlab_input_folder_name)

#helper functions



nlp = spacy.load("en_core_sci_md")
stop_words = set(stopwords.words("english"))
stemmer = SnowballStemmer("english")  # PorterStemmer()
lemmatizer = WordNetLemmatizer()
tokenizer = nltk.RegexpTokenizer(r"\w+")

def keywords_finder(text):
    """Return keywords after removing list of not required words."""
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

    return " ".join(summarize_text)


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

# functions to get dataset from various sparc ressources
def get_dataset_latest_version(datasetId):
    url = "https://api.pennsieve.io/discover/datasets/" + datasetId
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers)
    response_json = json.loads(response.text)
    versionId = str(response_json['version'])
    return versionId


def get_dataset_file_response(datasetId, filepath):
    versionId = get_dataset_latest_version(datasetId)

    url = "https://api.pennsieve.io/zipit/discover"

    payload = {"data": {
        "paths": [filepath],
        "datasetId": datasetId,
        "version": versionId
    }}
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)
    return response


def get_dataset_file_download(datasetId, filepath):
    versionId = get_dataset_latest_version(datasetId)

    url = "https://api.pennsieve.io/zipit/discover"

    payload = {"data": {
        "paths": [filepath],
        "datasetId": datasetId,
        "version": versionId
    }}
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)
    return response

def get_dataset_description_text(datasetId):
    filepath = "readme.md"
    response = get_dataset_file_response(datasetId, filepath)
    if response.status_code == 200:
        description = response.text
        # remove section titles that are common to all datasets
        description_cleaned = re.sub("[**].*[**]", "", description)
        # remove markdown go to line
        description_cleaned = description_cleaned.replace('\n', '')
        return description_cleaned
    else:
        return 'Error'


def get_dataset_protocolsio_link(datasetId):
    url = "https://api.pennsieve.io/discover/search/records"
    querystring = {"limit": "10", "offset": "0",
                   "model": "protocol", "datasetId": datasetId}
    headers = {"Accept": "application/json"}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    json_protocol = json.loads(response.text)
    protocol_url = json_protocol['records'][0]['properties']['url']
    return protocol_url


def get_protocolsio_text(datasetId):
    data_protocol = {}
    protocol_url = get_dataset_protocolsio_link(datasetId)
    doi = protocol_url.rsplit('/', 1)[-1]

    url = "https://www.protocols.io/api/v3/protocols/" + str(doi)
    querystring = {
        "Authorization": "76d6ca8285076f48fe611091fd97eab4bc1c65051da75d7dc70ce746bd64dbe6"}
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json"
    }
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    protocol_json = json.loads(response.content)
    protocol_title = protocol_json["protocol"]['title']
    data_protocol['title'] = protocol_title
    protocol_description = protocol_json["protocol"]['description']
    cleanr = re.compile('<.*?>')
    protocol_description_clean = re.sub(cleanr, '', protocol_description)
    data_protocol['description'] = protocol_description_clean
    steps_text = ""
    for step in protocol_json["protocol"]["steps"]:
        for item in step['components']:
            if item['type_id'] == 1:
                step_description = item['source']['description']
                step_description_cleaned = re.sub(cleanr, '', step_description)
                steps_text = steps_text + " " + step_description_cleaned
    data_protocol['steps'] = steps_text

    return data_protocol


def get_dataset_main_manifest(datasetId):
    # this manifest contains a list of all the files in the dataset
    # and their paths
    filepath = 'manifest.json'
    response = get_dataset_file_response(datasetId, filepath)

    return json.loads(response.content)


def get_dataset_text_files(datasetId):
    datafile_text = {}
    manifest_json = get_dataset_main_manifest(datasetId)
    for file_info in manifest_json['files']:
        if file_info['fileType'] == 'Text':
            filepath = file_info['path']
            if 'license' not in filepath and 'LICENSE' not in filepath:
                response = get_dataset_file_response(datasetId, filepath)
                file_text = response.text
                file_text = file_text.replace('\r', '')
                file_text = file_text.replace('\n', '')
                datafile_text[filepath] = file_text
    return datafile_text


def get_dataset_mat_files(datasetId):
    datafile_mat = {}
    manifest_json = get_dataset_main_manifest(datasetId)
    for file_info in manifest_json['files']:
        if file_info['fileType'] == 'MAT':
            filepath = file_info['path']
            if 'derivative' in filepath:
                response = get_dataset_file_response(datasetId, filepath)
                datafile_mat[filepath] = response
    return datafile_mat


def get_image_files(datasetId):
    datafile_image = {}
    manifest_json = get_dataset_main_manifest(datasetId)
    for file_info in manifest_json['files']:
        if file_info['fileType'] == 'TIFF':
            try:
                filepath = file_info['path']
                response = get_dataset_file_response(datasetId, filepath)
                # Create an in-memory stream of the content
                sio = io.BytesIO(response.content)
                img = Image.open(sio)
                image_name = str(datasetId) + "-" + \
                    str(os.path.basename(filepath))
                # img.save(image_name)
                datafile_image[filepath] = img
            except:
                print("NOT SAVED")
                pass
    return datafile_image

def get_image_files_biolucida(datasetId):
    url = "https://sparc.biolucida.net/api/v1/imagemap/search_dataset/discover/" + datasetId
    payload={}
    headers = {
      'token': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    datafile_image = json.loads(response.text)
    return datafile_image
    
def get_images_all_datasets(list_datasetId):
    for datasetId in list_datasetId:
        datafile_image = get_image_files_biolucida(datasetId)
        for item in datafile_image["dataset_images"]:
            print(item)
            image_link = item["share_link"]
            print(image_link)
            url = image_link
            
            payload={}
            headers = {
              'token': ''
            }
            
            response = requests.request("GET", url, headers=headers, data=payload)
            #print(response.text)
    return datafile_image
                    
# data processing
def get_knowledge_graph_data(datasetId):
    # get species information from subjects file
    # get specimen type and specimen anatomical location from samples.xlsx
    data_knowledge_graph = {}
    filepath = "files/subjects.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine='openpyxl')
    df.dropna(axis=0, how='all', inplace=True)
    data_knowledge_graph['Species'] = df['species'].values[0]

    filepath = "files/samples.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine='openpyxl')
    df.dropna(axis=0, how='all', inplace=True)
    #specimen_type = list(set(df['specimen type'].values.tolist()))

    data_knowledge_graph['Specimen type'] = df['specimen type'].values[0]
    return data_knowledge_graph


def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect."""
    def convert(text): return int(text) if text.isdigit() else text
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def get_summary_table_data(datasetId):
    # manifest.json: get dataset title, subtitle, publication date
    # subjects.xlsx: species, n subjects, age range, sex
    # samples.xlsx: n samples, specimen type, specimen anatomical location
    data_table_summary = {}
    manifest_json = get_dataset_main_manifest(datasetId)
    data_table_summary['Dataset id'] = datasetId
    data_table_summary['Title'] = manifest_json['name']
    data_table_summary['Subtitle'] = manifest_json['description']
    data_table_summary['Publication_date'] = manifest_json['datePublished']

    filepath = "files/subjects.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine='openpyxl')
    df.dropna(axis=0, how='all', inplace=True)
    data_table_summary['Number of subjects'] = len(df)
    data_table_summary['Species'] = df['species'].values[0]
    age_values = list(set(df['age'].values.tolist()))
    if len(age_values) > 1:
        age_values = sorted_nicely(age_values)
        age_range = age_values[0] + " - " + age_values[-1]
        data_table_summary['Age'] = age_range
    else:
        data_table_summary['Age'] = str(age_values[0])

    sex_values = list(set(df['sex'].values.tolist()))
    data_table_summary['Sex'] = sex_values

    filepath = "files/samples.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine='openpyxl')
    df.dropna(axis=0, how='all', inplace=True)
    data_table_summary['Number of samples'] = len(df)
    data_table_summary['Speciment type'] = df['specimen type'].values[0]
    anatomical_location_values = list(
        set(df['specimen anatomical location'].values.tolist()))
    data_table_summary['Anatomical location(s)'] = anatomical_location_values

    return data_table_summary


def get_all_datasets_text(list_datasetId):
    # get text from each dataset

    # text for each dataset is obtained from the dataset description,
    # protocol, and any text files in the datasets
    data_text = {}
    for datasetId in list_datasetId:
        data_text[datasetId] = {}
        # text from dataset description
        data_text[datasetId]['description'] = get_dataset_description_text(
            datasetId)
        # text from protocol all nice and clean, includes title, description
        # and protocol steps
        data_text[datasetId]['protocol'] = get_protocolsio_text(datasetId)
        # text from any txt file in the dataset except license files
        data_text[datasetId]['text files'] = get_dataset_text_files(datasetId)
    return data_text


def get_keywords(data_text):
    # clean up text (remove stopwords etc.)
    top_words = 20
    index = []
    all_keyword_df = []
    for datasetId in data_text:
        index.append(datasetId)
        text = " ".join(list(NestedDictValues(data_text[datasetId])))

        # data_text[datasetId]["description"] + \
        # " ".join(data_text[datasetId]["protocol"].values())
        text = text.replace("*", "").replace("\n", " ")
        words = [str(word) for word in keywords_finder(text)]
        # Cleaning
        keywords_json = {}
        # print(words)

        for word in set(words):
            if word not in keywords_json:
                keywords_json[word] = [0]
            for word2 in words:
                if word in word2:
                    keywords_json[word][0] += 1  # [text.count(word)]

        all_keyword_df.append(pd.DataFrame(keywords_json))
    all_keyword_df = pd.concat(all_keyword_df).fillna(0)
    all_keyword_df.index = index
    all_keyword_df = all_keyword_df.T
    all_keyword_df["min_in_sample"] = all_keyword_df.apply(
        lambda x: np.min(x.values), axis=1)
    all_keyword_df = all_keyword_df.sort_values(
        "min_in_sample", ascending=False).head(top_words)
    # print(all_keyword_df.to_json())
    return all_keyword_df['min_in_sample'].to_dict()  # .to_json()

def get_abstract(data_text):
    # combine text from all datasets

    # run text summarizer for all the datasets combined
    # text_to_summarise = []
    # for datasetId in data_text:
    # text_to_summarise.append(data_text[datasetId]["description"])
    # text_to_summarise = " ".join(text_to_summarise)

    text_to_summarise = " ".join(list(NestedDictValues(data_text)))
    abstract = summariser(text_to_summarise, top_n=10)

    # abstract = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    return abstract


def get_text_correlation(data_text):

    # clean up text (remove stopwords etc.)

    # run text correlation calculator

    # save json + PNG
    index = []
    all_keyword_df = []
    for datasetId in data_text:
        index.append(datasetId)
        text = " ".join(list(NestedDictValues(data_text[datasetId])))

        # data_text[datasetId]["description"] + \
        # " ".join(data_text[datasetId]["protocol"].values())
        text = text.replace("*", "").replace("\n", " ")
        words = [str(word) for word in keywords_finder(text)]
        # Cleaning
        keywords_json = {}
        # print(words)

        for word in set(words):
            if word not in keywords_json:
                keywords_json[word] = [0]
            for word2 in words:
                if word in word2:
                    keywords_json[word][0] += 1  # [text.count(word)]

        all_keyword_df.append(pd.DataFrame(keywords_json))
    all_keyword_df = pd.concat(all_keyword_df).fillna(0)
    all_keyword_df.index = index
    all_keyword_df = all_keyword_df.T
    all_keyword_df[all_keyword_df != 0] = 1
    df_len = len(all_keyword_df)
    cor_matrix = {"from dataset ID": [], "to dataset ID": [], "value": []}
    for c1 in all_keyword_df.columns:
        for c2 in all_keyword_df.columns:
            if c1 == c2:
                cor_matrix["from dataset ID"].append(c1)
                cor_matrix["to dataset ID"].append(c1)
                cor_matrix["value"].append(1)
            if c1 < c2:
                # tdata = all_keyword_df[~(
                # (all_keyword_df[c1] == 0) & (all_keyword_df[c2] == 0))]
                # value = len(tdata[tdata[c1] == tdata[c2]])/len(tdata)

                value = len(
                    all_keyword_df[all_keyword_df[c1] == all_keyword_df[c2]])*1./df_len
                cor_matrix["from dataset ID"].append(c1)
                cor_matrix["to dataset ID"].append(c2)
                cor_matrix["from dataset ID"].append(c2)
                cor_matrix["to dataset ID"].append(c1)
                cor_matrix["value"].append(value)
                cor_matrix["value"].append(value)
    cor_matrix = pd.DataFrame(cor_matrix)
    cor_matrix = cor_matrix.pivot(
        index="from dataset ID", columns="to dataset ID", values="value")
    
    plot = sns.heatmap(cor_matrix, cmap='coolwarm')
    fig = plot.get_figure()
    fig.savefig(os.path.join(output_dir, "Correlation_heatmap.png"))
    fig.savefig(os.path.join(output_dir, "Correlation_heatmap.svg"))
    fig.clf()

    return cor_matrix.to_json()

def get_all_datasets_mat_files(list_datasetId):
    if os.path.isdir(matlab_input_save_folder):
        #delete any existing output matlab folder
        shutil.rmtree(matlab_input_save_folder)
    os.makedirs(matlab_input_save_folder)  
    
    matlab_data_folder = os.path.join(matlab_input_save_folder, 'matlab_data')
    os.makedirs(matlab_data_folder) 
    df = pd.DataFrame()
    full_datasetId_list = []
    filepath_list = []
    for datasetId in list_datasetId:
        dataset_mat = get_dataset_mat_files(datasetId)
        if dataset_mat:
            datasetId_path = os.path.join(matlab_data_folder, str(datasetId))
            os.makedirs(datasetId_path)
            for filepath in dataset_mat.keys():
                #matlab-input.xlsx data
                full_datasetId_list.append(int(datasetId))
                ps_file_path = "/".join(filepath.strip("/").split('/')[1:])
                filepath_list.append(ps_file_path)
                
                #saving mat file
                mat_file_name = os.path.basename(ps_file_path)
                mat_file_folder = os.path.join(datasetId_path, 'derivative')
                if not os.path.isdir(mat_file_folder):
                    os.makedirs(mat_file_folder) 
                mat_file_path = os.path.join(mat_file_folder, mat_file_name)                
                response = dataset_mat[filepath]
                with open(mat_file_path, 'wb') as f:
                    f.write(response.content)
#                with open(mat_file_path, 'w', encoding="utf-8") as f:
#                    f.write(response.text)
    if len(full_datasetId_list)>0:
        df["datasetId"] = full_datasetId_list
        df["filepath"] = filepath_list
        matlab_excel_file = os.path.join(matlab_input_save_folder, 'matlab_input.xlsx')
        df.to_excel(matlab_excel_file, sheet_name='Sheet1', 
                    engine = 'xlsxwriter', index=False)
#        pd.read_csv(io.StringIO(df.to_csv(index=False)), header=None).to_excel(
#                matlab_excel_file, header=None, index=None)
        output_zip_folder = os.path.join(matlab_input_save_folder + ".zip")
        if os.path.exists(output_zip_folder):
            os.remove(output_zip_folder)
            
        shutil.make_archive(matlab_input_save_folder, 'zip', output_dir,
                            matlab_input_folder_name)
    return        
        
# Test
input_file = os.path.join(input_dir, 'input.json')
datasetIdsinput = json.load(open(input_file))
list_datasetId = datasetIdsinput['datasetIds']
list_datasetId = [str(x) for x in list_datasetId]
#list_datasetId = ['60']

# storage dict to be saved as a json and returned to front-end
dataset_data = {}

# knowledge graph data
dataset_data['knowledge_graph'] = {}
for datasetId in list_datasetId:
    dataset_data['knowledge_graph'][datasetId] = get_knowledge_graph_data(
            datasetId)

# summary table
dataset_data['summary table'] = {}
for datasetId in list_datasetId:
    dataset_data['summary table'][datasetId] = get_summary_table_data(
        datasetId)

# keywords
data_text = get_all_datasets_text(list_datasetId)
keywords = get_keywords(data_text)
dataset_data['keywords'] = keywords

# abstract
abstract = get_abstract(data_text)
dataset_data['abstract'] = abstract

# text correlation matrix
dataset_data['correlation_matrix'] = get_text_correlation(data_text)

# matlab_input files generator
get_all_datasets_mat_files(list_datasetId)

# save output
output_file = os.path.join(output_dir, 'output.json')
with open(output_file, 'w+') as f:
    json.dump(dataset_data, f, indent=4)
