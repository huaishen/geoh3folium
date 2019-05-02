from setuptools import setup

description = '''
- Geographical data conversion among kml, shapely, coordinates
- Transformation from polygons to h3 hexagons and visualization on map by folium
See github for more details.
'''

install_requires = [
    'Shapely', 'h3',
    'pandas', 'folium', 'fastkml'
]

setup(
    name='geoh3folium',
    version='0.0.2',
    author='Li Huaishen',
    author_email='lhsjj0109@gmail.com',
    py_modules=['geo_h3folium'],
    url='https://github.com/lhs328808891/geoh3folium',
    license='LICENSE',
    description='Transform polygons to h3 hexagons and visualize them by folium',
    long_description=description,
    install_requires=install_requires,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='geographical visualization h3 folium'
)
