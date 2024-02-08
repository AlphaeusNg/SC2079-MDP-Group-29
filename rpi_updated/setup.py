from setuptools import setup

setup(name='rpi',
      version='1.0',
      description='MDP ARPI',
      author='Group 29',
      packages=['mdp-rpi'],
      install_requires=[
        'opencv-python',
        'picamera',
        'serial',
      ]
     )