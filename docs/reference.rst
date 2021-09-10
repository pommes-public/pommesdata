Reference docs
==============

.. contents::

data_preparation
----------------

```data_preparation.ipynb`` is the main project file. It is a jupyter notebook
that contains the code and markdown description from raw data and assumptions
to *POMMES* model input used for ``pommes-dispatch`` as well as ``pommes-invest``.

Since it contains a transparent description itself, please directly `refer
to it <https://github.com/pommes-public/pommes-data/blob/dev/data_preparation.ipynb>`_
and jump to the data source or component you are interested in. We recommend
to use a jupyter notebook or jupyterlab table of content extension to facilitate
navigation. You may find instructions for installing and using them here:

* `jupyter nbextension <https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html>`_
* `jupyterlab extensions <https://jupyterlab.readthedocs.io/en/stable/user/extensions.html>`_

data_prep
---------

The ``data_prep`` package contains some functions that are used in the data
preparation process.

Modules
+++++++

* ``eeg_transformers.py`` contains functions for reading in and creating RES units
  under the German Renewable Energies Act (Erneuerbare-Energien-Gesetz - EEG).
  This comprises routines for reading in data, clustering, assigning market values etc.
  Additionally, routines for the projection of levelized costs of electricity (LCOE)
  for RES units are included.
* ``hydro.py`` contains functions for reading in hydro generation data, both for
  reservoir power plants as well as pumped storage plants. Additionally, it contains
  a routine for resampling hydro inflow data.
* ``tools.py`` contains a collection of functions for facilitating the workflow,
  such as reading in data, transferring data to the oemof.solph naming required or
  assigning time-dependent NTC values for interconnectors.
* ``transformer_aggregation.py`` contains routines for clustering conventional
  power plant data.
