from setuptools import setup, find_packages

VERSION = '2.0.0'
DESCRIPTION = 'Manyterm - spawn multiple terminals to print to'
with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='manyterm',
    version=VERSION,
    author='Tyler Bowers',
    author_email='tylerebowers@gmail.com',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=["psutil"],
    keywords=['python', 'terminal', 'print'],
    classifiers=[
        'Topic :: Terminals',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    project_urls={
        'Source': 'https://github.com/tylerebowers/manyterm-python',
        'PyPI': 'https://pypi.org/project/manyterm/'
    }
)