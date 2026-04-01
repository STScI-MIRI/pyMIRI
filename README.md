<h1 align="center">pyMIRI</h1>
<h2 align="center">Sachin's MIRI data reduction, calibration, and analysis package.</h2>

================================================================================

## Installation.
1. Create an conda environment to install this package.
```shell
conda create --name pymiri_utils python=3.11
```

2. Activate the conda environment
```shell
conda activate pymiri_utils
```

3. Install package using pip. I have used the HTTP protocol to get the package but 
you can also use SSH if you prefer.
```shell
pip install git+https://github.com/STScI-MIRI/pyMIRI.git
```
--------------------------------------------------------------------------------

This project contains pymiri package that can be used to work with MIRI data. 
The pacakge contains CLI scripts: get_data, select_data, generate_imager_flat,
and generate_lrs_flat.

- get_data is a command line script that can be used to get appropriate data 
from the MAST archive.

- select_data is a script to select the appropriate files to use in generating 
MIRI imager flat.

- generate_imager/lrs_flat is a script to build a MIRI imager/lrs flat using an 
input manifest (output of the select_data script).

More detailed installation instruction will be added soon to this repo.

Contributors
------------
Sachin(dev) Shenoy

License
-------
This code is licensed under a OSI Approved MIT license (see the``LICENSE`` 
file).
