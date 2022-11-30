from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.md').read()

setup(
    name="lineage_viewer",
    packages=["lineage_viewer"],
    version=version,
    description="Graphical interface for editing a lineage and viewing related microscopy images.",
    long_description=readme,
    include_package_data=True,
    author="Aaron Watters",
    author_email="awatters@flatironinstitute.org",
    url=url,
    install_requires=[
        "numpy", 
        "scipy", 
        ],
    license="MIT"
)
