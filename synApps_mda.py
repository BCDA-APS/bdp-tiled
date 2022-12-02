"""Read the synApps MDA file format."""

from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
import mda

EXTENSIONS = [".mda"]
MIMETYPE = "application/x-mda"


def as_str(v):
    if isinstance(v, bytes):
        return v.decode()
    return v


def read_mda_header(mda_obj):
    h_obj = mda_obj[0]
    file_md = {key: h_obj[key] for key in h_obj["ourKeys"] if key != "ourKeys"}
    file_md["PVs"] = {
        as_str(key): dict(
            desc=as_str(values[0]),
            unit=as_str(values[1]),
            value=values[2],
            EPICS_type=mda.EPICS_types_dict.get(values[3], f"unknown #{values[3]}"),
            count=values[4],
        )
        for key, values in h_obj.items()
        if key not in h_obj["ourKeys"]
    }
    if "version" in file_md:
        # fix the truncation error of 1.299999...
        file_md["version"] = round(file_md["version"], 2)
    if len(mda_obj) != file_md["rank"] + 1:
        raise ValueError(f"rank={file_md['rank']} but {len(mda_obj)=}")

    return file_md


def read_mda_scan_detector(detector):
    md = {k: getattr(detector, k) for k in "desc fieldName number unit".split()}
    md["EPICS_PV"] = as_str(detector.name)
    return md["fieldName"], ArrayAdapter.from_array(detector.data, metadata=md)


def read_mda_scan_positioner(positioner):
    md_attrs = """
        desc
        fieldName
        number
        readback_desc
        readback_name
        readback_unit
        step_mode
        unit
    """.split()
    md = {k: getattr(positioner, k) for k in md_attrs}
    md["readback_PV"] = md.pop("readback_name")  # rename
    md["EPICS_PV"] = as_str(positioner.name)
    return md["fieldName"], ArrayAdapter.from_array(positioner.data, metadata=md)


def read_mda_scan(scan):
    scan_md = dict(
        dim=scan.dim,
        number_detectors=scan.nd,
        number_points_acquired=scan.curr_pt,
        number_points_requested=scan.npts,
        number_positioners=scan.np,
        number_triggers=scan.nt,
        PV=as_str(scan.name),
        rank=scan.rank,
        time=as_str(scan.time),  # TODO: convert to timestamp (need TZ)
        time_zone="US/Central (assumed since not in MDA file)",
    )
    arrays = {}
    for detector in scan.d:
        k, v = read_mda_scan_detector(detector)
        arrays[k] = v
    for positioner in scan.p:
        k, v = read_mda_scan_positioner(positioner)
        arrays[k] = v

    for i, trigger in enumerate(scan.t, start=1):
        # stored with scan metadata
        v = {k: getattr(trigger, k) for k in "command number".split()}
        v["EPICS_PV"] = as_str(trigger.name)
        scan_md[f"T{i}"] = v

    return MapAdapter(arrays, metadata=scan_md)


def read_mda(filename):
    mda_obj = mda.readMDA(
        str(filename),
        useNumpy=True,
        verbose=False,
        showHelp=False,
    )
    file_md = read_mda_header(mda_obj)
    scans = {f"S{scan.rank}": read_mda_scan(scan) for scan in mda_obj[1:]}
    return MapAdapter(scans, metadata=file_md)


def main():
    import pathlib

    path = (
        pathlib.Path().home()
        / "Documents"
        / "projects"
        / "NeXus"
        / "exampledata"
        / "APS"
        / "scan2nexus"
    )
    for filename in sorted(path.iterdir()):
        if filename.name.endswith(EXTENSIONS[0]):
            structure = read_mda(filename)
            print(f"{filename.name=}")
            print(f"{structure}")


if __name__ == "__main__":
    main()
