# KnowMore osparc jobs
This folder contains the files required to run our jobs on [osparc](http://docs.osparc.io/). 
- We send a input.json (containing dataset Ids) and the main.zip (which has two files zipped: requirements.txt and main.py) to the osparc Python Runner service) which excutes the main.py code and sends back an output.zip folder with requested outputs.
- Subsequently, we send a matlab-input-folder.zop file, that comes in the output.zip folder to our custome Matlab service on osparc which excutes the main.m code already deployed there and sends back an matlab-output.zip folder with requested outputs.

If either of the requirements.txt or main.py files get changed, make sure to make a new main.zip with these files. The matlab code is already deployed as a service on osparc and is not required to run the associated job. If deploying a new version of the code is required, please reach out to the <a href="mailto: support@osparc.io"> osparc support </a>

### Clone repo
Clone the repo and submodules
```
git clone https://github.com/SPARC-FAIR-Codeathon/KnowMore.git --recurse
```

## Setup for the Python code

### Prerequisites 
We recommend using Anaconda to create and manage your development environments for KnowMore. All the subsequent instructions are provided assuming you are using [Anaconda (Python 3 version)](https://www.anaconda.com/products/individual).

### cd into this folder

Open Anaconda prompt (Windows) or the system Command line interface then naviguate to this folder
```sh
cd .KnowMore/assets/INPUT_FOLDER

```

### Setup conda env
```sh
$ conda create -n "knowmore-py-env" python=3.6
$ conda activate knowmore-flask-env
```

### Install Python dependencies
```sh
$ conda install pip
$ pip install -r requirements.txt
```

### Setup env vars
The environment variables required are listed in the table below along with information on how to get them

<table>
<thead>
  <tr>
    <th>Suggested name</th>
    <th>Value or instructions for obtaining it</th>
    <th>Purpose</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>OSPARC_API_KEY</td>
    <td> <a href="mailto: support@osparc.io"> Contact osparc support </a> </td>
    <td> Sending jobs to osparc</td>
  </tr>
  <tr>
    <td>OSPARC_API_SECRET</td>
    <td><a href="mailto: support@osparc.io"> Contact osparc support </a></td>
    <td>Sending jobs to osparc </td>
  </tr>
</tbody>
</table>


Each of them can be set in your conda environment as follows
```sh
$ conda env config vars set MY_VAR=value1 MY_OTHER_VAR=value2
```

###
Edit and test the main.py file with your favorite text editor.

## Setup for the Matlab code
The Matlab code was developed and tested with Matlab 2020a.


