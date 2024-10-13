from setuptools import setup, find_packages

setup(
    name='vulncov',
    version='0.0.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'vulncov=vulncov.main:main',
        ],
    },
    install_requires=[
        'faiss-cpu==1.9.0',
        'langchain==0.3.3',
        'langchain-community==0.3.2',
        'langchain-core==0.3.10',
        'langchain-huggingface==0.1.0',
        'langchain-ollama==0.2.0',
        'langchain-text-splitters==0.3.0',
        'langsmith==0.1.134',
        'tqdm==4.66.5',
    ],
    description='A tool to match semgrep results with coverage data.',
    author='Miguel Llamazares',
    author_email='mllamazares@protonmail.com',
    url='https://github.com/mllamazares/vulncov',
    package_data={
        'vulncov': [
            'config/coverage.cfg', 
            'config/venv_reqs.txt',
            'config/llm_instructions.txt'
        ], 
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
