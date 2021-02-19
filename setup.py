from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='physion',
    version='1.0',
    description='Physiology of Vision - Code for experimental setup and analysis to study the physiology of visual circuits',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/yzerlaut/physion',
    author='Yann Zerlaut',
    author_email='yann.zerlaut@icm-institute.org',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='vision physiology',
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "numpy",
        "scipy",
        "argparse",
        "scikit-image",
        "scikit-learn",
        "scikit-video",
        "numba",
        "av",
        "mkl",
        "psychopy",
        "pyqt5",
        "pyqtgraph",
        "imageio",
        "opencv-python",
        "scanimage-tiff-reader>=1.4.1",
        "opencv_python_headless",
        "tifffile",
        "nidaqmx",
        "xmltodict",
        "importlib_metadata",
        "natsort",
        "paramiko",
        "rastermap>0.1.0",
        "temp",
        "pynwb"
    ]
)
