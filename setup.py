from setuptools import setup, find_packages
# import version
from src.vmusic import __version__

setup(
    name='vmusic',
    version=__version__,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        # add your project dependencies here
    ],
    entry_points='''
        [console_scripts]
        vmusic=vmusic.main:main
    ''',
)