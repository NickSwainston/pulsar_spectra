Catalogue
=========

The catalogue comprises YAML files containing pulsar flux density measurements for each paper the repository has included.
You should not assume that this repository has all flux density measurements for a pulsar you are interested in.
Instead, you should search through the literature to find all papers that contain flux density measurements of
the pulsar and confirm all of those papers are :ref:`in the catalogue<cat_papers>`.
If you would like to add a new paper to the catalogue see the :ref:`Adding to the catalogue<adding_papers>` section.


Using the catalogue
-------------------

This section will explain how to use the catalogue.
If you would like more information, you can see the module documentation in :ref:`the catalogue module description<catalogue_module>`.

You can use the following command to get all fluxes from the catalogue.

.. code-block:: python

    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    cat_dict = collect_catalogue_fluxes()

cat_dict will have the format

.. code-block:: python

    cat_dict = {"Pulsar Jname":[["List of frequencies in MHz"],
                                ["List of flux densities in mJy"],
                                ["List of flux density uncertainties in mJy"],
                                ["The reference label (in the format 'Author_year')"]],
                "Other pulsar":[["List of frequencies in MHz"],
                                ["List of flux densities in mJy"],
                                ["List of flux density uncertainties in mJy"],
                                ["The reference label (in the format 'Author_year')"]],
               }

For example, this is the data for PSR J1453-6413.

.. code-block:: python

    print(cat_dict['J1453-6413'])
    [[950.0, 800.0, 1400, 8400, 728, 1382, 3100, 185.0, 200.0, 154.0, 200, 400, 150, 800],
     [42.0, 89.0, 14.0, 1.5, 80.0, 18.0, 2.4, 1244.0, 684.0, 630.0, 684.0, 230.0, 630.0, 53.0],
     [4.2, 26.7, 1.4, 0.75, 10.0, 1.0, 0.5, 20.0, 23.0, 200.0, 23.0, 115.0, 20.0, 3.0],
     ['van_Ommen_1997', 'van_Ommen_1997', 'Hobbs_2004', 'Johnston_2006', 'Jankowski_2018', 'Jankowski_2018', 'Jankowski_2018', 'Xue_2017', 'Xue_2017', 'Bell_2016', 'Murphy_2017', 'Taylor_1993', 'Bell_2016', 'Jankowski_2019']]

You can add your data like so before fitting the spectra

.. code-block:: python

    freqs, fluxs, flux_errs, refs = cat_dict[pulsar]
    freqs += [150.]
    fluxs += [1000.]
    flux_errs += [100.]
    refs += ["Your Work"]

You can `exclude` papers that you don't trust the results or if you think they're negatively affecting your fit.
For example, I can create a cat_dict without Sieber et al. 1973 like so

.. code-block:: python

    cat_dict = collect_catalogue_fluxes(exclude=["Sieber_1973"])

Inversely if you only what the flux density measurements from a few papers, you can use the `include` argument.
For example, you can create a cat_dict that only includes data from Murphy et al. 2017 and Xue et al. 2017 like so


.. code-block:: python

    cat_dict = collect_catalogue_fluxes(include=["Murphy_2017", "Xue_2017"])


.. _cat_papers:

Papers included in our catalogue
--------------------------------
..
    Regenerate this table with this code https://github.com/NickSwainston/misc_scripts/blob/master/spectra_paper/check_ref_num_and_rage.py

.. csv-table:: Papers included in our catalogue
    :header: "Paper","# Pulsars","Frequency range (MHz)","Link"
    :file: papers_in_catalogue.csv


.. _finding_papers:

Finding more papers to add to the catalogue
-------------------------------------------
The pulsar\_spectra catalogue is not a complete catalogue of flux density measurements, so researchers should do
their own literature review to find any publications that have not yet been included in the catalogue.
The following sections are suggestions of some ways to find new publications.


.. _look_up_ATNF:

Look up ANTF references
^^^^^^^^^^^^^^^^^^^^^^^
If you see a reference label ending in \_ATNF (see below for an example), those flux density measurements were imported from the ATNF catalogue.

.. image:: figures/atnf_label_example.png
  :width: 800

The ATNF catalogue values often record flux density measurements at the nearest standard
frequency, which can be inaccurate and should be replaced with the actual value.

The first author and the year in the reference label will help you find the full
reference on the `ATNF references page <https://www.atnf.csiro.au/research/pulsar/psrcat/psrcat_ref.html>`_.
The publication can be :ref:`added to the catalogue <adding_papers>`.


.. _adding_papers:

Adding to the catalogue
-----------------------
If you would like to add a new paper to the catalogue, you should first format the data into CSV with the following format:

.. code-block:: bash

    Pulsar Jname,Frequency (MHz),Flux Density (mJy),Flux Density Uncertainty (mJy)
    J0030+0451,150,37.6,4.4
    J0030+0451,180,32.4,3.2
    J0034-0534,150,202.8,7.9
    J0034-0721,150,367.9,10.5

If the paper does not provide a flux density, then the script will assume a 50\% uncertainty if you do not have to include it in your CSV like so:

.. code-block:: bash

    Pulsar Jname,Frequency (MHz),Flux Density (mJy)
    J0030+0451,150,37.6
    J0030+0451,180,32.4
    J0034-0534,150,202.8
    J0034-0721,150,367.9

If the paper only provides the B name then the script will convert to a J name using `psrqpy` as long as the PSR name starts with a B:

.. code-block:: bash

    Pulsar Jname,Frequency (MHz),Flux Density (mJy)
    B0037+56,390,3.5
    B0045+33,390,4.5
    B0052+51,390,3.6
    B0053+47,390,5.8

Then move to the scripts subdirectory of the repository and run the command:

.. code-block:: bash

    python csv_to_yaml.py --csv your_paper.csv --ref author_year

This will put a YAML file of the paper in pulsar_spectra/catalogue_papers/.
You should then reinstall the software (:code:`python setup.py install`) then run a spectral fit to confirm it worked.


Catalogue standards for new paper
---------------------------------
For flux density measurements to be uploaded to the catalogue, they must meet the following criteria and standards:

1. Published
    The paper must be peer-reviewed and published.
    We are considering altering this to accept regular measurement programs with an established and reliable method.

2. New results
    If the paper includes flux density measurements from previous publications, do not include them.

3. Include bandwidth
    A bandwidth value is required for each flux density measurement.
    If there is no mention of the bandwidth in the paper, investigate previous publications that use the telescope to determine what bandwidth was likely used.
    If there is no way to determine the bandwidth used, do not use the paper.

4. Flux density uncertainties
    If the paper does not supply a flux density uncertainty, assume a relative uncertainty of 50 %.

5. Do not include upper limits
    The catalogue does not currently have a way of handling upper limits, so do not include them.
    If you have a suggestion for handling upper limits, please make an issue or start a discussion on the GitHub page.


Uploading the new catalogue to GitHub
-------------------------------------
So others can use this paper's data, you should create `a fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ of the pulsar_spectra,
and the new catalogue files and make a `pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork>`_.
The following are the steps this will require and what you should include in your pull request.

1. Make a fork of pulsar spectra
    Go to the `pulsar_spectra <https://github.com/NickSwainston/pulsar_spectra>`_ repository and fork it by clicking the fork button in the top right.
    Follow the steps until you are on the webpage with your fork (the URL should look like https://github.com/yourusername/pulsar_spectra).

2. Clone your fork
    From your fork webpage, click the code button and copy the clone URL.
    In your terminal, go to a directory where you would like to put the code and run the command

    :code:`git clone <copied url here>`

    The :code:`pulsar_spectra` directory it creates is where you should be working on your changes.

3. Add each paper
    For each paper, perform the following sub-steps

    a. Create the YAML paper file
        Follow the steps in the :ref:`added to the catalogue <adding_papers>` section,
        will make a YAML file in the directory :code:`pulsar_spectra/catalogue_papers/`.

    b. Update ADS links
        In the :code:`pulsar_spectra/catalogue.py`, there is a dictionary called :code:`ADS_REF` (currently on line 25).
        Add a new line to this dictionary by making the key "Author_year" and the link to the ADS abstract page for the paper.
        So the format is:

        :code:`"Author_year": "adslink",`

    c. Commit the changed files
        First, you must add the new YAML file and the updated ADS ref like so (changing the command for your file):

        :code:`git add pulsar_spectra/catalogue_papers/<AUTHOR_YEAR>.yaml pulsar_spectra/catalogue.py`

        Then make a commit describing your changes:

        :code:`git commit -m "Added <AUTHOR_YEAR> to the catalogue.`

        Feel free to add a brief description of the paper if you'd like.

4. Create a pull request
    Once you have finished adding to the repo, you can push your changes to your GitHub fork using:

    :code:`git push`

    Then go to your GitHub pulsar_spectra fork webpage and click on "Pull requests", and then "Create pull request"
    (It may have prompted you to make a pull request already).

    What we want (and what should happen by default) is the pull request will say something like this:

    :code:`base respository:NickSwainston/pulsar_spectra  base:main   <-   head respository:YOURUSERNAME/pulsar_spectra  base:main`

    Write a description of the changes you have made and click submit.

5. Wait for approval
    The maintainers will review your changes, run some of the tests and either help you fix any errors or fix them on your behalf.
    Once the pull request is fixed and tested, it will be merged into the main branch so everyone can use it.

6. Celebrate!
    Pat yourself on the back for contributing to open-source software!
    You should now see yourself listed under the contributors to the repository.


Catalogue format
----------------

The catalogue is made up of YAML files of each paper. The format of the YAML files is:

.. code-block:: python

    {
        "Pulsar Jname": {
            "Frequency MHz":    ["List of frequencies in MHz"],
            "Flux Density mJy": ["List of flux densities in mJy"],
            "Flux Density error mJy": ["List of flux density uncertainties in mJy"]
        }
    }

For example:

.. code-block:: python

    {
        "J0030+0451": {
            "Frequency MHz": [150.0, 180.0],
            "Flux Density mJy": [ 37.6, 32.4],
            "Flux Density error mJy": [ 4.4, 3.2]
        },
        "J0034-0534": {
            "Frequency MHz": [150.0],
            "Flux Density mJy": [202.8],
            "Flux Density error mJy": [7.9]
        },
    }
