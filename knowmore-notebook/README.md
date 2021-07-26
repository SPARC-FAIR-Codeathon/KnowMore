# KnowMore notebook
This folder contains the files required to run the KnowMore Jupyter notebook, which bypass the sparc-app front-end and flask server to run the knowledge discovery process directly on osparc based on the dataset Ids specified in the notebook by the user. 

## Clone repo
Clone the repo and submodules
```
git clone https://github.com/SPARC-FAIR-Codeathon/KnowMore.git --recurse
```

## Prerequisites 
We recommend using Anaconda to create and manage your development environments for KnowMore. All the subsequent instructions are provided assuming you are using [Anaconda (Python 3 version)](https://www.anaconda.com/products/individual).

### cd into this folder

Open Anaconda prompt (Windows) or the system Command line interface then naviguate to this folder
```sh
cd .KnowMore/knowmore-notebook

```

### Setup conda env
```sh
$ conda create -n "knowmore-notebook-env" python=3.6
$ conda activate knowmore-notebook-env
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

## Open notebook
Open the notebook with you prefer notebook editor such as Jupyter lab and change the kernel to the above-defined environment (e.g., see [here](https://medium.com/@nrk25693/how-to-add-your-conda-environment-to-your-jupyter-notebook-in-just-4-steps-abeab8b8d084)). 




