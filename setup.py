# coding: utf-8

"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import find_namespace_packages, setup

# Reading version from __version__.py file
with open('src/myofinder/__version__.py') as file:
  for line in file:
    if line.startswith('__version__'):
      __version__ = line.split("'")[1]

setup(
  # Description of the project
  name='myofinder',
  version=__version__,
  description='Automatic calculation of the fusion index by AI segmentation',
  long_description="""Myoblast Fusion Index Determination
  Myofinder is is a Python module for the automatic calculation of the fusion 
  index on florescence-stained images of muscle cultures. It provides a simple 
  and user-friendly interface managing several images, processing all or part 
  of them, visualizing the output, and manually correcting it if needed. It 
  relies on the DeepCell library for performing the image segmentation.
  """,
  keywords='segmentation,fusion index,automation,muscle culture',
  license='GPL V3',
  classifiers=['Development Status :: 5 - Production/Stable ',
               'Intended Audience :: Science/Research',
               'License :: OSI Approved :: GNU General Public License v3 '
               '(GPLv3)',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3.7',
               'Programming Language :: Python :: 3.8',
               'Programming Language :: Python :: 3.9',
               'Programming Language :: Python :: 3.10',
               'Topic :: Scientific/Engineering :: Artificial Intelligence',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               'Topic :: Scientific/Engineering :: Image Recognition'
               ],

  # URLs of the project
  url='https://github.com/TissueEngineeringLab/MyoFInDer',
  download_url='https://pypi.org/project/myofinder/#files',
  project_urls={
    'Documentation': 'https://tissueengineeringlab.github.io/MyoFInDer/',
    'Source': 'https://github.com/TissueEngineeringLab/MyoFInDer'},

  # Information on the author
  author='Antoine Weisrock',
  author_email='antoine.weisrock@kuleuven.be',
  maintainer='Antoine Weisrock',
  maintainer_email='antoine.weisrock@gmail.com',

  # Packaging information
  packages=find_namespace_packages(where="src", exclude=list()),
  package_dir={"": "src"},
  include_package_data=True,
  package_data={"myofinder": ["app_images/*"]},
  ext_package='myofinder',
  ext_modules=list(),

  # Installation requirements
  python_requires=">=3.7,<3.11",
  install_requires=['Pillow>=9.0.0', 'opencv-python>=4.5', 'DeepCell==0.12.7',
                    'XlsxWriter>=3.0.0', 'screeninfo>=0.7', 'numpy<1.24'],
  extras_require=dict(),

  # Others
  zip_safe=False,
)
