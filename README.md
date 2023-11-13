# Dynamics SBM DEA Python code  

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

## Overview

This repository contains Python code replicating the [Dynamics Slack-Based DEA Model] (https://doi.org/10.1016/j.omega.2009.07.003) proposed in Tone & Tsutsui's (2010) paper. The Dynamics SBM DEA is a DEA model widely used for analyzing the evolving structure of dynamic networks. This project aims to provide an open-source implementation for researchers and practitioners interested in understanding and applying the Dynamics SBM.


A brief summary of the Dynamic SBM DEA model (Tone & Tsutsui's, 2010): 
> The SBM model is non-radial and can deal with inputs/outputs individually, contrary to the radial approaches that assume proportional changes in inputs/outputs. Furthermore, according to the characteristics of carry-overs, we classify them into four categories, i.e. desirable, undesirable, free and fixed. Desirable carry-overs correspond, for example, to profit carried forward and net earned surplus carried to the next term, while undesirable carry-overs include, for example, loss carried forward, bad debt and dead stock. Free and fixed carry-overs indicate, respectively, discretionary and non-discretionary ones.



## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Reference](#reference)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)


## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/georgia-max/DynamicsSBM.git 
    ```

2. Navigate to the project directory:

    ```bash
    cd DynamicSBM
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

First Step: Download the Sample Dataset Folder [Here](https://drive.google.com/drive/u/1/folders/14K7A1Y9wQ7JhzqdKBcMvfIjeoj7Q9_ET), and add them to the folder. 
Second Step: To run the test code, check out Jupyter Notebook [DSBM_DEA_function_example.ipynb](https://github.com/georgia-max/DynamicsSBM/blob/master/DynamicSBM/DSBM_DEA_function_example.ipynb) for step-by-step guidelines.    


## Example


```python
cd DynamicSBM
python ./Main.py

## Reference

1. Tone, K., & Tsutsui, M. (2010). Dynamic DEA: A slacks-based measure approach. Omega, 38(3-4), 145-156.

