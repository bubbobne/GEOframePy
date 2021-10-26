import setuptools
import os

setuptools.setup(
    name="geoframepy",
    version="0.0.5",
    author="Niccolò Tubini, Riccardo Rigon",
    author_email="tubini.niccolo@gmail.com",
    description="A Python library for the GEOframe-NewAge system",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.md")).read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Science/Research",
		
    ],
    python_requires='>=3.6',
)