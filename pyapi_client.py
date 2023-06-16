"""
Demo of a tiled Python client using the tiled.client Python API.

Use this Python client to generate requests from the tiled server.
Then, inspect the server's logs for the specific URIs that were used.

Produce some specific URI queries and responses.

* [x] Find all runs in a catalog between these two ISO8601 dates.
* [x] Find run(s) which match given metadata.
* [ ] Get overall metadata from given run.
* [ ] What are the data streams in this run?
* [ ] What is the metadata for this stream?
* [ ] Get the data from the data stream named primary (the canonical main data).
* [ ] What about loose matches?  Maybe not now.  Might require some deeper expertise.
"""

import datetime
from tiled.client import from_uri
from tiled.client.cache import Cache
from tiled.utils import tree
import tiled.queries


def overview(host="localhost", port=8000):
    client = from_uri(f"http://{host}:{port}", cache=Cache.in_memory(2e9))
    print(f"{client=}")
    for catalog in client:
        print(f"{catalog=}  {client[catalog]=}")
        print(f"{client.search(tiled.queries.FullText('bdp'))}")
    # tree(client)


def demo2(host="localhost", port=8000):
    client = from_uri(f"http://{host}:{port}", cache=Cache.in_memory(2e9))
    # cat = client["20idb_usaxs"]
    cat = client["class_2021_03"]
    print(f"{cat=}")

    def iso2time(isotime):
        return datetime.datetime.timestamp(datetime.datetime.fromisoformat(isotime))
    def QueryTimeFrom(isotime):
        return tiled.queries.Key("time") >= iso2time(isotime)
    def QueryTimeUntil(isotime):
        return tiled.queries.Key("time") < iso2time(isotime)

    # Find all runs in the catalog between these two ISO8601 dates.
    start_time = "2021-03-17 00:30"
    end_time = "2021-05-19 15:15"
    cat = cat.search(QueryTimeFrom(start_time)).search(QueryTimeUntil(end_time))
    print(f"{cat=}")

    # Find run(s) which match given metadata: given plan_name
    plan_name = "rel_scan"
    # case_sensitive = False
    # runs = cat.search(tiled.queries.FullText(plan_name), case_sensitive=case_sensitive)
    cat = cat.search(tiled.queries.Key("plan_name") == plan_name)
    print(f"{cat=}")

    # With latest run:
    run = cat.values()[-1]
    print(f"last run: {run=}")

    # Get overall metadata from this run.
    print(f"Run metadata: {run.metadata=}")

    # What are the data streams in this run?
    stream_names = run.metadata["summary"]["stream_names"]
    print(f"streams: {stream_names=}")

    # Get the data from the data stream named primary (the canonical main data).
    if "primary" in stream_names:
        stream_data = run["primary"]
        print(f"{stream_data['data']=}")
        # What is the metadata for this stream?
        print(f"{stream_data.metadata=}")

    ideas_from_json_api = {
        "queries": [
            "fulltext",
            "lookup",
            "keys_filter",
            "regex",
            "eq",
            "noteq",
            "comparison",
            "contains",
            "in",
            "notin",
            "specs",
            "structure_family",
            "scan_id",
            "scan_id_range",
            "partial_uid",
            "duration",
            "time_range",
        ]
    }


def get_run(catalog, uid, host="localhost", port=8000):
    client = from_uri(f"http://{host}:{port}", cache=Cache.in_memory(2e9))
    return client[catalog][uid]


def get_run_data(catalog, uid, host="localhost", port=8000):
    run = get_run(catalog, uid, host=host, port=port)

    # for k, v in run.primary.data.items():
    #     print(f"{k=} {v.shape=}  {v.size=}  {len(v)=}")
    #     data = v.read()  # a really big bite for the image data!
    #     # /api/v1/array/block
    #     # /{catalog}
    #     # /{uid}
    #     # /{stream}
    #     # /data/adsimdet_image
    #     # ?block=0,0,0,0
    #     # &format=application/octet-stream

    # http://localhost:8000/api/v1/array/block/bdp2022/00714a91-c33e-4e7b-90fd-2e8f385bebc9/primary/data/adsimdet_image?block=0,0,0,0

    return run


def some_run_data(host="localhost", port=8000):
    # run = get_run_data(
    #     "bdp2022", "00714a91-c33e-4e7b-90fd-2e8f385bebc9", host=host, port=port
    # )
    run = get_run_data(
        "bdp2022", "43044b6e-f6ba-48cb-a975-90d236dcbaaa", host=host, port=port
    )
    print(f"{run.metadata=}")
    print(f"{run.primary.metadata=}")
    print(f"{list(run.primary.data.keys())=}")
    signal_name = "time"  # or adsimdet_image which has shape [1, 1, 1024, 1024]
    arr = run.primary.data["time"]
    print(f"{type(arr)=}")
    print(f"{arr=}")


def external_files(catalog, uid, host="localhost", port=8000):
    run = get_run(catalog, uid, host=host, port=port)
    docs = [doc for name, doc in run.documents() if name in ('resource', 'datum_page')]
    print(f"{len(docs)=}")


def main():
    r = external_files("bdp2022", "43044b6e-f6ba-48cb-a975-90d236dcbaaa")
    print(f"{r=}")


if __name__ == "__main__":
    # main()
    demo2()
