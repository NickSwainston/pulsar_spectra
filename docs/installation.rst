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


If you plan to publish your results in a scientific journal, it is important that you use a specific version/tag of ``pulsar_spectra`` and keep the Python dependencies as similar to that version as possible.
To do this, we recommend that you either use the ``uv`` lock file (which defines specific Python dependency versions) or the Docker container (which has specific Python dependency versions already installed).

To check what versions are available, you can either browse the `GitHub release page <https://github.com/NickSwainston/pulsar_spectra/releases>`_ or, in the repository, run the command:

.. code-block:: bash

    git tag

The most recent version is likely what you will need.
Replace ``<version>`` in the following commands with the version you have chosen.


From Docker Hub
^^^^^^^^^^^^^^^

There is a Docker container that you can install with:

.. code-block:: bash

    docker pull nickswainston/pulsar_spectra:<version>


From source (using ``uv``)
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are installing the package from source, we recommend first reverting the repository to a specific version.
This can be done using following command:

.. code-block:: bash

    git checkout tags/<version>

You can then install that version by following the instructions in the :ref:`for_developers_uv` section below.


For Developers
--------------

To install the package from source, first clone the repository and move into the repository directory.
You can then install the package using either ``uv`` or ``pip``, as described below.

.. _for_developers_uv:

Using uv (Recommended)
^^^^^^^^^^^^^^^^^^^^^^

The package can be installed in a new virtual environment using ``uv``, which will ensure a consistent development environment.
This can be done with the command:

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
