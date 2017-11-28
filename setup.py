""" Cricic installation script """
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Cricic',
    version='0.0.1',
    description='Simple make/git-based CI',
    author='jwmng',
    author_email='mail@jwmng.nl',
    url='https://github.com/jwmng/cricic',
    packages=['cricic'],
    data_files=[('config', ['conf/buildfile.sample', 
                            'conf/config.ini'])],
    # scripts=['bin/cricic']
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'cricic=cricic.__main__:main'
        ]
    },
)
