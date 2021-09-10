Installation and User's guide
=============================

.. contents::

Installation
------------

To set up ``pommes-data``, you have to set up a virtual environment (e.g. using conda)
or add the required packages to your python installation.

``pommes-data`` is (to be) hosted on `PyPI <https://pypi.org/>`_
To install it, please use the following command

.. code::

    pip install pommes-data

For now, you still have to clone the environment and copy the files locally by typing

.. code::

    git clone https://github.com/pommes-public/pommes-data.git

After cloning the repository, you have to install the required dependencies.
Make sure you have conda installed as a package manager.
If not, you can download it `here <https://www.anaconda.com/>`_.
Open a command shell and navigate to the folder where you copied the environment to.
Use the following command to install dependencies

.. code::

    conda env create -f environment.yml

Activate your environment by typing

.. code::

    conda activate pommes_data

User's guide
------------

Using ``pommes-data`` is fairly simple:

1. Open the `jupyter notebook <https://github.com/pommes-public/pommes-data/blob/dev/data_preparation.ipynb>`_.

* Activate your environment by typing

.. code::

    conda activate pommes_data

* Open jupyterlab by typing

.. code::

    jupyterlab

3. Configure and run the jupyter notebook.

* Adjust the notebook workflow settings if you wish so. The respective
  code cell looks like this

.. code:: python

    year = 2019
    use_new_data_set = True
    shutdown_assumption = 2022
    cluster_transformers_DE = True
    res_capacity_projection = "Prognos"  # "EEG_2021"

3. Copy all files that were created and are stored in the folder `prepared_data`
   to your ``pommes-dispatch`` or ``pommes-invest`` model input data folder.

That`s already it! :-)

.. note::

    If you want to, you may change whatever assumption you like in the jupyter notebook.
