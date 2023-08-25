from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Python wrapper for GraphDB and SPARQL interface'
LONG_DESCRIPTION = 'Python wrapper for GraphDB and SPARQL interface'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="py2graphdb", 
        version=VERSION,
        author="Bart Gajderowicz",
        author_email="bgajdero@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'grpahdb', 'ontotext', 'sparql'],
        classifiers= [
            "Development Status :: 1 - Planning",
            "Topic :: Database"
            "Intended Audience :: Education",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3.10",
            "Environment :: Console",
            "Operating System :: POSIX :: Linux",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
