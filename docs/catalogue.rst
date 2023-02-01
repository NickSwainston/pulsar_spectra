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

    "ATNF pulsar catalogue","2863","40-150000","`Catalogue website <https://www.atnf.csiro.au/research/pulsar/psrcat/>`_"
    "Bartel et al. (1978)","18","14800-22700","`ADS <https://ui.adsabs.harvard.edu/abs/1978A%26A....68..361B/abstract>`_"
    "Manchester et al. (1978a)","224","40-408","`ADS <https://ui.adsabs.harvard.edu/abs/1978MNRAS.185..409M/abstract>`_"
    "Izvekova et al. (1981)","86","39-102","`ADS <https://ui.adsabs.harvard.edu/abs/1981Ap%26SS..78...45I/abstract>`_"
    "Dewey et al. (1985)","34","390-390","`ADS <https://ui.adsabs.harvard.edu/abs/1985ApJ...294L..25D/abstract>`_"
    "McConnell et al. (1991)","4","610-610","`ADS <https://ui.adsabs.harvard.edu/abs/1991MNRAS.249..654M/abstract>`_"
    "Johnston et al. (1992)","100","640-1577","`ADS <https://ui.adsabs.harvard.edu/abs/1992MNRAS.255..401J/abstract>`_"
    "Wolszczan et al. (1992)","1","430-1400","`ADS <https://ui.adsabs.harvard.edu/abs/1992Natur.355..145W/abstract>`_"
    "Johnston et al. (1993)","1","430-2360","`ADS <https://ui.adsabs.harvard.edu/abs/1993Natur.361..613J/abstract>`_"
    "Manchester et al. (1993)","1","660-660","`ADS <https://ui.adsabs.harvard.edu/abs/1993ApJ...403L..29M/abstract>`_"
    "Camilo et al. (1995)","29","430-430","`ADS <https://ui.adsabs.harvard.edu/abs/1995ApJ...445..756C/abstract>`_"
    "Lundgren et al. (1995)","1","430-1400","`ADS <https://ui.adsabs.harvard.edu/abs/1995ApJ...453..419L/abstract>`_"
    "Nicastro et al. (1995)","1","411-1400","`ADS <https://ui.adsabs.harvard.edu/abs/1995MNRAS.273L..68N/abstract>`_"
    "Qiao et al. (1995)","61","660-1440","`ADS <https://ui.adsabs.harvard.edu/abs/1995MNRAS.274..572Q/abstract>`_"
    "Robinson et al. (1995)","2","436-640","`ADS <https://ui.adsabs.harvard.edu/abs/1995MNRAS.274..547R/abstract>`_"
    "Lorimer et al. (1995b)","280","408-1606","`ADS <https://ui.adsabs.harvard.edu/abs/1995MNRAS.273..411L/abstract>`_"
    "Manchester et al. (1996)","55","436-436","`ADS <https://ui.adsabs.harvard.edu/abs/1996MNRAS.279.1235M/abstract>`_"
    "Zepka et al. (1996)","1","430-1400","`ADS <https://ui.adsabs.harvard.edu/abs/1996ApJ...456..305Z/abstract>`_"
    "van Ommen et al. (1997)","82","800-960","`ADS <https://ui.adsabs.harvard.edu/abs/1997MNRAS.287..307V/abstract>`_"
    "Kramer et al. (1998)","34","1400-1400","`ADS <https://ui.adsabs.harvard.edu/abs/1998ApJ...501..270K/abstract>`_"
    "Toscano et al. (1998)","19","436-1660","`ADS <https://ui.adsabs.harvard.edu/abs/1998ApJ...506..863T/abstract>`_"
    "Kramer et al. (1999)","15","2695-4850","`ADS <https://ui.adsabs.harvard.edu/abs/1999ApJ...526..957K/abstract>`_"
    "Stairs et al. (1999)","19","410-1414","`ADS <https://ui.adsabs.harvard.edu/abs/1999ApJS..123..627S/abstract>`_"
    "Lommen et al. (2000)","3","430-1400","`ADS <https://ui.adsabs.harvard.edu/abs/2000ApJ...545.1007L/abstract>`_"
    "Malofeev et al. (2000)","212","102-102","`ADS <https://ui.adsabs.harvard.edu/abs/2000ARep...44..436M/abstract>`_"
    "Kuzmin et al. (2001)","30","102-111","`ADS <https://ui.adsabs.harvard.edu/abs/2001A%26A...368..230K/abstract>`_"
    "Manchester et al. (2001)","100","1374-1374","`ADS <https://ui.adsabs.harvard.edu/abs/2001MNRAS.328...17M/abstract>`_"
    "Morris et al. (2002)","120","1374-1374","`ADS <https://ui.adsabs.harvard.edu/abs/2002MNRAS.335..275M/abstract>`_"
    "Kramer et al. (2003a)","200","1374-1374","`ADS <https://ui.adsabs.harvard.edu/abs/2003MNRAS.342.1299K/abstract>`_"
    "Hobbs et al. (2004a)","453","1400-1400","`ADS <https://ui.adsabs.harvard.edu/abs/2004MNRAS.352.1439H/abstract>`_"
    "Karastergiou et al. (2005)","48","3100-3100","`ADS <https://ui.adsabs.harvard.edu/abs/2005MNRAS.359..481K/abstract>`_"
    "Johnston et al. (2006)","31","8356-8356","`ADS <https://ui.adsabs.harvard.edu/abs/2006MNRAS.369.1916J/abstract>`_"
    "Lorimer et al. (2006)","142","1374-1374","`ADS <https://ui.adsabs.harvard.edu/abs/2006MNRAS.372..777L/abstract>`_"
    "Kijak et al. (2007)","11","325-1060","`ADS <https://ui.adsabs.harvard.edu/abs/2007A%26A...462..699K/abstract>`_"
    "Stappers et al. (2008)","13","147-147","`ADS <https://ui.adsabs.harvard.edu/abs/2008AIPC..983..593S/abstract>`_"
    "Bates et al. (2011)","18","6591-6591","`ADS <https://ui.adsabs.harvard.edu/abs/2011MNRAS.411.1575B/abstract>`_"
    "Keith et al. (2011)","9","17000-24000","`ADS <https://ui.adsabs.harvard.edu/abs/2011MNRAS.416..346K/abstract>`_"
    "Kijak et al. (2011)","15","610-4850","`ADS <https://ui.adsabs.harvard.edu/abs/2011A%26A...531A..16K/abstract>`_"
    "Zakharenko et al. (2013)","40","20-25","`ADS <https://ui.adsabs.harvard.edu/abs/2013MNRAS.431.3624Z/abstract>`_"
    "Dembska et al. (2014)","19","610-8350","`ADS <https://ui.adsabs.harvard.edu/abs/2014MNRAS.445.3105D/abstract>`_"
    "Dai et al. (2015)","24","730-3100","`ADS <https://ui.adsabs.harvard.edu/abs/2015MNRAS.449.3223D/abstract>`_"
    "Stovall et al. (2015)","36","35-79","`ADS <https://ui.adsabs.harvard.edu/abs/2015ApJ...808..156S/abstract>`_"
    "Basu et al. (2016)","1","325-1280","`ADS <https://ui.adsabs.harvard.edu/abs/2016MNRAS.458.2509B/abstract>`_"
    "Bell et al. (2016)","17","154-154","`ADS <https://ui.adsabs.harvard.edu/abs/2016MNRAS.461..908B/abstract>`_"
    "Bilous et al. (2016)","158","149-149","`ADS <https://ui.adsabs.harvard.edu/abs/2016A%26A...591A.134B/abstract>`_"
    "Frail et al. (2016)","200","147-147","`ADS <https://ui.adsabs.harvard.edu/abs/2016ApJ...829..119F/abstract>`_"
    "Han et al. (2016)","204","1274-1523","`ADS <https://ui.adsabs.harvard.edu/abs/2016RAA....16..159H/abstract>`_"
    "Kondratiev et al. (2016)","48","149-149","`ADS <https://ui.adsabs.harvard.edu/abs/2016A%26A...585A.128K/abstract>`_"
    "Kijak et al. (2017)","12","325-610","`ADS <https://ui.adsabs.harvard.edu/abs/2017ApJ...840..108K/abstract>`_"
    "Mignani et al. (2017)","1","97500-343500","`ADS <https://ui.adsabs.harvard.edu/abs/2017ApJ...851L..10M/abstract>`_"
    "Murphy et al. (2017)","60","76-227","`ADS <https://ui.adsabs.harvard.edu/abs/2017PASA...34...20M/abstract>`_"
    "Xue et al. (2017)","48","185-185","`ADS <https://ui.adsabs.harvard.edu/abs/2017PASA...34...70X/abstract>`_"
    "Jankowski et al. (2018)","441","728-3100","`ADS <https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.4436J/abstract>`_"
    "Johnston et al. (2018)","586","1360-1360","`ADS <https://ui.adsabs.harvard.edu/abs/2018MNRAS.474.4629J/abstract>`_"
    "Jankowski et al. (2019)","205","843-843","`ADS <https://ui.adsabs.harvard.edu/abs/2019MNRAS.484.3691J/abstract>`_"
    "Kaur et al. (2019)","1","81-3100","`ADS <https://ui.adsabs.harvard.edu/abs/2019ApJ...882..133K/abstract>`_"
    "Sanidas et al. (2019)","288","135-135","`ADS <https://ui.adsabs.harvard.edu/abs/2019A%26A...626A.104S/abstract>`_"
    "Xie et al. (2019)","32","1369-1369","`ADS <https://ui.adsabs.harvard.edu/abs/2019RAA....19..103X/abstract>`_"
    "Zhang et al. (2019)","3","768-3968","`ADS <https://ui.adsabs.harvard.edu/abs/2019ApJ...885L..37Z/abstract>`_"
    "Zhao et al. (2019)","71","4820-5124","`ADS <https://ui.adsabs.harvard.edu/abs/2019ApJ...874...64Z/abstract>`_"
    "Bilous et al. (2020)","43","53-63","`ADS <https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..75B/abstract>`_"
    "Bondonneau et al. (2020)","64","53-65","`ADS <https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..76B/abstract>`_"
    "McEwen et al. (2020)","670","350-350","`ADS <https://ui.adsabs.harvard.edu/abs/2020ApJ...892...76M/abstract>`_"
    "Alam et al. (2021)","47","430-2100","`ADS <https://ui.adsabs.harvard.edu/abs/2021ApJS..252....4A/abstract>`_"
    "Bondonneau et al. (2021)","12","50-50","`ADS <https://ui.adsabs.harvard.edu/abs/2021A%26A...652A..34B/abstract>`_"
    "Han et al. (2021)","201","1250-1250","`ADS <https://ui.adsabs.harvard.edu/abs/2021RAA....21..107H/abstract>`_"
    "Johnston et al. (2021)","44","1369-1369","`ADS <https://ui.adsabs.harvard.edu/abs/2021MNRAS.502.1253J/abstract>`_"
    "Kravtsov et al. (2022)","20","24-24","`ADS <https://ui.adsabs.harvard.edu/abs/2022MNRAS.512.4324K/abstract>`_"
    "Lee et al. (2022)","22","70-352","`ADS <https://ui.adsabs.harvard.edu/abs/2022PASA...39...42L/abstract>`_"
    "Spiewak et al. (2022)","189","1284-1284","`ADS <https://ui.adsabs.harvard.edu/abs/2022PASA...39...27S/abstract>`_"


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
