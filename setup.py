from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.md').read()

setup(
    name="lineage_viewer",
    packages=["lineage_viewer"],
    package_data={"lineage_viewer": ["lineage_doodle.js"]},
    include_package_data=True,
    version=version,
    description="Graphical interface for editing a lineage and viewing related microscopy images.",
    long_description=readme,
    author="Aaron Watters",
    author_email="awatters@flatironinstitute.org",
    url=url,
    install_requires=[
        "numpy", 
        "scipy",
        "h5gizmos",
        "resample3",
        ],
    license="MIT"
)
