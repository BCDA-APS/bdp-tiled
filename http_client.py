"""
Simple demo tiled Python client using the http API.

[12/2 2:40 PM] Jemian, Pete R.
Maybe, instead of a Python client, I will show some specific URI queries and responses.

* [x] Find all runs in a catalog between these two ISO8601 dates.
* [x] Find run(s) which match given metadata.
* [ ] Get overall metadata from given run.
* [ ] What are the data streams in this run?
* [ ] What is the metadata for this stream?
* [ ] Get the data from the data stream named primary (the canonical main data).
* [ ] What about loose matches?  Maybe not now.  Might require some deeper expertise.
"""

import datetime
import requests
import pyRestTable


def requests_tiled(server, catalog, api="/api/v1/node/search", suffix="", port=8000):
    uri = f"http://{server}:{port}{api}/{catalog}{suffix}"
    r = requests.get(uri)
    # print(f"{r.encoding=}")
    # print(f"{r.headers=}")
    # print(f"{r.status_code=}")
    # print(f"{r.text=}")
    return r.json()


def overview():
    table = pyRestTable.Table()
    table.labels = (
        "catalog scan_id date/time duration,s plan_name title ESAF_id".split()
    )

    for catalog in "bdp2022 20idb_usaxs".split():
        # how many runs in the catalog?
        # Set limit to 1 because a 0 means ALL the runs.
        response = requests_tiled("terrier", catalog, suffix="?page[limit]=1")
        # print(f"{response['error']=}")
        count = response["meta"]["count"]
        print(f"{catalog=} has {count} runs")

        # get the n most recent runs
        num_runs = 20
        response = requests_tiled(
            "terrier",
            catalog,
            suffix=f"?page[offset]={count-num_runs}&page[limit]={num_runs}",
        )
        # print(f"{response['error']=}")

        # list these runs
        for run in reversed(response["data"]):
            md = run["attributes"]["metadata"]
            dt = md["summary"]["datetime"]
            duration = md["summary"]["duration"]
            esaf_id = md["start"].get("esaf_id", "")
            exit_status = md["stop"]["exit_status"]
            plan_name = md["summary"]["plan_name"]
            scan_id = md["summary"]["scan_id"]
            streams = " ".join(md["summary"]["stream_names"])
            title = md["start"].get("title", "")
            uid = md["start"]["uid"]
            table.addRow(
                (
                    catalog,
                    f"{scan_id:>7}",
                    dt,
                    f"{duration:>10.1f}",
                    plan_name,
                    title,
                    esaf_id,
                )
            )

    print(table)


def table_of_runs(runs):
    table = pyRestTable.Table()
    table.labels = "row# scan_id plan_name start duration(s) uid7".split()
    for row, run in enumerate(runs, start=1):
        md = run["attributes"]["metadata"]
        dt = md["summary"]["datetime"]
        duration = md["summary"]["duration"]
        plan_name = md["summary"]["plan_name"]
        scan_id = md["summary"]["scan_id"]
        uid = md["summary"]["uid"]
        table.addRow(
            (row, scan_id, plan_name, dt, duration, uid[:7])
        )
    return table


def find_runs_by_date(server, catalog, since, until, limit=20):
    # Find all runs in a catalog between these two ISO8601 dates.
    def to_ts(isodate):
        return datetime.datetime.fromisoformat(isodate).timestamp()

    tz = "US/Central"
    suffix = (
        "?page[offset]=0"
        f"&page[limit]={limit}"
        f"&filter[time_range][condition][since]={to_ts(since)}"
        f"&filter[time_range][condition][until]={to_ts(until)}"
        f"&filter[time_range][condition][timezone]={tz}"
        "&sort=time"
    )
    r = requests_tiled(server, catalog, suffix=suffix)
    print(f"Runs starting after '{since}' and before '{until}'")
    print(table_of_runs(r["data"]))

    return r


def find_by_plan_name(server, catalog, plan_name, limit=20):
    # Find run(s) which match given metadata: given plan_name
    case_sensitive = False
    suffix = (
        "?page[offset]=0"
        f"&page[limit]={limit}"
        "&filter[eq][condition][key]=plan_name"
        f'&filter[eq][condition][value]="{plan_name}"'
        "&sort=time"
    )
    r = requests_tiled(server, catalog, suffix=suffix)
    print(f"Runs that match 'plan_name={plan_name}'")
    print(table_of_runs(r["data"]))

    return r


def get_run_metadata(server, catalog, uid, stream=None):
    suffix = f"/{uid}"
    if stream is not None:
        suffix += f"/{stream}"
    r = requests_tiled(
        server, catalog,
        api="/api/v1/node/metadata",
        suffix=suffix,
    )
    print(r["data"]["attributes"]["metadata"])

    return r["data"]["attributes"]["metadata"]


def main():
    server = "localhost"
    catalog = "bdp2022"

    r = find_runs_by_date(
        server, "20idb_usaxs", "2022-11-01 15:50", "2022-12-01 16:10"
    )
    r = find_by_plan_name(server, "20idb_usaxs", "tune_a2rp")

    r = find_runs_by_date(
        server, "bdp2022", "2022-11-01 15:50", "2022-12-01 16:10"
    )
    r = find_by_plan_name(server, "bdp2022", "take_image")

    r = get_run_metadata(
        server, "bdp2022", "00714a91-c33e-4e7b-90fd-2e8f385bebc9",
    )

    r = get_run_metadata(
        server, "bdp2022", "00714a91-c33e-4e7b-90fd-2e8f385bebc9", "primary"
    )

    if False:
        # Get the data from the data stream named primary (the canonical main data).
        data_format = "json"
        uid = "00714a91-c33e-4e7b-90fd-2e8f385bebc9"
        r = requests_tiled(
            server, catalog,
            api="/api/v1/array/full",
            suffix=(
                f"/{uid}"
                f"/{stream_name}"
                "/data"
                r"%format=json"
            )
        )
        print(len(r))


if __name__ == "__main__":
    main()
