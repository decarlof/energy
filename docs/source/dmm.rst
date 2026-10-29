===
DMM
===

The 2-BM beamline uses a **Double Multilayer Monochromator (DMM)** as
its energy-selection optic in Mono mode. This page collects the DMM
specifications, EPICS motor list, per-energy saved positions, and the
channel-cut energy-calibration procedure — the material previously
scattered across the ``docs2bm-decarlof`` beamline manual
(``item_020``, ``item_021``, ``item_022``) so that it lives alongside
the ``energy`` CLI that drives the DMM.

Content sourced from ``docs2bm-decarlof`` on 2026-07-16 and reproduced
here so the ``energy`` docs are self-contained.


Role in the beamline
====================

The DMM sits downstream of the Y3-30 mirror (M1) and upstream of the
diagnostic flag and B-shutter. It selects the monochromatic X-ray
energy by Bragg reflection off a pair of W–B\ :sub:`4`\ C multilayer
crystals. In **Pink mode** the DMM is retracted (tank Y motors driven
to −10 mm) and the beam bypasses it.

Component summary (from the APS 02-BM reference table):

:Role: Energy selection (monochromatic mode)
:z position: crystal 1 at 29335 mm, crystal 2 at 29934 mm
   (from the centre of the storage-ring straight section; ref 2 =
   centre of optic)
:Y offset: 9.0 mm (crystal 1), 41.0 mm (crystal 2)
:Position tolerance: 250 µm (x, y), 5 mm (z)
:Material: Silicon substrate with W–B\ :sub:`4`\ C multilayer coating
:Inter-crystal spacing: 1323 mm along beam, 765 mm inboard / outboard
:Mounted on: Front-end stand (floor-referenced)
:MEDM screen: ``DMMV.adl`` (running on ``arcturus``)
:EPICS prefix: ``2bma:`` (motors listed below)


Substrate specifications (Si <100>)
===================================

+----------------------------+-------------------------------------------------------------+
| Parameter                  | Value                                                       |
+============================+=============================================================+
| Material                   | Si <100> flat                                               |
+----------------------------+-------------------------------------------------------------+
| Quantity                   | 2 pieces                                                    |
+----------------------------+-------------------------------------------------------------+
| Dimensions                 | 145.57 × 101.60 × 34.04 mm³ ± 0.25 mm                       |
+----------------------------+-------------------------------------------------------------+
| Optical surface            | 140 × 92 mm²                                                |
+----------------------------+-------------------------------------------------------------+
| Spherical radius           | > 20 km                                                     |
+----------------------------+-------------------------------------------------------------+
| Meridional slope error     | 1.0 µrad (rms)                                              |
+----------------------------+-------------------------------------------------------------+
| Sagittal slope error       | 1.0 µrad (rms)                                              |
+----------------------------+-------------------------------------------------------------+
| Microroughness             | ≤ 0.3 nm (rms) HSFR                                         |
+----------------------------+-------------------------------------------------------------+
| HSFR spatial sampling      | 0.004–1 µm                                                  |
+----------------------------+-------------------------------------------------------------+
| Manufacturing note         | Grooves per ANL drawing ``X2-230001-00`` (28 Jan 1998)      |
+----------------------------+-------------------------------------------------------------+


Coating specifications (W–B\ :sub:`4`\ C multilayer)
=====================================================

+---------------------------+----------------------------------------------+
| Parameter                 | Value                                        |
+===========================+==============================================+
| Coating type              | W–B\ :sub:`4`\ C multilayer on Si substrate  |
+---------------------------+----------------------------------------------+
| Adhesion layer            | 5 nm Cr                                      |
+---------------------------+----------------------------------------------+
| Stripe dimension          | 140 × 44 mm²                                 |
+---------------------------+----------------------------------------------+
| Distance between stripes  | 4 mm                                         |
+---------------------------+----------------------------------------------+
| Multilayer period         | 13.8 Å and 24 Å ± <1%                        |
+---------------------------+----------------------------------------------+
| Interface roughness       | 2–3 Å rms                                    |
+---------------------------+----------------------------------------------+
| Number of layer pairs     | 200 / 150                                    |
+---------------------------+----------------------------------------------+
| Gamma (Γ)                 | 0.5                                          |
+---------------------------+----------------------------------------------+

The substrate carries **two multilayer stripes** (13.8 Å and 24 Å
periods, 4 mm apart laterally). Applying Bragg's law
(:math:`\lambda = 2d\sin\theta`) to the saved Bragg-arm angles across
all calibrated Mono energies yields :math:`d \approx 24\,\text{Å}` to
within ~5 %, with no values near 13.8 Å — so the **24 Å stripe is the
currently active one** at 2-BM. The 13.8 Å stripe has never been
calibrated into ``energy2bm.json``; switching to it would be a 4 mm
lateral substrate move plus a separate Mono-mode recalibration of the
Bragg arms and ``M2 Y`` for the new stripe.


Motors
======

.. list-table::
   :header-rows: 1
   :widths: 22 53 25

   * - Description
     - Role
     - EPICS PV
   * - DMM M2 Z
     - Second crystal translation along the beam relative to the first
     - ``2bma:m8``
   * - DMM USX
     - Global tank upstream X
     - ``2bma:m25``
   * - DMM USY OB
     - Global tank upstream Y outboard side
     - ``2bma:m26``
   * - DMM USY IB
     - Global tank upstream Y inboard side
     - ``2bma:m27``
   * - DMM DSX
     - Global tank downstream X
     - ``2bma:m28``
   * - DMM DSY
     - Second crystal Y relative to the first
     - ``2bma:m29``
   * - DMM US Arm
     - Upstream Bragg-arm rotation
     - ``2bma:m30``
   * - DMM DS Arm
     - Downstream Bragg-arm rotation
     - ``2bma:m31``
   * - DMM M2 Y
     - Second crystal Y (companion to ``M2 Z``)
     - ``2bma:m32``

The tank's upstream end carries two independent Y motors
(``USY OB`` and ``USY IB``); their average sets the upstream tank Y
position and their difference produces a Z-tilt around the beam axis.
The second crystal is positioned relative to the first via the
``DSY`` (Y), ``M2 Z`` (along beam), and ``M2 Y`` motors.


Tank / alignment motors (energy-independent within mode)
--------------------------------------------------------

The five DMM tank-positioning motors (``2bma:m25–m29``) are part of
the energy-change coordinated move but do **not** vary per energy;
they take only two configurations, selected by mode:

.. list-table::
   :header-rows: 1
   :widths: 18 14 22 22 24

   * - Motor
     - PV
     - Mono (in beam)
     - Pink (out of beam)
     - Role
   * - ``dmm_usx``
     - ``2bma:m25``
     - 111.0
     - 111.0 (same)
     - Upstream tank lateral X — **fixed alignment** (NOT a stripe
       selector; the value is identical in Mono and Pink)
   * - ``dmm_usy_ob``
     - ``2bma:m26``
     - 0.0
     - -10.0
     - Upstream tank Y outboard — in-beam vs retracted
   * - ``dmm_usy_ib``
     - ``2bma:m27``
     - 0.0
     - -10.0
     - Upstream tank Y inboard — in-beam vs retracted
   * - ``dmm_dsx``
     - ``2bma:m28``
     - 104.0
     - 104.0 (same)
     - Downstream tank lateral X — **fixed alignment** (NOT a stripe
       selector)
   * - ``dmm_dsy``
     - ``2bma:m29``
     - 0.0
     - -10.0
     - Downstream tank Y — in-beam vs retracted

The X pair (``m25`` / ``m28``) is the same lateral position in both
modes — they are **not** the per-energy stripe selector. The
per-energy mirror-stripe selection is on the Mirror M1
(``m1_horizontal`` = ``2bma:m3``). The three Y motors swing the DMM
tank into or out of the beam at mode switch.

The IOC re-asserts these values on every energy change (they're in
the ``energy_move_*`` set in ``energy2bm.json``), but interpolation
between the two constant values per axis is degenerate — the result
is the constant.


Per-energy saved positions
==========================

The energy-change IOC drives three of the DMM motors per energy: the
two Bragg arms (``2bma:m30`` / ``2bma:m31``) and the second-crystal
vertical (``2bma:m32``). Values are stored in
``energy2bm.json`` under the ``store_0`` field of each motor; the IOC
reads them on each energy change. Reproduced here as a snapshot (the
JSON file is the authoritative source):

.. list-table::
   :header-rows: 1
   :widths: 18 22 22 22 16

   * - Mode
     - Energy [keV]
     - ``dmm_us_arm`` (``2bma:m30``)
     - ``dmm_ds_arm`` (``2bma:m31``)
     - ``dmm_m2_y`` (``2bma:m32``)
   * - Mono
     - 13.374
     - 1.131
     - 1.133
     - 25.1201075
   * - Mono
     - 13.574
     - 1.081
     - 1.083
     - 24.3201075
   * - Mono
     - 18.000
     - 0.822
     - 0.824
     - 18.820045
   * - Mono
     - 20.000
     - 0.726
     - 0.737
     - 17.020045
   * - Mono
     - 25.000
     - 0.57725
     - 0.58825
     - 14.220045
   * - Mono
     - 25.584
     - 0.561
     - 0.572
     - 13.920045
   * - Pink
     - 30 / 40 / 50 / 60
     - 0.740 (parked)
     - 0.751 (parked)
     - 17.020045 (parked)

The Pink-mode values are constant across all four configured energies
(30 / 40 / 50 / 60 keV) — the Bragg arms are simply retracted to a
fixed park position and ``m2_y`` is held at the same value it had at
the Mono 20 keV configuration.


Energy calibration
==================

X-ray energy calibration uses a **channel-cut crystal** to provide an
absolute reference against which the DMM readback is checked and, if
necessary, updated in ``energy2bm.json``.

Channel-cut crystal parameters
------------------------------

- Length: **36 mm**
- Width: **3 mm**
- Lattice spacing (2d): **3.84 Å**


Procedure
---------

1. **Mount the channel-cut crystal**

   - Secure the channel-cut crystal on the rotation stage in the
     X-ray beam path.
   - Align the crystal so the incident beam fully illuminates the
     3 mm width and the reflection geometry is symmetric.
   - Set the rotation angle to zero.

2. **Set initial conditions**

   - Set the monochromator energy to approximately **20 keV**.
   - Compute the expected Bragg angle :math:`\theta` using Bragg's
     law:

     .. math::
        E = \frac{12.3984}{2d \sin\theta} \quad [\text{keV}]

     Rearranged:

     .. math::
        \theta = \arcsin\!\left(\frac{12.3984}{2d\,E}\right)

     where :math:`2d = 3.84\,\text{Å}` and :math:`E = 20\,\text{keV}`.

   - For a 20 keV X-ray beam, the expected Bragg angle is
     approximately **9.29°**.

   Example Python code to compute the expected angle:

   .. code-block:: python

      import numpy as np

      # Parameters
      two_d = 3.84         # 2d in Å
      E_nom = 20.0         # nominal energy in keV
      hc    = 12.3984      # hc in keV·Å

      # Compute Bragg angle (radians and degrees)
      theta_rad = np.arcsin(hc / (two_d * E_nom))
      theta_deg = np.degrees(theta_rad)
      print(f"Bragg angle at {E_nom} keV: {theta_deg:.6f}°")

3. **Record the reflected X-ray**

   - Rotate the crystal to the calculated Bragg angle and search for
     the reflected beam.
   - Select an ROI around the reflection using the ROI plugin in
     areaDetector.
   - Use the Stat2 plugin to compute the mean intensity in the ROI.

4. **Perform rocking-curve scan**

   - Perform a fine angular scan (rocking curve) around the
     calculated Bragg angle to record reflected intensity versus
     angle.

5. **Identify the peak position**

   - Fit the rocking curve to determine the Bragg peak angle
     :math:`\theta_B`.
   - :math:`\theta_B` corresponds to the true Bragg condition at the
     monochromator setting.

   To inspect and fit the data interactively, run **mdaviz**::

     (base) 2bmb@arcturus $ cd /APSshare/bin
     (base) 2bmb@arcturus $ ./mdaviz

6. **Calculate the true energy**

   - Compute the actual energy using Bragg's law:

     .. math::
        E = \frac{12.3984}{2d \sin\theta_B} \quad [\text{keV}]

   Example Python code to compute the true energy from the measured
   peak angle:

   .. code-block:: python

      import numpy as np

      # Parameters
      two_d = 3.84         # 2d in Å
      E_nom = 20.0         # nominal energy in keV
      hc    = 12.3984      # hc in keV·Å

      # Example: replace with measured peak angle in degrees
      theta_B_deg = 9.2903
      theta_B_rad = np.radians(theta_B_deg)

      # Compute measured energy and offset
      E_meas     = hc / (two_d * np.sin(theta_B_rad))
      offset_keV = E_meas - E_nom

      print(f"Measured energy: {E_meas:.6f} keV")
      print(f"Offset from nominal: {offset_keV:.6f} keV")

7. **Update the monochromator calibration**

   - Compare the measured true energy to the nominal monochromator
     value (e.g. 20 keV).
   - Update the per-energy calibration table directly via the
     ``energy`` CLI; there is no separate "offset" stored anywhere.
     Two equivalent options, operator's choice:

     - **Update the existing calibrated entry**: tweak the optics
       (typically the DMM upstream / downstream arms and ``M2 Y``)
       until the channel-cut rocking curve peaks at exactly the
       nominal energy, then save the corrected motor positions::

           (base) 2bmb@arcturus $ energy add --energy 20 --mode Mono

       This overwrites the existing ``20.000 keV`` row of
       ``energy2bm.json`` ``store_0`` with the now-correct motor
       positions. Recommended when the nominal energy is the
       operationally-targeted value.

     - **Save a new calibrated point at the measured value**::

           (base) 2bmb@arcturus $ energy add --energy 20.05 --mode Mono

       This adds a fresh ``20.050 keV`` row to ``energy2bm.json``
       without modifying ``20.000``. Recommended when the measured
       value itself is what subsequent operation will target, or
       when you want to densify the calibration table around a band
       of interest.

8. **Verify calibration**

   - Repeat the procedure at another energy (e.g. 19 keV or 21 keV)
     to verify linearity and consistency of the calibration.


Comparison of calculated and measured X-ray energies
====================================================

The table below lists calculated X-ray energies using a 24 Å
W–B\ :sub:`4`\ C multilayer period (first-order Bragg reflection) and
compares them with measured energies for various incident angles.

+------------------------+------------+--------------------+--------------------------+------------------------+
| Angle (°)              | sin(θ)     | λ (Å) = 2d·sinθ    | Calculated energy (keV)  | Measured energy (keV)  |
+========================+============+====================+==========================+========================+
| 1.1309999999999922     | 0.0197396  | 0.9475             | 13.09                    | 13.374                 |
+------------------------+------------+--------------------+--------------------------+------------------------+
| 1.0809999999999933     | 0.0188718  | 0.9059             | 13.68                    | 13.574                 |
+------------------------+------------+--------------------+--------------------------+------------------------+
| 0.8220000000000001     | 0.0143412  | 0.6884             | 18.02                    | 18.000                 |
+------------------------+------------+--------------------+--------------------------+------------------------+
| 0.726                  | 0.0126695  | 0.6081             | 20.39                    | 20.000                 |
+------------------------+------------+--------------------+--------------------------+------------------------+
| 0.5772499999999998     | 0.0100756  | 0.4836             | 25.63                    | 25.000                 |
+------------------------+------------+--------------------+--------------------------+------------------------+
| 0.5609999999999995     | 0.0097919  | 0.4700             | 26.38                    | 25.584                 |
+------------------------+------------+--------------------+--------------------------+------------------------+

.. note::

   Calculated energies are obtained from Bragg's law:

   .. math::
      E = \frac{12.3984193}{2 d \, \sin\theta} \;\text{[keV]}

   where :math:`d = 24\,\text{Å}` is the multilayer period and
   :math:`\theta` is the incident angle.


Incident angle for given X-ray energies
=======================================

The table below shows the incident angle :math:`\theta` (in degrees)
for selected X-ray energies, assuming a 24 Å W–B\ :sub:`4`\ C
multilayer and first-order Bragg reflection.

+------------------+---------+
| Energy (keV)     | Angle ° |
+==================+=========+
| 13               | 1.145   |
+------------------+---------+
| 14               | 1.061   |
+------------------+---------+
| 15               | 0.990   |
+------------------+---------+
| 16               | 0.928   |
+------------------+---------+
| 17               | 0.872   |
+------------------+---------+
| 18               | 0.823   |
+------------------+---------+
| 19               | 0.779   |
+------------------+---------+
| 20               | 0.739   |
+------------------+---------+
| 21               | 0.703   |
+------------------+---------+
| 22               | 0.670   |
+------------------+---------+
| 23               | 0.640   |
+------------------+---------+
| 24               | 0.612   |
+------------------+---------+
| 25               | 0.586   |
+------------------+---------+
| 26               | 0.561   |
+------------------+---------+
| 27               | 0.538   |
+------------------+---------+
| 28               | 0.517   |
+------------------+---------+
| 29               | 0.497   |
+------------------+---------+
| 30               | 0.478   |
+------------------+---------+
| 31               | 0.460   |
+------------------+---------+
| 32               | 0.443   |
+------------------+---------+
| 33               | 0.426   |
+------------------+---------+

.. note::

   Angles are in degrees (grazing incidence). They are calculated
   using Bragg's law:

   .. math::
      \theta = \arcsin\left(\frac{12.3984193}{2 d E}\right)

   where :math:`d = 24\,\text{Å}` is the multilayer period and
   :math:`E` is the desired X-ray energy in keV.
