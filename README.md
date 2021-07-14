[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
<!-- [![DOI](https://zenodo.org/badge/185270688.svg)](https://zenodo.org/badge/latestdoi/185270688) -->

<!-- HEADER -->
<br />
<p align="center">
  <a href="#">
    <img src="https://github.com/SPARC-FAIR-Codeathon/KnowMore/blob/main/docs/kmlogo-with-text3.png" alt="Logo" height="80">
  </a>
  <br/>
  <p align="center">Say "no more" to tedious manual discovery across SPARC datasets <p>

  <p align="center">
     <br/>
    <a href="https://github.com/bvhpatel/SODA/issues">Report Issue</a>
    ·
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSfyUw2_NI1-2tlAr8oB5_JcJ_yjTB-zUDt9skfGjNU9qjITwg/viewform?ts=5e433bea">Submit feedback </a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About](#about)
* [The Problem](#the-problem)
* [Our Solution - KnowMore](#our-solution---knowmore)
* [Workflow](#workflow)
* [Using KnowMore](#using-knowmore)
* [Using the Source Code](#using-the-source-code)
* [License](#license)
* [Team](#team)
* [Acknowledgements](#acknowledgements)

## About
This is the repository of Team KnowMore (Team #6) at the SPARC Codeathon 2021. Click [here](https://commonfund.nih.gov/sparc) to find out more about the NIH SPARC Program. Click [here](https://sparc.science/help/2021-sparc-fair-codeathon) to find out more about the SPARC Codeathon 2021. Checkout the [Team section](#team) of this page to find out more about our team members.

## The Problem
All the datasets generated by SPARC funded projects are curated and shared according to strict guidelines that ensure these datasets are [Findable, Accessible, Interoperable, and Reusable (FAIR)](https://www.go-fair.org/fair-principles/). Specifically, the datasets are organized and annotated following the [SPARC Data Structure](https://www.biorxiv.org/content/10.1101/2021.02.10.430563v2) and then shared publicly on the SPARC Data Portal ([sparc.science](https://sparc.science/)). The SPARC program thus provides a wealth of openly available and well curated datasets. This is great! But...

While it is very easy to look at the findings of each individual dataset on the portal, there is currently **no easy way to make preliminary discoveries or analysis across multiple datasets of choice**. Typically, a researcher wanting to find relations across datasets would have to do so manually, i.e., read the description of each datasets, go through their protocols, browse files that are accessible from the browser, etc. If they find that the datasets could have some interesting relations that is worth investigating further, they will then have to download each dataset (payment may be required for large datasets according to AWS pricing) before analyzing them further. This is a tedious process that needs to be urgently improved in order to 1) Enable rapid discoveries from SPARC datasets, 2) Encourage more researchers to use the SPARC Data Portal.


## Our Solution - KnowMore
To address this problem, we have developed a tool called KnowMore for the SPARC Data Portal. KnowMore is an automated knowledge discovery tool that allows users of the portal to visualize, in just a few click, potential relations and/or correlation between multiple SPARC datasets of their choice. This simple process is illustrated in the figure below. 

<br/>
<p align="center">
   <img src="https://github.com/SPARC-FAIR-Codeathon/KnowMore/blob/main/docs/knowmore-usage-blue.png" alt="knowmore-usage" width="900">
  <br/> 
  <br/> 
  <i> Illustration of the simple user side workflow of KnowMore. </i>
  </img>
 </p> 
<br/>

The output of KnowMore consists of multiple interactive items displayed to the user: 
1. Common keywords describing the datasets
2. An automated summary paragraph of the combined datasets
3. A knowledge graph
4. Clustering of similar images (if images are included in the datasets)
5. Correlation between measured quantities (if tabular data is included in the datasets). 

A screenshot of a sample output is presented in the figure below. This output can provide a foundation to the user for rapidly identifying potential relations or previously unknown correlations between the data and proceed accordingly in their investigation.

<br/>
<p align="center">
   <img src="" alt="knowmore-output" width="900">
  <br/> 
  <i> Sample output from KnowMore. It consists of interactive text and plots display to the user.</i>
  </img>
 </p> 
<br/>




Under the hood, KnowMore uses several Machine Learning and Data Science workflows to output the above-mentioned elements, including:
*	Natural Language Processing
*	Image classification
*	Correlation matrix

## Workflow
The overall workflow of KnowMore is shown in the figure below. 

<br/>
<p align="center">
   <img src="https://github.com/SPARC-FAIR-Codeathon/KnowMore/blob/main/docs/workflow.png" alt="knowmore-wokflow" width="900">
  <br/> 
  <i> Overall technical workflow of KnowMore. The red blocks highlight major code that has been developed during this Codeathon. </i>
  </img>
 </p> 
<br/>



## Using KnowMore
You can use KnowMore directly on our fork of the SPARC Data Portal: (add link)

Follow the steps described below:
1. Find datasets of interest and click on the "Add to automated discovery" button, visible in the header of the datasets, to add each of them in the KnowMore analysis 
2. Go to the KnowMore tab, and check that all your selected datasets are listed
3. Click on "Discover" to initiate the automated discovery process
4. Wait until the interactive results are displayed

## Using the Source Code

## License
KnowMore is distributed under the MIT License. See [LICENSE](https://github.com/SPARC-FAIR-Codeathon/KnowMore/blob/main/LICENSE) for more information.

<!-- ## FAIR practices -->

## Team
* [Bhavesh Patel](https://github.com/bvhpatel/) (Lead)
* [Ryan Quey](https://github.com/RyanQuey) (SysAdmin)
* [Eric Ramirez](https://github.com/netshadows/) (ML lead)
* [Anmol Kiran](https://github.com/codemeleon) (Writer - Documentation)
* [Matthew Schiefer](https://github.com/schiefma/) (Writer - Manuscript)

## Acknowledgements



[contributors-shield]: https://img.shields.io/github/contributors/SPARC-FAIR-Codeathon/KnowMore.svg?style=flat-square
[contributors-url]: https://github.com/SPARC-FAIR-Codeathon/KnowMore/graphs/contributors
[stars-shield]: https://img.shields.io/github/stars/SPARC-FAIR-Codeathon/KnowMore.svg?style=flat-square
[stars-url]: https://github.com/SPARC-FAIR-Codeathon/KnowMore/stargazers
[issues-shield]: https://img.shields.io/github/issues/SPARC-FAIR-Codeathon/KnowMore.svg?style=flat-square
[issues-url]: https://github.com/SPARC-FAIR-Codeathon/KnowMore/issues
[license-shield]: https://img.shields.io/github/license/SPARC-FAIR-Codeathon/KnowMore.svg?style=flat-square
[license-url]: https://github.com/SPARC-FAIR-Codeathon/KnowMore/blob/master/LICENSE
