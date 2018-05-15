from setuptools import setup

setup(name='Magstim',
    version='1.0.5',
    download_url="https://github.com/kaysoky/MagStim_PyServer",
    packages=['Magstim'],
    install_requires=[
        'pyserial>=2.5', 
        'web.py>=0.37', 
        'requests>=1.2.3', 
        'mock>=1.0.0'
    ],
    tests_require=['mock'],
    zip_safe=False,
    platforms=['any'],
)
