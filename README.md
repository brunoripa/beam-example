# Beam example

This article will show a basic usage of Apache Beam library.

## Introduction

The application is made for Google Cloud Platform, specifically Flexible Environment. Please read the google docs here () to get more information about that

## Installation

First, create a virtualenv

    virtualenv --no-site-packages beam
    source beam/binactivate

After this, install all the dependencies:

    pip install -r requirements.txt

## Input files generation

In order to create a valid input file, use the `generate.py` script:

    python generate.py

## Execution

last, but not least, start the instance with:

    make run

The endpoint to hit is `http://localhost:8090/dataflow/from_text`

Once you see the page showing `ok`, you can go on the filesystem and look at the `output.txt-00000-of-00001` file.

## Note

Pay attention that some python version might throw you an error:

    TypeError: Error when calling the metaclass bases
    metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
    make: *** [run] Error 1

This happened to me when i tried to use a different Python version (still 2, but a different build). Sadly you have to address any of these errors contenxtually.
