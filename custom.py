"""
Custom handling for data file types not recognized by tiled.

https://blueskyproject.io/tiled/how-to/read-custom-formats.html
"""

from punx.utils import isHdf5FileObject
from punx.utils import isNeXusFile
from spec2nexus.spec import is_spec_file_with_header
import h5py
import pathlib


FILE_OF_UNRECOGNIZED_FILE_TYPES = "/tmp/unrecognized_files.txt"


def isHdf5(filename):
    try:
        with h5py.File(filename, "r") as fp:
            return isHdf5FileObject(fp)
    except Exception:
        pass
    return False


def isNeXus(filename):
    try:
        return isNeXusFile(filename)
    except Exception:
        pass
    return False


mimetype_table = {
    is_spec_file_with_header: "text/spec_data",  # spec2nexus.spec.is_spec_file_with_header
    isNeXus: "application/x-hdf5",  # punx.utils.isNeXusFile
    isHdf5: "application/x-hdf5",  # punx.utils.isHdf5FileObject
}


def detect_mimetype(filename, mimetype):
    filename = pathlib.Path(filename)
    if "/.log" in str(filename).lower():
        mimetype = "text/plain"
    elif ".log" in filename.name.lower():
        mimetype = "text/plain"

    if mimetype is None:
        # When tiled has not already recognized the mimetype.
        mimetype = "text/csv"  # the default
        for tester, mtype in mimetype_table.items():
            # iterate through our set of known types
            if tester(filename):
                mimetype = mtype
                break
    if filename.name == "README":
        mimetype = "text/readme"

    if mimetype is None:
        with open(FILE_OF_UNRECOGNIZED_FILE_TYPES, "a") as fp:
            # TODO: What's the point of writing mimetype here? It's `None`!
            fp.write(f"{mimetype}  {filename}\n")

    return mimetype
