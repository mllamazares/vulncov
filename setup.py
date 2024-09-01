from setuptools import setup, find_packages

setup(
    name='vulncov',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'vulncov=vulncov.vulncov:main',
        ],
    },
    install_requires=[
    ],
    description='A tool to match semgrep results with coverage data.',
    author='Miguel Llamazares',
    author_email='mllamazares@protonmail.com',
    url='https://github.com/mllamazares/vulncov',
    package_data={
        'vulncov': ['coverage.cfg'], 
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
