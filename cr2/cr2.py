#!/usr/bin/python
"""Compare runs 2

Second version of the compare runs script, to compare two traces of
the power allocator governor"""

import os
import csv, re
import pandas as pd

class CR2(pd.DataFrame):
    """A DataFrame-like class for storing benchmark results"""
    pass

def get_results(dirname="."):
    """Return a pd.DataFrame with the results

    The DataFrame has one row: "score" and as many columns as
    benchmarks were found.  For benchmarks that have a score
    result, that's what's used.  For benchmarks with FPS_* result,
    that's the score.  E.g. glbenchmark "score" is it's fps"""

    pat_result = re.compile("score|FPS_")
    res_dict = {}

    with open(os.path.join(dirname, "results.csv")) as fin:
        results = csv.reader(fin)

        for row in results:
            if (re.match(pat_result, row[3])):
                bench = row[0]
                result = int(row[4])

                if bench not in res_dict:
                    res_dict[bench] = [result]
                else:
                    res_dict[bench].append(result)

    for k in res_dict.keys():
        res_dict[k] = pd.Series(res_dict[k])

    return CR2(res_dict)

def combine_results(data, keys):
    """Combine two DataFrame results into one

    The data should be an array of results like the ones returned by
    get_results() or have the same structure.  The returned DataFrame
    has two column indexes.  The first one is still the benchmark and
    the second one is the key for the result.  keys must be an array
    of strings, each of which describes the same element in the data
    array.

    """

    combined = pd.concat(data, axis=1, keys=keys)

    # Now we've got everything in the DataFrame but the first column
    # index is the key for the result and the second one is the
    # benchmark. Swap the column indexes.  (There *has* to be a better
    # way of doing this)
    combined = combined.stack([1, 1]).unstack([1, 1])

    return CR2(combined)