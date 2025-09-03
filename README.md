pulsar_spectra
======
<div class="bg-gray-dark" align="center" style="background-color:#24292e">
<img src="docs/logos/logo_white.svg" height="150px" alt="pulsar_spetra logo">
<!-- <br/>
<a href='https://all-pulsar-spectra.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/all-pulsar-spectra/badge/?version=latest' alt='Documentation Status' />
</a>
<a href='https://github.com/NickSwainston/pulsar_spectra/actions'>
    <img src='https://github.com/github/docs/actions/workflows/main.yml/badge.svg' alt='Test Status' />
</a> -->
</div>

![tests](https://github.com/NickSwainston/pulsar_spectra/actions/workflows/pytest.yaml/badge.svg)
![documentation](https://readthedocs.org/projects/all-pulsar-spectra/badge/?version=latest)

A simple interface to record pulsar's flux density measurements for a large number of papers and perform fitting of spectral models.


Installation
=====

For Users
-----

### From PyPI
The latest stable release can be installed from [PyPI](https://pypi.org/project/pulsar-spectra/) using `pip`:
```bash
pip install pulsar-spectra
```
or using `uv`:
```bash
uv pip install pulsar-spectra
```

### From Docker Hub
There is a Docker container that you can install with:
```bash
docker pull nickswainston/pulsar_spectra
```


For Publishers
-----

If you plan to publish your results in a scientific journal, it is important that you use a specific version/tag of `pulsar_spectra` and keep the Python dependencies as similar to that version as possible.
To do this, we recommend that you either use the `uv` lock file (which defines specific Python dependency versions) or the Docker container (which has specific Python dependency versions already installed).

To check what versions are available, you can either browse the [GitHub release page](https://github.com/NickSwainston/pulsar_spectra/releases) or, in the repository, run the command:

```bash
git tag
```

The most recent version is likely what you will need.
Replace `<version>` in the following commands with the version you have chosen.


### From Docker Hub

There is a Docker container that you can install with:

```bash
docker pull nickswainston/pulsar_spectra:<version>
```

### From source

If you are installing the package from source, we recommend first reverting the repository to a specific version.
This can be done using following command:

```
git checkout tags/<version>
```

You can then install that version by following the instructions in the "For Developers" section below.

For Developers
-----

To install the package from source, first clone the repository and move into the repository directory.
You can then install the package using either `uv` or `pip`, as described below.

### Using uv (Recommended)

The package can be installed in a new virtual environment using `uv`, which will ensure a consistent development environment.
This can be done with the command:
```bash
uv sync --locked
```
By default, this will install the dependencies in the `dev` group but no other groups. If you
are developing documentation, then include the `docs` group:
```bash
uv sync --locked --group docs
```
Then activate the virtual environment:
```bash
source .venv/bin/activate
```

### Using pip

Alternatively, you can install the package into your working environment using `pip`. In the repository
directory, run:
```bash
pip install .
```
To install the development dependencies, run:
```bash
pip install --group dev .
```
To install the documentation dependencies, run:
```bash
pip install --group docs .
```

Help
=====
The documentation can be found [here](https://pulsar-spectra.readthedocs.io/en/latest/)

Credit
=====
If you use pulsar_spectra for your research please give credit by citing [Swainston et al 2022, PASA, 39, e056](https://ui.adsabs.harvard.edu/abs/2022arXiv220913324S/abstract) and the [publications of the data](https://pulsar-spectra.readthedocs.io/en/latest/catalogue.html#papers-included-in-our-catalogue) used in your spectral fits.

Until there is a more appropriate method for crediting software development and maintainance, please also consider including me as a co-author on publications which rely on pulsar_spectra.

Catalogue data
=====
The catalogue comprises YAML files containing pulsar flux density measurements for each paper the repository has included.
You should not assume that this repository has all flux density measurements for a pulsar you are interested in.
Instead, you should search through the literature to find all papers that contain flux density measurements of
the pulsar and confirm all of those papers are in the catalogue. You can find a list of the papers in the catalogue [here](https://pulsar-spectra.readthedocs.io/en/latest/catalogue.html#papers-included-in-our-catalgoue)

If you would like to add a new paper to the catalogue read [the guide](https://pulsar-spectra.readthedocs.io/en/latest/catalogue.html#adding-papers)
