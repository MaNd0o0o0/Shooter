"""
setup.py - إعداد المشروع
"""

from setuptools import setup, find_packages

setup(
    name='GalaxyShooter',
    version='1.0.0',
    description='Galaxy Shooter Game',
    author='Developer',
    packages=find_packages(),
    install_requires=[
        'kivy>=2.3.0',
        'pygame>=2.6.0',
    ],
)