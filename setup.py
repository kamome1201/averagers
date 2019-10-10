from setuptools import setup, find_packages

setup(
    name             = 'averagers',
    version          = "0.1.0",
    description      = 'Tools for mean temperature estimation',
    license          = "BSD 3-clause License",
    author           = "Kenji Fukushima",
    author_email     = 'kfuku52@gmail.com',
    url              = 'https://github.com/kfuku52/averagers.git',
    keywords         = '',
    packages         = find_packages(),
    install_requires = ['numpy','pandas','ephem',],
    #scripts          = ['',],
)