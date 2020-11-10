from setuptools import setup


# Description
with open('README.md') as file:
    long_description = file.read()


setup(
    name='spa',
    version='0.0.1',
    description='Speech phoneme alignment representation',
    author='Max Morrison',
    author_email='maxrmorrison@gmail.com',
    url='https://git.corp.adobe.com/adobe-research/spa',
    packages=['spa'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='speech phoneme duration alignment',
    license='TODO',
    install_requires=['numpy'])
