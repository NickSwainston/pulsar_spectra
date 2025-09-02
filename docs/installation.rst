Installation
============

For Users
---------

From PyPI
^^^^^^^^^
The latest stable release can be installed from [PyPI](https://pypi.org/project/pulsar-spectra/) using `pip`:

.. code-block:: bash

    pip install pulsar-spectra

or using `uv`:

.. code-block:: bash

    uv pip install pulsar-spectra

From Docker Hub
^^^^^^^^^^^^^^^
There is a Docker container that you can install with:

.. code-block:: bash

    docker pull nickswainston/pulsar_spectra

For Developers
--------------

Using uv
^^^^^^^^
To install the package from source, first clone the repository and change into the repository directory.
We recommend using `uv` to ensure a consistent development environment. To install the package, run:

.. code-block:: bash

    uv sync --locked

By default, this will install the dependencies in the `dev` group but no other groups. If you
are developing documentation, then include the `docs` group:

.. code-block:: bash

    uv sync --locked --group docs

Then activate the virtual environment:

.. code-block:: bash

    source .venv/bin/activate

Using pip
^^^^^^^^^
Alternatively, you can install the package into your working environment using `pip`. In the repository
directory, run:

.. code-block:: bash
    pip install .

To install the development dependencies, run:

.. code-block:: bash
    pip install --group dev .

To install the documentation dependencies, run:

.. code-block:: bash
    pip install --group docs .
