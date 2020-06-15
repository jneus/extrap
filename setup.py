from setuptools import setup, find_namespace_packages, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="extrap-meaparvitas",
    version="0.0.18",
    package_dir={"": "src"},
    packages=find_packages("src"),
    author="Extra-P Project",
    author_email="extra-p@lists.parallel.informatik.tu-darmstadt.de",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MeaParvitas/Extra-P",
    entry_points={
        "console_scripts": [
            "extrap = extrap.extrap:main",
        ],
        
        "gui_scripts": [
            "extrap-gui = extrap.extrapgui:main",
        ]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=["pyqt5", "numpy", "matplotlib"],
)
