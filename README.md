<p align="center">
  <br>
  <a href="https://github.com/danicc097/RailwaySim/blob/master/LICENSE"><img alt="undefined" src="resources/images/GPLv3_badge.svg"></a>
  <a ><img alt="undefined" src="resources/images/Windows_badge.svg"></a>
  <a ><img alt="undefined" src="resources/images/Linux_badge.svg"></a>
  <br>
</p>

<p align="center"><img src="resources/images/RailwaySimLogo.svg" width="250"/ ></p>

<font size="20"><b>WIP</b></font>

# RailwaySim

#### Table of contents  <!-- omit in toc -->

- [RailwaySim](#railwaysim)
  - [Implemented functionality](#implemented-functionality)
    - [Rolling stock resistances](#rolling-stock-resistances)
  - [Installation](#installation)
  - [Capabilities](#capabilities)
  - [Usage](#usage)
    - [Solvers:](#solvers)
  - [Results](#results)


<p align="center"><img src="resources/tabScreen.png" alt="tab" width="650"/></p>
<p align="center">Full screen:</p>
<p align="center"><img src="resources/tabScreenDark.png" alt="tab" width="650"/></p>

A deterministic simulation tool to perform time-driven railway route simulations. 
## Implemented functionality

Virtual speed calculation:

To ensure that the rolling stock complies with the predefined track speed limits at all points, it is necessary to take its total length into account. In a nutshell, this algorithm will offset the original speed limit by the train length when a target is encountered, <i>i.e.</i> when the next speed is higher than the preceding one, splitting the original array while preserving the rest of the track's parameters (grade, curve radius, etc.). The simulation point is set to be in the front of the train for further calculations.

<p align="center"><img src="resources/images/Virtual_speed_acceleration_example.svg" alt="resistances" width="750"/></p>
<p align="center"><img src="resources/images/Virtual_speed_example.svg" alt="resistances" width="750"/></p>

Train length is equally essential to determine the average grade to which the system is subjected. An equivalent grade can be obtained based on train length and weighing one step backwards at a time up until the total length.

### Rolling stock resistances


<p align="center"><img src="resources/images/formulas/Resistances.png" alt="resistances" width="350"/></p>
where <i>m</i> is the total mass in tonnes, <i>u</i> is speed in km/h and <i>g</i> is gravity in m/s<sup>2</sup>. <i>R<sub>S</sub></i> is the starting resistance, introduced manually as deemed fit for the system. Rolling resistance <i>R<sub>R</sub></i> is given by the Davis formula with coefficients <i>A</i>, <i>B</i> and <i>C</i>, which depend on the particular vehicle. Resistance due to grade, <i>R<sub>G</sub></i>, is dependent on the track slope. Finally, <i>R<sub>C</sub></i> is given by the empirical Desdovits formula and is passed the current curve radius and track gauge.       
## Installation


## Capabilities

Test

## Usage
### Solvers:
1. Minimize operation time: normally used as a benchmark. Yields the fastest driving strategy possible with the given constraints.
2. Minimize energy consumption: TODO
3. Fixed travel time: TODO
## Results

Test


