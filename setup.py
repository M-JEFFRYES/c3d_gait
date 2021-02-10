from setuptools import setup

#with open('requirements.txt') as f:
    #requirements = f.read().splitlines()

setup(
    name='C3D_gait',
    author='Michael Jeffryes',
    author_email='mike.jeffryes@hotmail.com',
    url='',
    version='1.0.5',
    description='Extracts gait data from C3D files',
    #packages=['gpscalc'],
    py_modules=["gaittrial","anonymisec3d"],
    package_dir={'':'c3dgait'},
    setup_requires=['wheel'],
    classifiers=[
        #"License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    #install_requires=requirements,
    long_description=open('README.md').read(),
)

