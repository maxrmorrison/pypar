from setuptools import setup


# Description
with open('README.md') as file:
    long_description = file.read()


setup(
    name='pypar',
    version='0.0.3',
    description='Python phoneme alignment representation',
    author='Max Morrison',
    author_email='maxrmorrison@gmail.com',
    url='https://github.com/maxrmorrison/pypar',
    install_requires=['numpy', 'textgrid'],
    packages=['pypar'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['align', 'duration', 'phoneme', 'speech'],
    classifiers=['License :: OSI Approved :: MIT License'],
    license='MIT')
