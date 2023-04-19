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
You can install via pip using
`pip install pulsar_spectra` (stable)

Or you can clone or download the repository and then use `python setup.py install` or `pip install .`

There is also a docker container that you can install with `docker pull nickswainston/pulsar_spectra`.


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
