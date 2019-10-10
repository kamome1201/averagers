## Overview
**averagers** is a python package for estimating daily mean temperature using daily min/max temperatures.

## Dependency
* [python 3](https://www.python.org/)
* [numpy](https://github.com/numpy/numpy)
* [pandas](https://github.com/pandas-dev/pandas)
* [PyEphem](https://github.com/brandon-rhodes/pyephem)

## Installation
```
# Installation with pip
pip install git+https://github.com/kfuku52/averagers
```

## Example
See `./data/cross_validation.ipynb`

## Citation
This is an implementation of the method proposed by this paper.

**Dall'Amico and Hornsteiner. 2006.** A simple method for estimating daily and monthly mean temperatures from daily minima and maxima. Int J Climatol 26: 1929-1936. https://rmets.onlinelibrary.wiley.com/doi/abs/10.1002/joc.1363

## Licensing
**averagers** is BSD-licensed (3 clause). See [LICENSE](LICENSE) for details.