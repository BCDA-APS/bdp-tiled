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


def tiled_query(server, catalog, api="/api/v1/node/search", suffix="", port=8000):
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
        response = tiled_query("terrier", catalog, suffix="?page[limit]=1")
        # print(f"{response['error']=}")
        count = response["meta"]["count"]
        print(f"{catalog=} has {count} runs")

        # get the n most recent runs
        num_runs = 20
        response = tiled_query(
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


def main():
    server = "localhost"
    catalog = "20idb_usaxs"

    # Find all runs in a catalog between these two ISO8601 dates.
    start_time = "2022-12-01 15:50"
    end_time = "2022-12-01 16:10"
    ts_since = datetime.datetime.fromisoformat(start_time).timestamp()
    ts_until = datetime.datetime.fromisoformat(end_time).timestamp()
    tz = "US/Central"
    suffix = (
        "?page[offset]=00&page[limit]=100"
        f"&filter[time_range][condition][since]={ts_since}"
        f"&filter[time_range][condition][until]={ts_until}"
        f"&filter[time_range][condition][timezone]={tz}"
        "&sort=time"
    )
    r = tiled_query(server, catalog, suffix=suffix)
    print(f"Runs starting after '{start_time}' and before '{end_time}'")
    print(table_of_runs(r["data"]))

    # Find run(s) which match given metadata: given plan_name
    plan_name = "my_fly_plan"
    case_sensitive = False
    suffix = (
        "?page[offset]=0"
        # f"&filter[fulltext][condition][text]={plan_name}"
        # f"&filter[fulltext][condition][case_sensitive]={str(case_sensitive).lower()}"
        "&filter[eq][condition][key]=plan_name"
        f'&filter[eq][condition][value]="{plan_name}"'
        "&sort=time"
    )
    r = tiled_query(server, catalog, suffix=suffix)
    print(f"Runs that match 'plan_name={plan_name}'")
    print(table_of_runs(r["data"]))

    # With latest run:
    # Get overall metadata from this run.
    # What are the data streams in this run?
    # Get the data from the data stream named primary (the canonical main data).
    # What is the metadata for this stream?


if __name__ == "__main__":
    main()
