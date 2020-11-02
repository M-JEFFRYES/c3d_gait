from setuptools import setup

#with open('requirements.txt') as f:
    #requirements = f.read().splitlines()

setup(
    name='C3D_gait',
    author='Michael Jeffryes',
    author_email='mike.jeffryes@hotmail.com',
    url='',
    version='0.0.3',
    description='Extracts gait data from C3D files',
    #packages=['gpscalc'],
    py_modules=["anon_c3d","c3d_extract_data"],
    package_dir={'':'src'},
    setup_requires=['wheel'],
    classifiers=[
        #"License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    #install_requires=requirements,
    long_description=open('README.md').read(),
)

