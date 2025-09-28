from setuptools import setup, find_packages

setup(
    name='nhtsa',
    version='0.1.3',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    author='Reed Graff',
    author_email='rangergraff@gmail.com',
    description='Unofficial Python SDK/wrapper for NHTSA APIs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ReedGraff/NHTSA',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'httpx',
        'pydantic',
        'aiofiles',
        'python-dotenv',
        'pillow',
        'tqdm',
        'beautifulsoup4',
        'lxml',
    ],
)