import os

import io

import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

with io.open('ktuvitDownloader/__version__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

setup(
    name='ktuvitDownloader',
    version='0.1',
    description=readme,
    # url='http://github.com/storborg/funniest',
    classifiers=['Development Status :: 1 - Planning',
                 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                 'Operating System :: OS Independent',
                 'Intended Audience :: End Users/Desktop',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Multimedia',
                 ],
    author='Aviad Levy',
    author_email='aviadlevy1@gmail.com',
    license='LGPLv3',
    packages=['ktuvitDownloader'],
    install_requires=[
        'guessit',
    ],
    entry_points={
        'console_scripts': [
            'ktuvitDownloader = ktuvitDownloader.__main__:main'
        ],
    },
    zip_safe=True)
