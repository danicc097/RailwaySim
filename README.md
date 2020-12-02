<p align="center">
  <br>
  <a href="https://github.com/danicc097/RailwaySim/blob/master/LICENSE"><img alt="undefined" src="resources/images/GPLv3_badge.svg"></a>
  <a ><img alt="undefined" src="resources/images/Windows_badge.svg"></a>
  <a ><img alt="undefined" src="resources/images/Linux_badge.svg"></a>
  <br>
</p>

<p align="center"><img src="resources/images/RailwaySimLogo.svg" width="250"/ ></p>

#### Table of contents  <!-- omit in toc -->
- [RailwaySim](#railwaysim)
  - [Development](#development)
      - [Requirements](#requirements)
  - [Features](#features)
        - [Virtual speed calculation:](#virtual-speed-calculation)
        - [Rolling stock resistance](#rolling-stock-resistance)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Solvers](#solvers)
  - [Results](#results)

<p align="center"><b>WIP</b></p>

# RailwaySim
A deterministic tool to perform railway route simulations. 

<p align="center"><img src="resources/tabScreen.png" alt="tab"/></p>
<p align="center"><img src="resources/tabScreenDark.png" alt="tab"/></p>


## Development

#### Requirements
- `Python +3.8`
- `pip3`
- `PyQt5` (or `PySide2`; in this case, its licensing is the only difference)
- `pipenv` (recommended)
- Packages inside `pipfile`. They will be installed by default in the virtual environment with `pipenv install`.

To get started:
1. Clone the repo: `git clone https://github.com/danicc097/RailwaySim.git`
2. Install the required packages and corresponding versions with `pipenv install`
3. Run the main program file with `pipenv run python RailwaySim_main.py`
4. If you make any changes to a `.ui` file, convert it later to python with
   `pyuic5 -x input_file.ui -o output_file.py` 
5. To distribute using `PyInstaller`, execute `pipenv run pyinstaller --onefile RailwaySim_main.py -i railwaysimicon.ico`.

## Features

##### Virtual speed calculation:

To ensure that the rolling stock complies with the predefined track speed limits at all points, it is necessary to take its total length into account. In a nutshell, this algorithm will offset the original speed limit by the train length when a target is encountered, <i>i.e.</i> when the next speed is higher than the preceding one, splitting the original array while preserving the rest of the track's parameters (grade, curve radius, etc.). The simulation point is set to be in the front of the train for further calculations.

<p align="center"><img src="resources/images/Virtual_speed_acceleration_example.svg" alt="resistances" width="750"/></p>
<p align="center"><img src="resources/images/Virtual_speed_example.svg" alt="resistances" width="750"/></p>

Train length is equally essential to determine the average grade to which the system is subjected, instead of using the front car as only reference. A far more accurate equivalent grade can be obtained based on train length and weighing one grade step backwards at a time up until the total length is reached. Curve resistance is however independent of train length and calculated based on the current simulation point.

To determine the actual braking curve, whenever any intersection is found (A) between the powering/cruising and braking matrices, the remaining curve that follows is appended.

<p align="center"><img src="resources/images/braking_example.svg"/></p>


##### Rolling stock resistance
Total resistance effort is currently computed based on the following set of formulas. Custom formulas defined by the user with a given set of variables may be implemented in the future.

<p align="center"><img src="resources/images/formulas/Resistances.png" alt="resistances" width="350"/></p>
where <i>m</i> is the total mass in tonnes, <i>u</i> is speed in km/h and <i>g</i> is gravity in m/s<sup>2</sup>. <i>R<sub>S</sub></i> is the starting resistance, introduced manually as deemed fit for the system. Rolling resistance <i>R<sub>R</sub></i> is given by the Davis formula with coefficients <i>A</i>, <i>B</i> and <i>C</i>, which depend on the particular vehicle. Resistance due to grade, <i>R<sub>G</sub></i>, is dependent on the track slope. Finally, <i>R<sub>C</sub></i> is given by the empirical Desdovits formula and is passed the current curve radius and track gauge.       
## Installation

## Usage



### Solvers
As of now, unless the project gains some <i>traction</i>, the only available solver is 1. Any contribution is welcome.

1. <i>Minimize operation time</i>: normally used as a benchmark. Yields the fastest driving strategy possible with the given constraints.
2. <i>Minimize energy consumption</i>: -
3. <i>Fixed travel time</i>: -

## Results

An output CSV file is saved with relevant results to represent the unit's performance to the selected location, easily imported into the user's most preferred visualization software or ready to analyze in the beautifully integrated GUI's canvas.


