# <font size="20"><b> WIP</b></font>
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

A deterministic simulation tool to perform time-driven railway route simulations. 
## Implemented functionality


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


