import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

main_ns = {}
with open('ffr/version.py') as f:
    exec(f.read(), main_ns)

setuptools.setup(
    name="ffr",
    version=main_ns['__version__'],
    author="Psycoguana",
    author_email="",
    description="Filter for Reddit saves",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Psycoguana/Filter-for-Reddit",
    packages=setuptools.find_packages(),
    install_requires=[
        'praw',
        'rich',
        'click'
    ],
    scripts=['bin/ffr'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
