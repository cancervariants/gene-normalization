"""Defines how metakb is packaged and distributed."""
from setuptools import setup

# TODO: Fix name and packages
setup(name='gene',
      version='0.0.1',
      description='VICC normalization routine for genes',
      url='https://github.com/cancervariants/gene-normalization',
      author='VICC',
      author_email='help@cancervariants.org',
      license='MIT',
      packages=['gene'],
      zip_safe=False)
