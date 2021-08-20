# pommes-data

**A full-featured transparent data preparation routine from raw data to POMMES model inputs**

This is the **data preparation routine** of the fundamental power market model *POMMES* (**PO**wer **M**arket **M**odel of **E**nergy and re**S**ources).<br>
Please navigate to the section of interest to find out more.

## Contents
* [Introduction](#introduction)
* [Documentation](#documentation)
* [Installation](#installation)
* [Contributing](#contributing)
* [Citing](#citing)
* [License](#license)

## Introduction
*POMMES* itself is a cosmos consisting of a **dispatch model**, a **data preparation routine** (stored in this repository and described here) and an **investment model** for the German wholesale power market. The model was originally developed by a group of researchers and students at the [chair of Energy and Resources Management of TU Berlin](https://www.er.tu-berlin.de/menue/home/) and is now maintained by a group of alumni and open for other contributions.

If you are interested in the actual dispatch or investment model, please find more information here:
- [pommes-dispatch](https://github.com/pommes-public/pommes-dispatch): A bottom-up fundamental power market model for the German electricity sector
- pommes-invest: A multi-period integrated investment and dispatch model for the German power sector (upcoming).

## Documentation
The data preparation is mainly carried out in this **[jupyter notebook](https://github.com/pommes-public/pommes-data/blob/dev/data_preparation.ipynb)**. The data sources used as well as the calculation and transformation steps applied are described in a transparent manner. In addition to that, there is a **[documentation of pommes-data]()** on readthedocs. This in turn contains a documentation of the functions and classes used for data preparation. 

## Installation
To set up `pommes-data`, you have to set up a virtual environment (e.g. using conda) or add the required packages to your python installation.

`pommes-data` is (to be) hosted on [PyPI](). To install it, please use the following command
```
pip install pommes-data
```

For now, you still have to clone the environment and copy the files locally by typing
```
git clone https://github.com/pommes-public/pommes-data.git
```
After cloning the repository, you have to install the required dependencies. Make sure you have conda installed as a package manager. If not, you can download it [here](https://www.anaconda.com/). Open a command shell and navigate to the folder where you copied the environment to. Use the following command to install dependencies
```
conda env create -f environment.yml
```
Activate your environment by typing
```
conda activate pommes_data
```

## Contributing
Every kind of contribution or feedback is warmly welcome.<br>
We use the GitHub issue management as well as pull requests for collaboration. We try to stick to the PEP8 coding standards.

## Citing
A publication using and introducing `pommes-dispatch` as well as `pommes-data` for data preparation is currently in preparation.

If you are using `pommes-data` for your own analyses, please cite as:<br>
*Werner, Y.; Kochems, J. et al. (2021): pommes-data. A full-featured transparent data preparation routine from raw data to POMMES model inputs. https://github.com/pommes-public/pommes-data, accessed YYYY-MM-DD.*

We furthermore recommend to name the version tag or the commit hash used for the sake of transparancy and reproducibility.

## License
This software is licensed under MIT License. For the licensing of the data, please see the breakdown below.

### Software

Copyright 2021 pommes developer group

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Data
| data set | license | distributed with the repository | download link |
| ---- | ---- | ---- | ---- |
| dummy data set 1 | GPLv3 | yes | https://fantasy-url-for-fantasy-dataset1.com |
| dummy data set 2 | GPLv3 | no | https://fantasy-url-for-fantasy-dataset2.com |
