"""
Demo of a tiled Python client using the tiled Python API.

Use this Python client to genereate requests from the tiled server.
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

from tiled.client import from_uri
from tiled.client.cache import Cache
import tiled.queries
from tiled.utils import tree


def overview(host="localhost", port=8000):
    client = from_uri(f"http://{host}:{port}", cache=Cache.in_memory(2e9))
    print(f"{client=}")
    for catalog in client:
        print(f"{catalog=}  {client[catalog]=}")
        print(f"{client.search(FullText('bdp'))}")
    # tree(client)


def main(host="localhost", port=8000):
    client = from_uri(f"http://{host}:{port}", cache=Cache.in_memory(2e9))
    cat = client["20idb_usaxs"]

    # Find all runs in a catalog between these two ISO8601 dates.
    start_time = "2022-12-01 15:01"
    end_time = "2022-12-01 16:45"

    # Find run(s) which match given metadata: given plan_name
    plan_name = "my_fly_plan"
    case_sensitive = False
    # runs = cat.search(tiled.queries.FullText(plan_name), case_sensitive=case_sensitive)
    runs = cat.search(tiled.queries.Key("plan_name") == plan_name)
    print(f"{runs=}")

    # With latest run:
    # Get overall metadata from this run.
    # What are the data streams in this run?
    # Get the data from the data stream named primary (the canonical main data).
    # What is the metadata for this stream?

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


if __name__ == "__main__":
    main()
