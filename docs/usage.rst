Installation and User's guide
=============================

.. contents::

Installation
------------

There are **two use cases** for using ``pommesdata``:
1. Using readily prepared output data sets as ``pommesdispatch`` or ``pommesinvest`` inputs
2. Understanding and manipulating the data prep process (inspecting / developing)

If you are only interested in the readily prepared data sets (option 1), you can obtain
them from zenodo and download it here: `https://zenodo.org/ <https://zenodo.org/>`_

If you are interested in understanding the data preparation process itself or
if you wish to include own additions, changes or assumptions, you can
you fist have to
`fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_
 and then clone the repository, in order to copy the files locally by typing

.. code::

    git clone https://github.com/pommes-public/pommesdata.git

| After cloning the repository, you have to install the required dependencies.
 Make sure you have conda installed as a package manager.
 If not, you can download it `here <https://www.anaconda.com/>`_.
| Open a command shell and navigate to the folder
 where you copied the environment to.
| Use the following command to install dependencies

.. code::

    conda env create -f environment.yml

Activate your environment by typing

.. code::

    conda activate pommes_data

User's guide
------------

Using ``pommesdata`` is fairly simple:

1. Open the `jupyter notebook <https://github.com/pommes-public/pommesdata/blob/dev/data_preparation.ipynb>`_.

* Activate your environment by typing

.. code::

    conda activate pommes_data

* Open jupyterlab by typing

.. code::

    jupyterlab

.. note::

    You may also use jupyter notebook, the predecessor of jupyterlab.

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
