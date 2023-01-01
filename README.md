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
This program was reported in:

**Fukushima et al. 2021.** A discordance of seasonally covarying cues uncovers misregulated phenotypes in the heterophyllous pitcher plant *Cephalotus follicularis*. Proceedings of the Royal Society B 288(1943): 20202568. https://royalsocietypublishing.org/doi/10.1098/rspb.2020.2568

Also, this program implements the method reported in the following paper.

**Dall'Amico and Hornsteiner. 2006.** A simple method for estimating daily and monthly mean temperatures from daily minima and maxima. International Journal of Climatology 26: 1929-1936. https://rmets.onlinelibrary.wiley.com/doi/abs/10.1002/joc.1363

## Licensing
**averagers** is BSD-licensed (3 clause). See [LICENSE](LICENSE) for details.
