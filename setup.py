from setuptools import setup, find_packages

VERSION_NUMBER = '0.1.0'


with open('requirements.txt', 'rb') as handle:
    REQUIREMENTS = [
        x.decode('utf8') for x in handle.readlines()
    ]


with open('dev_requirements.txt', 'rb') as handle:
    TEST_REQUIREMENTS = [
        x.decode('utf8') for x in handle.readlines()
    ]


setup(
    name='apache_beam_example',
    version=VERSION_NUMBER,
    description="",
    long_description=open("README.md").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='',
    author='Bruno Ripa',
    author_email='bruno.ripa@gmail.com',
    url='',
    license='GPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS
)
