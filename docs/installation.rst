Installation
============

For Users
---------

From PyPI
^^^^^^^^^
The latest stable release can be installed from `PyPI <https://pypi.org/project/pulsar-spectra/>`_ using ``pip``:

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


For Publishers
--------------

If you plan to publish your results to a scientific journal, it is important you use a specific version/tag of pulsar_spectra instead of the latest latest and use similar python dependencies as possible.
To do this we recommend that you either use the ``uv`` lock file (defines specific python dependency versions) or the docker container (has specific python dependency versions already installed).

To check what versions are available you can either check the `GitHub release page <https://github.com/NickSwainston/pulsar_spectra/releases>`_ or, in the repository, run the command:

.. code-block:: bash

    git tag

The most recent version is likely what you will need.
Replace ``<version>`` in the following commands with the version you have chosen.


From Docker Hub
^^^^^^^^^^^^^^^

There is a Docker container that you can install with:

.. code-block:: bash

    docker pull nickswainston/pulsar_spectra:<version>


Using uv
^^^^^^^^

To install the package from source, first clone the repository and move into the repository directory.
Then to revert the repository to a certain version of the software, run the following command:

.. code-block:: bash

    git checkout tags/<version>

You can then install that version in a virtual environment using ``uv``
We recommend using ``uv`` to ensure a consistent development environment that uses exact python dependencies.
To install the package, run:

.. code-block:: bash

    uv sync --locked

By default, this will install the dependencies in the ``dev`` group but no other groups. If you
are developing documentation, then include the ``docs`` group:

.. code-block:: bash

    uv sync --locked --group docs

Then activate the virtual environment:

.. code-block:: bash

    source .venv/bin/activate



For Developers
--------------

Using uv
^^^^^^^^
To install the package from source, first clone the repository and change into the repository directory.
We recommend using ``uv`` to ensure a consistent development environment. To install the package, run:

.. code-block:: bash

    uv sync --locked

By default, this will install the dependencies in the ``dev`` group but no other groups. If you
are developing documentation, then include the ``docs`` group:

.. code-block:: bash

    uv sync --locked --group docs

Then activate the virtual environment:

.. code-block:: bash

    source .venv/bin/activate

Using pip
^^^^^^^^^
Alternatively, you can install the package into your working environment using ``pip``. In the repository
directory, run:

.. code-block:: bash

    pip install .

To install the development dependencies, run:

.. code-block:: bash

    pip install --group dev .

To install the documentation dependencies, run:

.. code-block:: bash

    pip install --group docs .
