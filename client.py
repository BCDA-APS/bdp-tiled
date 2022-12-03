"""
Simple tiled Python client to list most recent scans from catalogs.
"""

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


def main():
    table = pyRestTable.Table()
    table.labels = "catalog scan_id date/time duration,s plan_name title ESAF_id".split()

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
                    esaf_id
                )
            )

    print(table)


if __name__ == "__main__":
    main()
