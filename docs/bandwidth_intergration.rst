Bandwidth Intergration
======================

Pulsar spectral fitting often assumes that the reported average flux densities are currently treated as
the flux density at one specific (usually central) frequency, whereas in reality, they are averaged over some finite bandwidth.
This assumption becomes increasingly inaccurate for wider fractional bandwidths.
For this reason we have expanded the catalogue's database to include the bandwidth of all detections and
expanded our equations to model the integrated flux across the band.

Derivations
-----------
If \alpha measurement is reported along with \alpha bandwidth, then the correct way to fit models is to find the expected mean flux across the band for each model,

.. math::

    S_{avg} = \frac{1}{\rm{BW}} \int_{\nu_\text{min}}^{\nu_\text{min}} S_v\,\text{d}\nu,

where :math:`\rm{BW} = \nu_\text{min} - \nu_\text{min}`.
The evaluation of this expression for each model follows.

How to use sympy to help with derivations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`Sympy <https://docs.sympy.org/latest/index.html>`_ is an excellent tool for performing differentation and simple intergration like so:

.. code::

    v, vpeak, a, c, beta, v0 = symbols('v vpeak \alpha c beta v0')
    f = c * (v/v0)^a * exp( \alpha / beta * (v/vpeak)^(-beta) )
    f2 = f.diff(v).diff(v).simplify()

Which will output the second differentatial:

.. code::

    a*c*(v/v0)^a*(v/vpeak)^(-2*(a + (v/vpeak)^(2*(a - 1) + (v/vpeak)^beta*(-2*a + beta + 1))*exp(a*(v/vpeak)^(-beta)/beta)/v^2

Intergration Derivations
------------------------


Simple power law
~~~~~~~~~~~~~~~~

.. math::

    \Sv &= c \left( \frac{\nu}{\nu_0} \right)^\alpha, \\
    \Savg &= \frac{1}{\BW} \int_\vmin^\vmax c \left( \frac{\nu}{\nu_0} \right)^\alpha \,\text{d}\nu, \\
    &= \frac{\nu_0}{\BW} \left[\frac{c}{\alpha+1} \left(\frac{\nu}{\nu_0}\right)^{\alpha + 1}  \right]_\vmin^\vmax \\
    &= \frac{\nu_0}{\BW} \frac{c}{\alpha+1} \left( \left(\frac{\vmax}{\nu_0}\right)^{\alpha + 1} - \left(\frac{\vmin}{\nu_0}\right)^{\alpha + 1} \right) \\
    &= \frac{c(\vmax^{\alpha+1} - \vmin^{\alpha+1})}{\BW\,\nu_0^\alpha(\alpha+1)}.

Broken power law
~~~~~~~~~~~~~~~~

.. math::

    \Sv &= c\begin{cases}
            \left( \frac{\nu}{\nu_0} \right)^{\alpha_1}   & \mathrm{if}\: \nu \leq \vb \\[5pt]
            \left( \frac{\nu}{\nu_0} \right)^{\alpha_2} \left( \frac{\vb}{\nu_0} \right)^{\alpha_1-\alpha_2} & \mathrm{otherwise} \\
        \end{cases}.


If :math:`\vmin < \vmax \le\vb`, then :math:`\Savg` is identical to the simple power law with the substitution :math:`\alpha \leftarrow \alpha_1`:

.. math::

    \Savg = \frac{c(\vmax^{\alpha_1+1} - \vmin^{\alpha_1+1})}{\BW\,\nu_0^{\alpha_1}(\alpha_1+1)}.

If both :math:`\vb \le \vmin < \vmax`, then

.. math::

    \Savg = \frac{c(\vmax^{\alpha_2+1} - \vmin^{\alpha_2+1})}{\BW\,\nu_0^{\alpha_2}(\alpha_2+1)} \left( \frac{\vb}{\nu_0} \right)^{\alpha_1-\alpha_2}.


In the final case, when :math:`\vmin < \vb < \vmax`,

.. math::

    \Savg = \frac{c(\vb^{\alpha_1+1} - \vmin^{\alpha_1+1})}{(\vb - \vmin)\,\nu_0^{\alpha_1}(\alpha_1+1)} + \frac{c(\vmax^{\alpha_2+1} - \vb^{\alpha_2+1})}{(\vmax - \vb)\,\nu_0^{\alpha_2}(\alpha_2+1)} \left( \frac{\vb}{\nu_0} \right)^{\alpha_1-\alpha_2}.


Log-parabolic spectrum
~~~~~~~~~~~~~~~~~~~~~~

.. math::

    \log_{10} \Sv
        &= \alpha  \left [ \log_{10} \left ( \frac{\nu}{\nu_0} \right ) \right]^2 +
            b \, \log_{10} \left ( \frac{\nu}{\nu_0} \right ) + c \\
    \Sv &= 10^{a  \left [ \log_{10} \left ( \frac{\nu}{\nu_0} \right ) \right]^2 + b \, \log_{10} \left ( \frac{\nu}{\nu_0} \right ) + c} \\
    &= e^{\ln 10 \left(a  \left [ \log_{10} \left ( \frac{\nu}{\nu_0} \right ) \right]^2 + b \, \log_{10} \left ( \frac{\nu}{\nu_0} \right ) + c\right)} \\
    &= Ce^{\ln 10 \left(a  \left [ \log_{10} \left ( \frac{\nu}{\nu_0} \right ) \right]^2 + b \, \log_{10} \left ( \frac{\nu}{\nu_0} \right )\right)},


where :math:`C = e^{c\ln 10} = 10^c`.

.. math::

    \Sv &= Ce^{\ln 10 \left(a  \left [ \frac{\ln\left ( \frac{\nu}{\nu_0} \right )}{\ln 10} \right]^2 + b \, \frac{\ln \left ( \frac{\nu}{\nu_0} \right )}{\ln 10}\right)} \\
    &= Ce^{\left(\frac{a}{\ln 10}  \left [ \ln\left ( \frac{\nu}{\nu_0} \right )\right]^2 + b \, \ln \left ( \frac{\nu}{\nu_0} \right )\right)}.


In this form, the integration becomes \emph{slightly} easier (at least, WolframAlpha gives an answer!):

.. math::

    \int e^{A(\ln x)^2 + B\ln x}\,\text{d}x
        = \frac{\sqrt{\pi} e^{-\frac{(B+1)^2}{4A}} \text{erfi} \left(\frac{2A\ln x + B + 1}{2\sqrt{A}}\right)}{2\sqrt{A}}.


In our case, this works out to

.. math::

    \Savg &=
        \frac{1}{\BW}\int_\vmin^\vmax Ce^{\left(\frac{a}{\ln 10}  \left [ \ln\left ( \frac{\nu}{\nu_0} \right )\right]^2 + b \, \ln \left ( \frac{\nu}{\nu_0} \right )\right)}\,\text{d}\nu \\
        &= \frac{C\nu_0}{2\BW} \sqrt{\frac{\pi \ln 10}{a}} \, 10^{-\frac{(b+1)^2}{4a}} \left[\text{erfi} \left(\frac{2a\ln \left(\frac{\nu}{\nu_0}\right) + b + 1}{2\sqrt{a\ln 10}}\right)\right]_\vmin^\vmax.


Power law with high-frequency cut-off
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

    \Sv &= c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \left ( 1 - \frac{\nu}{\nu_c} \right ),\qquad \nu < \nu_c, \\
    \Savg &= \frac{1}{\BW} \int_\vmin^\vmax c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \left ( 1 - \frac{\nu}{\nu_c} \right ) \,\text{d}\nu \\
    &= -\frac{c}{\BW \nu_0^\alpha} \left[ \frac{\nu^{\alpha + 1}}{\alpha + 1} + \frac{\nu^{\alpha + 2}}{\nu_c (\alpha + 2)}\right]_\vmin^\vmax \\
    &= -\frac{c}{\BW \nu_0^\alpha} \left( \frac{\vmax^{\alpha + 1} - \vmin^{\alpha + 1}}{\alpha + 1} + \frac{\vmax^{\alpha + 2} - \vmin^{\alpha + 2}}{\nu_c (\alpha + 2)}\right ) \\


sympy solution:

.. code::

    Piecewise((-c*v0**2*(v*log(v) + vc)/(v*vc), Eq(a, -2)), (c*v0*(-v + vc*log(v))/vc, Eq(a, -1)), (c*v*(v/v0)**a*(-a*v + a*vc - v + 2*vc)/(vc*(a**2 + 3*a + 2)), True))

.. math::

    \Savg &=  \left( \frac{c \nu}{\BW\nu_c} \right) \left ( \frac{\nu}{\nu_0} \right)^ \alpha \left ( \frac{- \alpha  \nu +  \alpha  \nu_c -  \nu + 2  \nu_c}{ (\alpha + 1)(\alpha + 2)} \right)\\


Power law with low-frequency turn-over
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

    \Sv = c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_c} \right)^{-\beta} \right ].


Again with \alpha little help from WolframAlpha, defining

.. math::

    X &= \left( \frac{\nu}{\nu_0} \right)^{\alpha}, \\
    Y &= -\frac{\alpha}{\beta} \left( \frac{\nu}{\nu_c} \right)^{-\beta}, \\
    Z &= -\frac{\alpha + 1}{\beta},

we have

.. math::

    \Savg &= \frac{1}{\BW} \int_\vmin^\vmax cX e^{-Y} \,\text{d}\nu \\
        &= \frac{c}{\BW}\left[\frac{\nu X Y^{-Z}}{\beta} \Gamma(Z, Y) \right]_\vmin^\vmax,

where :math:`\Gamma(a,x)`` is the incomplete gamma function.

Double turn-over spectrum
~~~~~~~~~~~~~~~~~~~~~~~~~


.. math::

    \Sv = c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_{peak}} \right)^{-\beta} \right ] \left ( 1 - \frac{\nu}{\nu_c} \right ) ,\qquad \nu < \nu_c,


.. math::

    \Savg
    &= \frac{c}{\BW}\int_\vmin^\vmax \left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_{peak}} \right)^{-\beta} \right ] \left ( 1 - \frac{\nu}{\nu_c} \right )\,\text{d}\nu \\
    &=
        \frac{c}{\BW} \int_\vmin^\vmax \left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \,\text{d}\nu \left( \frac{\nu}{\nu_{peak}} \right)^{-\beta} \right ] \,\text{d}\nu -
        \frac{c}{\BW} \int_\vmin^\vmax \left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \,\text{d}\nu \left( \frac{\nu}{\nu_{peak}} \right)^{-\beta} \right ] \frac{\nu}{\nu_c} \,\text{d}\nu \\
    &=
        \frac{c}{\BW} \int_\vmin^\vmax Xe^{-Y} \,\text{d}\nu -
        \frac{c\nu_0}{\BW\,\nu_c} \int_\vmin^\vmax X^\prime e^{-Y} \,\text{d}\nu \\
    &=
        \frac{c}{\BW}\left[\frac{\nu X Y^{-Z}}{\beta} \Gamma(Z, Y) \right]_\vmin^\vmax -
        \frac{c\nu_0}{\BW\,\nu_c}\left[\frac{\nu X^\prime Y^{-Z^\prime}}{\beta} \Gamma(Z^\prime, Y) \right]_\vmin^\vmax,

where

.. math::

    X &= \left( \frac{\nu}{\nu_0} \right)^{\alpha}, &
    Y &= -\frac{\alpha}{\beta} \left( \frac{\nu}{\nu_c} \right)^{-\beta}, &
    Z &= -\frac{\alpha + 1}{\beta}, \\
    X^\prime &= \left( \frac{\nu}{\nu_0} \right)^{\alpha+1}, &
    & &
    Z^\prime &= -\frac{\alpha + 2}{\beta},


Taylor Expansion Derivations
----------------------------

Some of the above integrals involve functions that may be tricky to implement in practice.
The following Taylor expansions allow for easier implementation, at the cost of accuracy for wideband measurements.
Here, we derive Taylor expansions about an arbitrary "centre" frequency, :math:`\vctr` :

    \Sv \approx \Svctr + \Svctr^\prime(\nu - \vctr) + \frac{1}{2} \Svctr^{\prime\prime}(\nu - \vctr)^2 + \frac{1}{6} \Svctr^{\prime\prime\prime}(\nu - \vctr)^3 + \cdots


where :math:`\Svctr^{(n)} = S^{(n)}(\vctr)` is shorthand for the :math:`n` th derivative of :math:`\Sv` with respect to frequency, evaluated at :math:`\vctr` .

In general, the bandwidth integral will then be

.. math::

    \Savg
        &\approx \frac{1}{\BW} \int_\vmin^\vmax \Sv\,\text{d}\nu \\
        &\approx \frac{1}{\BW} \int_\vmin^\vmax \left(
            \Svctr + \Svctr^\prime(\nu - \vctr) + \frac{1}{2} \Svctr^{\prime\prime}(\nu - \vctr)^2 + \frac{1}{6} \Svctr^{\prime\prime\prime}(\nu - \vctr)^3 + \cdots
            \right)\,\text{d}\nu \\
        &\approx \frac{1}{\BW} \left[
            \Svctr\nu + \frac{\Svctr^\prime}{2}(\nu - \vctr)^2 + \frac{\Svctr^{\prime\prime}}{3}(\nu - \vctr)^3 +
            \frac{\Svctr^{\prime\prime\prime}}{4}(\nu - \vctr)^4 + \cdots
            \right]_\vmin^\vmax \\
        &\approx \frac{1}{\BW} \left(
            2\Svctr\left(\frac{\BW}{2}\right) + \frac{2\Svctr^{\prime\prime}}{3}\left(\frac{\BW}{2}\right)^3 + \cdots
            \right) \\
        &= \Svctr + \frac{\Svctr^{\prime\prime}}{3}\left(\frac{\BW}{2}\right)^2 +
            \cdots


We see that every other term cancels (due to the symmetry of the integrand), and the final sum is therefore

.. math::

    \Savg = \sum_{k=0}^\infty \frac{\Svctr^{(2k)}}{2k+1}\left(\frac{\BW}{2}\right)^{2k}.


This formula can then be simply implemented for each model by computing its ``even'' derivatives.
This is done for each model in the following subsections.

[To-do: Calculate the residual error for \alpha given truncation, for each of the models. Also need to consider the radius of convergence (esp. for models that are defined with cut-off frequencies).]

Simple power law
~~~~~~~~~~~~~~~~

.. math::

    \Sv &= c \left( \frac{\nu}{\nu_0} \right)^\alpha \\
    \Sv^\prime
        &= \alpha c \frac{\nu^{\alpha - 1}}{\nu_0^\alpha}
         = \frac{\alpha\Sv}{\nu} \\
    \Sv^{\prime\prime}
        &= \alpha(\alpha - 1) c \frac{\nu^{\alpha - 2}}{\nu_0^\alpha}
         = \frac{\alpha(\alpha - 1)\Sv}{\nu^2} \\
    &\vdots \notag \\
    \Sv^{(k)}
        &= \frac{\alpha!}{(\alpha - k)!}\frac{\Sv}{\nu^k}



Broken power law
~~~~~~~~~~~~~~~~

This one is too awkward to do using \alpha Taylor expansion, I reckon.

Log-parabolic spectrum
~~~~~~~~~~~~~~~~~~~~~~

For brevity, I will use the shorthands

.. math::

    X &\equiv 2a\log_{10} \left ( \frac{\nu}{\nu_0} \right ) + b, \\
    Y &\equiv \frac{2a}{\ln 10}.


Note that

.. math::

    X^\prime = \frac{2a}{\nu \ln 10} = \frac{Y}{\nu}
    \qquad\text{and}\qquad
    Y^\prime = 0.


The first four derivatives are:

.. math::

    \log_{10} \Sv
        &= \alpha  \left [ \log_{10} \left ( \frac{\nu}{\nu_0} \right ) \right]^2 +
            b \, \log_{10} \left ( \frac{\nu}{\nu_0} \right ) + c \\
    \frac{\Sv^\prime}{\Sv\ln10}
        &= \left(2a\log_{10} \left ( \frac{\nu}{\nu_0} \right ) + b\right)
            \left( \frac{1}{\nu\ln 10}\right)
         = \frac{X}{\nu\ln 10} \\
    \Sv^\prime
        &= \frac{\Sv X}{\nu} \\
    \Sv^{\prime\prime}
        &=
            \frac{\Sv^\prime X}{\nu} -
            \frac{\Sv X}{\nu^2} +
            \frac{\Sv X^\prime}{\nu} \\
        &= \frac{\Sv}{\nu^2}\left( X^2 - X + Y \right) \\
    \Sv^{\prime\prime\prime}
        &= \frac{\Sv^\prime}{\nu^2}\left( X^2 - X + Y \right) -
            \frac{2\Sv}{\nu^3}\left( X^2 - X + Y \right) +
            \frac{\Sv}{\nu^2}\left( 2XX^\prime - X^\prime \right) \\
        &= \frac{\Sv}{\nu^3}\left( X^3 - 3X^2 + 3XY + 2X - 3Y \right) \\
    \Sv^{\prime\prime\prime\prime}
        &= \frac{\Sv^\prime}{\nu^3}\left( X^3 - 3X^2 + 3XY + 2X - 3Y \right) -{} \\
            &\qquad\frac{3\Sv}{\nu^4}\left( X^3 - 3X^2 + 3XY + 2X - 3Y \right) +{} \\
            &\qquad\frac{\Sv}{\nu^3}\left( 3X^2X^\prime - 6XX^\prime + 3X^\prime Y + 2X^\prime \right) \\
        &= \frac{\Sv}{\nu^4}\left( X^4 - 6X^3 + 6X^2 Y + 11X^2 - 18XY - 6X + 11Y + 3Y^2 \right)



Power law with high-frequency cut-off
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This one is really just the sum of two simple power laws:

.. math::

    \Sv
        &= c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \left ( 1 - \frac{\nu}{\nu_c} \right ), \\
        &= c\left( \frac{\nu}{\nu_0} \right)^{\alpha} - \frac{c\nu_0}{\nu_c}\left( \frac{\nu}{\nu_0} \right)^{\alpha + 1}.


The derivatives are:

.. math::

    \Sv^{(k)}
        = \frac{c}{\nu_0^k} \frac{\alpha!}{(\alpha - k)!}
            \left(\frac{\nu}{\nu_0}\right)^{\alpha - k}\left(1 - \frac{\nu}{\nu_c}\right) -
            \frac{kc}{\nu_0^{k-1}\nu_c} \frac{\alpha!}{(\alpha - k + 1)!}
            \left(\frac{\nu}{\nu_0}\right)^{\alpha - k + 1}


A new attempt

.. math::

    \Sv
        &= c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \left ( 1 - \frac{\nu}{\nu_c} \right ), \\
        &= \left( \frac{c}{\nu_0^{\alpha}} \right ) \left (\nu^{\alpha} - \frac{\nu^{\alpha + 1}}{\nu_c} \right).

Deratives we need are:

.. math::

    \Sv^{\prime\prime}
       &= \left( \frac{c \alpha }{\nu_0^{\alpha}} \right )
          \left(
            (\alpha - 1) \nu^{\alpha -2} -
            \frac{(\alpha+1) \nu^{\alpha -1}}{\nu_c}
          \right)\\
    \Sv^{\prime\prime\prime\prime}
       &= \left( \frac{c \alpha (\alpha - 1) (\alpha - 2) }{\nu_0^{\alpha}} \right )
          \left(
            (\alpha - 3) \nu^{\alpha - 4} -
            \frac{(\alpha+1) \nu^{\alpha -3}}{\nu_c}
          \right) \\
     \Sv^{\prime\prime\prime\prime\prime\prime}
       &= \left( \frac{c
                 \alpha (\alpha - 1) (\alpha - 2) (\alpha - 3) (\alpha - 4) }
                 {\nu_0^{\alpha}} \right )
          \left(
            (\alpha - 5) \nu^{\alpha - 6} -
            \frac{(\alpha+1) \nu^{\alpha -5}}{\nu_c}
          \right)


Power law with low-frequency turn-over
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shorthands:

.. math::

    X &= \left( \frac{\nu}{\nu_c} \right)^{-\beta} &
    Y &= 1 - X \\
    X^\prime
        &= -\frac{\beta}{\nu_c} \left( \frac{\nu}{\nu_c} \right)^{-\beta - 1}
         = -\frac{\beta X}{\nu} &
    Y^\prime
        &= -X^\prime
         = \frac{\beta X}{\nu}


Derivatives:


.. math::

    \Sv^\prime
        &= \frac{c\alpha}{\nu_0} \left( \frac{\nu}{\nu_0} \right)^{\alpha - 1} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_c} \right)^{-\beta} \right ] +
            c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_c} \right)^{-\beta} \right ] \left(-\frac{\alpha}{\nu_c} \left( \frac{\nu}{\nu_c} \right)^{-\beta - 1} \right) \\
        &= \frac{\alpha \Sv}{\nu} - \frac{\alpha \Sv}{\nu_c} \left( \frac{\nu}{\nu_c} \right)^{-\beta - 1} \\
        &= \frac{\alpha \Sv}{\nu}\left( 1 - \left( \frac{\nu}{\nu_c} \right)^{-\beta} \right)
         = \frac{\alpha \Sv}{\nu}\left( 1 - X \right)
         = \frac{\alpha \Sv Y}{\nu}



.. math::

    \Sv^{\prime\prime}
        &= \frac{\alpha \Sv^\prime Y}{\nu} -
            \frac{\alpha \Sv Y}{\nu^2} +
            \frac{\alpha \Sv Y^\prime}{\nu} \\
        &= \frac{\alpha^2 \Sv Y^2}{\nu^2} -
            \frac{\alpha \Sv Y}{\nu^2} +
            \frac{\alpha \beta \Sv X}{\nu^2} \\
        &= \frac{\alpha \Sv}{\nu^2} \left [ \alpha Y^2 - Y + \beta X \right ]



.. math::

    \Sv^{\prime\prime\prime}
        &=
            \frac{\alpha\Sv^\prime}{\nu^2}\left [ \alpha Y^2 - Y + \beta X \right ] -
            \frac{2\alpha\Sv}{\nu^3}\left [ \alpha Y^2 - Y + \beta X \right ] + \frac{\alpha\Sv}{\nu^2}\left [ 2\alpha Y Y^\prime - Y^\prime + \beta X^\prime \right ] \\
        &=
            \frac{\alpha\Sv}{\nu^3}\alpha Y \left [ \alpha Y^2 - Y + \beta X \right ] -
            \frac{\alpha\Sv}{\nu^3}2\left [ \alpha Y^2 - Y + \beta X \right ] + \frac{\alpha\Sv}{\nu^3}\left [ 2\alpha Y - 1 - \beta \right ] \beta X \\
        &=
            \frac{\alpha\Sv}{\nu^3}\bigg( \alpha^2 Y^3 - 3\alpha Y^2 + (3\alpha\beta X + 2)Y - \beta X(3 + \beta)
            \bigg)


Shorthands:

.. math::

    X = \left( \frac{\nu}{\nu_{peak}} \right)^{\beta}


.. math::

    \Sv &=
        c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_c} \right)^{-\beta} \right ].\\
    \Sv^{\prime\prime}
        &= \left(\frac{\alpha c}{\nu^2}\right)
           \left (\frac{\nu}{v0} \right)^\alpha
           \left(\frac{\nu}{\nu_{peak}} \right)^{-2 \beta}
           \left[\alpha +
                \left(\frac{\nu}{\nu_{peak}} \right)^{2*\beta} (\alpha - 1) +
                \left(\frac{\nu}{\nu_{peak}} \right)^{\beta} (-2\alpha + \beta +
                1)\right]
            \exp\left[\left(\frac{\alpha}{\beta} \right) \left(\frac{\nu}{\nu_{peak}} \right)^{-\beta}\right]\\
        &= \Sv \left(\frac{\alpha}{\nu^2}\right) X^{-2} \left[\alpha + X^{2} (\alpha - 1) + X (-2\alpha + \beta + 1)\right]\\
    \Sv^{\prime\prime\prime\prime}
        &=
        \Sv \left(\frac{\alpha}{\nu^4}\right)
           X^{-4}
           \bigg [
            X^4 (
                + \alpha^3
                - 6 \alpha^2
                + 11 \alpha
                - 6
            ) +  \dots\\
            &\dots
            X^3 (
                - 4 \alpha^3
                + 6 \alpha^2 \beta
                + 18 \alpha^2
                - 4 \alpha  \beta^2
                - 18 \alpha  \beta
                - 22 \alpha
                + \beta^3
                + 6 \beta^2
                + 11 \beta
                + 6
            ) +  \dots\\
            &\dots
            X^2 \alpha (
                + 6 \alpha^2
                - 12 \alpha \beta
                - 18 \alpha
                + 7 \beta^2
                + 18 \beta
                + 11
            ) +  \dots\\
            &\dots
            X \alpha^2 (
                - 4 \alpha
                + 6 \beta
                + 6
            )
            + \alpha^3
            \bigg ]\\
    \Sv^{\prime\prime\prime\prime\prime\prime}
        &=
        \Sv \left(\frac{\alpha}{\nu^6}\right) X^{-6}
        \bigg [
            X^6 (
                + \alpha^5
                - 15 \alpha^4
                + 85 \alpha^3
                - 225 \alpha^2
                + 274 \alpha
                - 120
            ) + \dots\\
            &\dots
            X^5 (
                - 6 \alpha^5
                + 15 \alpha^4 \beta
                + 75 \alpha^4
                - 20 \alpha^3  \beta^2
                - 150 \alpha^3 \beta
                - 340 \alpha^3
                + 15 \alpha^2  \beta^3
                + 150 \alpha^2  \beta^2
                + 510 \alpha^2 \beta
                + 675 \alpha^2
            \dots\\
            &\dots
                - 6 \alpha  \beta^4
                - 75 \alpha  \beta^3
                - 340 \alpha  \beta^2
                - 675 \alpha \beta
                - 548 \alpha
                +  \beta^5
                + 15  \beta^4
                + 85  \beta^3
                + 225  \beta^2
                + 274 \beta
                + 12
            ) + \dots\\
            &\dots
            X^4 \alpha (
                + 15 \alpha^4
                - 60 \alpha^3 \beta
                - 150 \alpha^3
                + 105 \alpha^2  \beta^2
                + 450 \alpha^2 \beta
                + 510 \alpha^2
                - 90 \alpha  \beta^3
                - 525 \alpha  \beta^2
                - 1020 \alpha \beta
                - 675 \alpha
                + 31  \beta^4
                + 225  \beta^3
                + 595  \beta^2
                + 675 \beta
                + 274
            ) + \dots\\
            &\dots
            X^3 \alpha^2 (
                - 20 \alpha^3
                + 90 \alpha^2 \beta
                + 150 \alpha^2
                - 150 \alpha  \beta^2
                - 450 \alpha \beta
                - 340 \alpha
                + 90  \beta^3
                + 375  \beta^2
                + 510 \beta
                + 225
            ) + \dots\\
            &\dots
            X^2 \alpha^3 (
                + 15 \alpha^2
                - 60 \alpha \beta
                - 75 \alpha
                + 65   \beta^2
                + 150 \beta
                + 85
            ) + \dots\\
            &\dots
            X \alpha^4 (
                - 6 \alpha
                + 15 \beta
                + 15
            )
            + \alpha^5
        \bigg ]



Double turn over
~~~~~~~~~~~~~~~~
Shorthands:

.. math::

    X &= \left( \frac{\nu}{\nu_{peak}} \right)^{\beta} \\
    Y &= (\nu -\nu_c)\\
    Z &= c\left(\frac{\nu}{\nu_0}\right)^\alpha \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_{peak}} \right)^{-\beta} \right ]



.. math::

    \Sv &=
        c\left( \frac{\nu}{\nu_0} \right)^{\alpha} \exp\left [ \frac{\alpha}{\beta} \left( \frac{\nu}{\nu_{peak}} \right)^{-\beta} \right ] \left ( 1 - \frac{\nu}{\nu_c} \right )\\
    \Sv^{\prime\prime}
        &=  Z \frac{\alpha}{\nu^2\nu_c X^2} (-\alpha Y - 2\nu X^2 + 2\nu X + X^2(1 - \alpha) Y + X Y(2\alpha - \beta - 1))\\
    \Sv^{\prime\prime\prime\prime} &=
        Z
        \frac{\alpha}{X^4\nu^4\nu_c}
        \bigg  [
        X^4 (
            \nu (
                - \alpha^3
                + 2 \alpha^2
                + \alpha
                - 2
            ) +
            \nu_c (
                \alpha^3
                - 6 \alpha^2
                + 11 \alpha
                - 6
            )
        ) + \dots\\
        &\dots
        X^3 (
            \nu (
                4 \alpha^3
                - 6 \alpha^2 \beta
                -6 \alpha^2
                + 4 \alpha \beta^2
                + 6 \alpha \beta
                - 2 \alpha
                - \beta^3
                - 2 \beta^2
                + \beta
                + 2
            ) +
            \dots\\
            &\dots
            \nu_c (
                - 4 \alpha^3
                + 6 \alpha^2 \beta
                + 18 \alpha^2
                - 4 \alpha \beta^2
                - 18 \alpha \beta
                - 22 \alpha
                + \beta^3
                + 6 \beta^2
                + 11 \beta
                + 6
            )
        ) + \dots\\
        &\dots
        X^2 \alpha (
            \nu (
                - 6 \alpha^2
                + 12 \alpha \beta
                + 6 \alpha
                - 7 \beta^2
                - 6 \beta
                + 1
            ) +
            \nu_c (
                6 \alpha^2
                - 12 \alpha \beta
                - 18 \alpha
                + 7\beta^2
                + 18 \beta
                + 11
            )
        ) + \dots\\
        &\dots
        X \alpha^2(
            \nu (
                4 \alpha
                - 6 \beta
                - 2
            ) +
            \nu_c (
                - 4 \alpha
                + 6 \beta
                + 6
            )
        ) + \dots\\
        &\dots
             \alpha^3 \nu_c
            - \alpha^3 \nu
        \bigg ]

