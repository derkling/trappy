#    Copyright 2015-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Process the output of the cpu_cooling devices in the current
directory's trace.dat"""

import pandas as pd

from trappy.base import Base
from trappy.run import Run

def pivot_with_labels(dfr, data_col_name, new_col_name, mapping_label):
    """Pivot a DataFrame row into columns

    dfr is the DataFrame to operate on.  data_col_name is the name of
    the column in the DataFrame which contains the values.
    new_col_name is the name of the column in the DataFrame that will
    became the new columns.  mapping_label is a dictionary whose keys
    are the values in new_col_name and whose values are their
    corresponding name in the DataFrame to be returned.

    There has to be a more "pandas" way of doing this.

    Example:

    In [8]: dfr_in = pd.DataFrame({'cpus': ["000000f0", "0000000f", "000000f0", "0000000f"], 'freq': [1, 3, 2, 6]})

    In [9]: dfr_in
    Out[9]:
           cpus  freq
    0  000000f0     1
    1  0000000f     3
    2  000000f0     2
    3  0000000f     6

    [4 rows x 2 columns]

    In [10]: map_label = {"000000f0": "A15", "0000000f": "A7"}

    In [11]: power.pivot_with_labels(dfr_in, "freq", "cpus", map_label)
    Out[11]:
       A15  A7
    0    1 NaN
    1    1   3
    2    2   3
    3    2   6

    [4 rows x 2 columns]
    """

    col_set = set(dfr[new_col_name])

    ret_series = {}
    for col in col_set:
        try:
            label = mapping_label[col]
        except KeyError:
            available_keys = ", ".join(mapping_label.keys())
            error_str = '"{}" not found, available keys: {}'.format(col,
                                                                 available_keys)
            raise KeyError(error_str)
        data = dfr[dfr[new_col_name] == col][data_col_name]

        ret_series[label] = data

    return pd.DataFrame(ret_series).fillna(method="pad")

def num_cpus_in_mask(mask):
    """Return the number of cpus in a cpumask"""

    mask = mask.replace(",", "")
    value = int(mask, 16)

    return bin(value).count("1")

class CpuOutPower(Base):
    """Process the cpufreq cooling power actor data in a ftrace dump"""

    unique_word = "thermal_power_cpu_limit"
    name = "cpu_out_power"
    pivot = "cpus"

    def __init__(self):
        super(CpuOutPower, self).__init__(
            unique_word=self.unique_word,
        )

    def get_all_freqs(self, mapping_label):
        """get a DataFrame with the maximum frequencies allowed by the governor

        mapping_label must be a dictionary that maps cpumasks to name
        of the cpu.  Returned freqs are in MHz
        """

        dfr = self.data_frame

        return pivot_with_labels(dfr, "freq", "cpus", mapping_label) / 1000

Run.register_class(CpuOutPower, "thermal")

class CpuInPower(Base):
    """Process the cpufreq cooling power actor data in a ftrace dump"""

    unique_word = "thermal_power_cpu_get"
    name = "cpu_in_power"
    pivot = "cpus"

    def __init__(self):
        super(CpuInPower, self).__init__(
            unique_word=self.unique_word,
        )

    def _get_load_series(self):
        """get a pandas.Series with the aggregated load"""

        dfr = self.data_frame
        load_cols = [s for s in dfr.columns if s.startswith("load")]

        load_series = dfr[load_cols[0]].copy()
        for col in load_cols[1:]:
            load_series += dfr[col]

        return load_series

    def get_load_data(self, mapping_label):
        """return a dataframe suitable for plot_load()

        mapping_label is a dictionary mapping cluster cpumasks to labels."""

        dfr = self.data_frame
        load_series = self._get_load_series()
        load_dfr = pd.DataFrame({"cpus": dfr["cpus"], "load": load_series})

        return pivot_with_labels(load_dfr, "load", "cpus", mapping_label)

    def get_normalized_load_data(self, mapping_label):
        """return a dataframe for plotting normalized load data

        mapping_label should be a dictionary mapping cluster cpumasks
        to labels

        """

        dfr = self.data_frame
        load_series = self._get_load_series()

        load_series *= dfr['freq']
        for cpumask in mapping_label:
            num_cpus = num_cpus_in_mask(cpumask)
            idx = dfr["cpus"] == cpumask
            max_freq = max(dfr[idx]["freq"])
            load_series[idx] = load_series[idx] / (max_freq * num_cpus)

        load_dfr = pd.DataFrame({"cpus": dfr["cpus"], "load": load_series})

        return pivot_with_labels(load_dfr, "load", "cpus", mapping_label)

    def get_all_freqs(self, mapping_label):
        """get a DataFrame with the "in" frequencies as seen by the governor

        Frequencies are in MHz
        """

        dfr = self.data_frame

        return pivot_with_labels(dfr, "freq", "cpus", mapping_label) / 1000

Run.register_class(CpuInPower, "thermal")
