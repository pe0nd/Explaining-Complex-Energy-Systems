# Explaining-Complex-Energy-Systems

## Introduction
The code presented here is part of the "Explaining Complex Energy Systems: A Challenge" poster presented on the "Tackeling Climate Change with Machine Learning"-Workshop at the NIPS 2020.


## LP Model
The linear program implemented in **Model.py** has the following minimization goal:

<img src="https://render.githubusercontent.com/render/math?math=\min\limits_{Cap,p} cost = c_{PV} \times Cap_{PV} %2B c_{battery} \times Cap_{battery} %2B \sum\limits_{t} c_{buy}(t) \times p_{buy}(t)">



## Authors
* [Jonas H&uuml;lsmann](https://www.eins.tu-darmstadt.de/eins/team/jonas-huelsmann)
* [Florian Steinke](https://www.eins.tu-darmstadt.de/eins/team/florian-steinke)
