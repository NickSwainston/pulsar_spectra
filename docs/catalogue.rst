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

    from pulsar_spectra.catalogues import collect_catalogue_fluxes
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

    cat_dict = collect_catalogue_fluxes(exclude=["Murphy_2017", "Xue_2017"])


.. _cat_papers:
Papers included in our catalogue
--------------------------------

.. csv-table:: Papers included in our catalogue
    :header: "Paper","Link"

    "ATNF pulsar catalogue","`Catalogue website <https://www.atnf.csiro.au/research/pulsar/psrcat/>`_"
    "Sieber (1973)","`ADS <https://ui.adsabs.harvard.edu/abs/1973A%26A....28..237S/abstract>`_"
    "Bartel et al. (1978)","`ADS <https://ui.adsabs.harvard.edu/abs/1978A%26A....68..361B/abstract>`_"
    "Izvekova et al. (1981)","`ADS <https://ui.adsabs.harvard.edu/abs/1981Ap%26SS..78...45I/abstract>`_"
    "Lorimer et al. (1995)","`ADS <https://ui.adsabs.harvard.edu/abs/1995MNRAS.273..411L/abstract>`_"
    "van Ommen et al. (1997)","`ADS <https://ui.adsabs.harvard.edu/abs/1997MNRAS.287..307V/abstract>`_"
    "[Maron et al. (2000)","`ADS <https://ui.adsabs.harvard.edu/abs/2000A%26AS..147..195M/abstract>`_"
    "Malofeev et al. (2000)","`ADS <https://ui.adsabs.harvard.edu/abs/2000ARep...44..436M/abstract>`_"
    "Karastergiou et al. (2005)","`ADS <https://ui.adsabs.harvard.edu/abs/2005MNRAS.359..481K/abstract>`_"
    "Johnston et al. (2006)","`ADS <https://ui.adsabs.harvard.edu/abs/2006MNRAS.369.1916J/abstract>`_"
    "Kijak et al. (2007)","`ADS <https://ui.adsabs.harvard.edu/abs/2007A%26A...462..699K/abstract>`_"
    "Keith et al. (2011)","`ADS <https://ui.adsabs.harvard.edu/abs/2011MNRAS.416..346K/abstract>`_"
    "Bates et al. (2011)","`ADS <https://ui.adsabs.harvard.edu/abs/2011MNRAS.411.1575B/abstract>`_"
    "Kijak et al. (2011)","`ADS <https://ui.adsabs.harvard.edu/abs/2011A%26A...531A..16K/abstract>`_"
    "Zakharenko et al. (2013)","`ADS <https://ui.adsabs.harvard.edu/abs/2013MNRAS.431.3624Z/abstract>`_"
    "Dai et al. (2015)","`ADS <https://ui.adsabs.harvard.edu/abs/2015MNRAS.449.3223D/abstract>`_"
    "Basu et al. (2016)","`ADS <https://ui.adsabs.harvard.edu/abs/2016MNRAS.458.2509B/abstract>`_"
    "Bell et al. (2016)","`ADS <https://ui.adsabs.harvard.edu/abs/2016MNRAS.461..908B/abstract>`_"
    "Bilous et al. (2016)","`ADS <https://ui.adsabs.harvard.edu/abs/2016A%26A...591A.134B/abstract>`_"
    "Han et al. (2016)","`ADS <https://ui.adsabs.harvard.edu/abs/2016RAA....16..159H/abstract>`_"
    "Murphy et al. (2017)","`ADS <https://ui.adsabs.harvard.edu/abs/2017PASA...34...20M/abstract>`_"
    "Kijak et al. (2017)","`ADS <https://ui.adsabs.harvard.edu/abs/2017ApJ...840..108K/abstract>`_"
    "Hobbs et al. (2004)","`ADS <https://ui.adsabs.harvard.edu/abs/2004MNRAS.352.1439H/abstract>`_"
    "Johnston et al. 1993","`ADS <https://ui.adsabs.harvard.edu/abs/1993Natur.361..613J/abstract>`_"
    "Stovall et al. (2015)","`ADS <https://ui.adsabs.harvard.edu/abs/2015ApJ...808..156S/abstract>`_"
    "Xue et al. (2017)","`ADS <https://ui.adsabs.harvard.edu/abs/2017PASA...34...70X/abstract>`_"
    "Jankowski et al. (2018)","`ADS <https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.4436J/abstract>`_"
    "Bondonneu et al. (2020)","`ADS <https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..76B/abstract>`_"
    "Johnston et al. (2021)","`ADS <https://ui.adsabs.harvard.edu/abs/2021MNRAS.502.1253J/abstract>`_"


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

Then move to the scripts subdirectory of the repository and run the command:

.. code-block:: bash

    python csv_to_yaml.py --csv your_paper.csv --ref author_year

This will put a YAML file of the paper in pulsar_spectra/catalogue_papers/.
You should then reinstall the software (`python setup.py install`) then run a spectral fit to confirm it worked.

So others can use this paper's data, you should
1. Make a fork of the pulsar_spectra repository
2. Clone your fork
3. Add the new paper YAML file and make a commit
4. Git push to your fork and then make a pull request on GitHub
5. Wait for your pull request to be approved and merged
6. Pat yourself on the back for contributing to open-source software!


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
