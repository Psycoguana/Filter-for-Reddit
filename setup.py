import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ffr",
    version="0.0.1",
    author="Psycoguana",
    author_email="",
    description="Filter for Reddit saves",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Psycoguana/Filter-for-Reddit",
    packages=setuptools.find_packages(),
    scripts = ['bin/ffr'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
