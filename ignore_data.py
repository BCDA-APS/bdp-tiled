from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
import numpy


def read_ignore(filename):
    arrays = dict(
        ignore=ArrayAdapter.from_array(
            numpy.array([0,0]), metadata=dict(ignore="placeholder, ignore")
        )
    )
    return MapAdapter(
        arrays, metadata=dict(
            filename=str(filename),
            purpose="ignore this file's contents"
        )
    )
