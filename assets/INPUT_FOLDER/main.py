import requests
import json
import pandas as pd
from scipy.io import loadmat
import io
import re
import os

## define parameters depending on if you are running the code 
## on osparc or locally
if "INPUT_FOLDER" in os.environ:
    #In o²S²PARC, INPUT_FOLDER and OUTPUT_FOLDER are environment variables 
    #that map to the service input/output ports, respectively
    input_dir = os.environ["INPUT_FOLDER"] 
    output_dir = os.environ["OUTPUT_FOLDER"]
else:
    #local input/output folders
    current_folder = os.getcwd()
    input_dir = os.path.join(current_folder, "INPUT_FOLDER")
    output_dir = os.path.join(current_folder, "OUTPUT_FOLDER")
    
## helper functions    
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


def get_dataset_description_text(datasetId):
    filepath = "readme.md"
    response = get_dataset_file_response(datasetId, filepath)
    if response.status_code == 200:
        description = response.text
        #remove section titles that are common to all datasets
        description_cleaned = re.sub("[**].*[**]", "", description)
        #remove markdown go to line
        description_cleaned = description_cleaned.replace('\n', '') 
        return description_cleaned
    else:
        return 'Error'


def get_dataset_protocolsio_link(datasetId):
    url = "https://api.pennsieve.io/discover/search/records"
    querystring = {"limit":"10","offset":"0","model":"protocol","datasetId":datasetId}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    json_protocol = json.loads(response.text)
    protocol_url = json_protocol['records'][0]['properties']['url']
    return protocol_url

def get_protocolsio_text(datasetId):
    data_protocol = {}
    protocol_url = get_dataset_protocolsio_link(datasetId)
    doi = protocol_url.rsplit('/', 1)[-1]
    
    url = "https://www.protocols.io/api/v3/protocols/" + str(doi)
    querystring = {"Authorization":"76d6ca8285076f48fe611091fd97eab4bc1c65051da75d7dc70ce746bd64dbe6"}
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
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
    #this manifest contains a list of all the files in the dataset
    #and their paths
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


def get_knowledge_graph_data(datasetId):
    #get species information from subjects file
    #get specimen type and specimen anatomical location from samples.xlsx
    data_knowledge_graph = {}
    filepath = "files/subjects.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine = 'openpyxl')
    df.dropna(axis = 0, how = 'all', inplace = True)
    data_knowledge_graph['Species'] = df['species'].values[0]
    
    filepath = "files/samples.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine = 'openpyxl')
    df.dropna(axis = 0, how = 'all', inplace = True)
    #specimen_type = list(set(df['specimen type'].values.tolist()))
    data_knowledge_graph['Specimen type']  = df['specimen type'].values[0]
    return data_knowledge_graph 
  
    
def get_summary_table_data(datasetId):
    #manifest.json: get dataset title, subtitle, publication date 
    #subjects.xlsx: species, n subjects, age range, sex
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
        df = pd.io.excel.read_excel(fh, engine = 'openpyxl')
    df.dropna(axis = 0, how = 'all', inplace = True)
    data_table_summary['Number of subjects'] = len(df)
    data_table_summary['Species'] = df['species'].values[0]
    age_values = list(set(df['age'].values.tolist()))
    
    data_table_summary['Age'] = age_values
    sex_values = list(set(df['sex'].values.tolist()))
    data_table_summary['Sex'] = sex_values
    
    filepath = "files/samples.xlsx"
    response = get_dataset_file_response(datasetId, filepath)
    with io.BytesIO(response.content) as fh:
        df = pd.io.excel.read_excel(fh, engine = 'openpyxl')
    df.dropna(axis = 0, how = 'all', inplace = True)
    data_table_summary['Number of samples'] = len(df)
    data_table_summary['Speciment type'] = df['specimen type'].values[0]
    anatomical_location_values = list(set(df['specimen anatomical location'].values.tolist()))
    data_table_summary['Anatomical location(s)'] = anatomical_location_values
    
    return  data_table_summary

def get_all_datasets_text(list_datasetId):
    #get text from each dataset
    
    # text for each dataset is obtained from the dataset description,
    # protocol, and any text files in the datasets
    data_text = {}
    for datasetId in list_datasetId:
        data_text[datasetId] = {}
        # text from dataset description
        data_text[datasetId]['description'] = get_dataset_description_text(datasetId)
        #text from protocol all nice and cleaned, includes title, description
        # and protocol steps
        data_text[datasetId]['protocol'] = get_protocolsio_text(datasetId) 
        #text from any txt file in the dataset except license files
        data_text[datasetId]['text files'] = get_dataset_text_files(datasetId)
    return data_text

def get_keywords(data_text):
    
     
    # clean up text (remove stopwords etc.)
    
    # run keyword indentifier
    
    #this is an example with randomly generated keywords by be
    # we need a json format structure with keyword and their "weight"
    # I suggest we choose the weight as the minimum number of times a word is detected in a dataset text
    # so if the weight is 15, it means that the given word appears at least 15 times in each dataset
    keywords_json = {}
    keywords_json['vagus'] = 15 
    keywords_json['nerve'] = 12
    keywords_json['morphology'] = 10
    keywords_json['staining'] = 9
    keywords_json['diameter'] = 8
    keywords_json['nerve'] = 7
    keywords_json['experiment'] = 5
    keywords_json['lab'] = 6
    keywords_json['segmentation'] = 5
    keywords_json['fascicle'] = 4
    keywords_json['nerve'] = 3
    
    return keywords_json

def get_abstract(data_text):
    # clean up text (remove stopwords etc.)
    
    # run text summarizer for all the datasets combined
    abstract = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    return abstract

def get_text_correlation(data_text):
    # clean up text (remove stopwords etc.)
    
    # run text correlation calculator
    
    return 


## Test
input_file = os.path.join(input_dir, 'input.json') 
datasetIdsinput = json.load(open(input_file))
list_datasetId = datasetIdsinput['datasetIds']
list_datasetId = [str(x) for x in list_datasetId]

#storage dict to be saved as a json and returned to front-end
dataset_data = {}

#knowledge graph data
dataset_data['knowledge_graph'] = {}
for datasetId in list_datasetId:
    dataset_data['knowledge_graph'][datasetId] = get_knowledge_graph_data(datasetId)

#summary table
dataset_data['summary table'] = {}
for datasetId in list_datasetId:
    dataset_data['summary table'][datasetId] = get_summary_table_data(datasetId)

#keywords
data_text = get_all_datasets_text(list_datasetId)
keywords = get_keywords(data_text)
dataset_data['keywords'] = keywords

#text correlation matrix
#abstract = get_abstract(data_text)
#dataset_data['abstract'] = abstract

#abstract
abstract = get_abstract(data_text)
dataset_data['abstract'] = abstract

#save output
output_file = os.path.join(output_dir, 'output.json') 
with open(output_file, 'w+') as f:
    # this would place the entire output on one line
    # use json.dump(lista_items, f, indent=4) to "pretty-print" with four spaces per indent
    json.dump(dataset_data, f) 