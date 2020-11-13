# Explaining-Complex-Energy-Systems

## Introduction
The code presented here is part of the "Explaining Complex Energy Systems: A Challenge" poster presented on the "Tackeling Climate Change with Machine Learning"-Workshop at the NIPS 2020.


## LP Model
The linear program implemented in **Model.py** has the following minimization goal:

<img src="https://render.githubusercontent.com/render/math?math=\min\limits_{Cap,p} cost = c_{PV} \times Cap_{PV} %2B c_{battery} \times Cap_{battery}^S %2B \sum_{t} c_{buy}(t) \times p_{buy}(t)">

The following restrictions are applied:

<img src="https://render.githubusercontent.com/render/math?math=p_{buy}(t) %2B p_{PV}(t) %2B p_{battery}^{out}(t) - p_{battery}^{in}(t) = Demand(t), \forall t">

<img src="https://render.githubusercontent.com/render/math?math=p_{battery}^{S}(t) = p_{battery}^{S}(t-1) %2B p_{battery}^{in}(t) \times \delta t - p_{battery}^{out}(t) \times \delta t , t \in 2,...,T">

<img src="https://render.githubusercontent.com/render/math?math=0 \leq p_{PV}(t) \leq Cap_{PV} \times availibilty_{PV}(t) \times \delta t, \forall t">

<img src="https://render.githubusercontent.com/render/math?math=0 \leq p_{battery}^{S}(t) \leq Cap_{battery}^S, \forall t">

<img src="https://render.githubusercontent.com/render/math?math=0 \leq p_{battery}^{in}(t), p_{battery}^{out}(t) \leq Cap_{battery}^S \times \delta t, \forall t">

<img src="https://render.githubusercontent.com/render/math?math=p_{battery}^{S}(0) = p_{battery}^{S}(T)">

<img src="https://render.githubusercontent.com/render/math?math=0 = p_{buy}(t), \forall t">




## Authors
* [Jonas H&uuml;lsmann](https://www.eins.tu-darmstadt.de/eins/team/jonas-huelsmann)
* [Florian Steinke](https://www.eins.tu-darmstadt.de/eins/team/florian-steinke)
