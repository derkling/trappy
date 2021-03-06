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

"""
The EventPlot is used to represent Events with two characteristics:

    * A name, which determines the colour on the plot
    * A lane, which determines the lane in which the event occurred

In the case of a cpu residency plot, the term lane can be equated to
a CPU and the name attribute can be the PID of the task
"""

from trappy.plotter import AttrConf
import uuid
import json
import os
from IPython.display import display, HTML
from trappy.plotter.AbstractDataPlotter import AbstractDataPlotter

if not AttrConf.PLOTTER_IPYTHON:
    raise ImportError("Ipython Environment not Found")

# pylint: disable=R0201
# pylint: disable=R0921
# Initialize Resources
from trappy.plotter import Utils
Utils.iplot_install("EventPlot")


class EventPlot(AbstractDataPlotter):

    """EventPlot Class that extends
       AbstractDataPlotter"""

    def __init__(
            self,
            data,
            keys,
            lane_prefix,
            num_lanes,
            domain,
            summary=True,
            stride=False):
        """
            Args:
                data: Data of the format:
                   { "<name1>" : [
                                    [event_start, event_end, lane],
                                    .
                                    .
                                    [event_start, event_end, lane],
                                 ],
                     .
                     .
                     .

                     "<nameN>" : [
                                    [event_start, event_end, lane],
                                    .
                                    .
                                    [event_start, event_end, lane],
                                 ],
                    }
                keys: List of unique names in the data dictionary
                lane_prefix: A string prefix to be used to name each lane
                num_lanes: Total number of expected lanes
                domain: Domain of the event data
                stride: Stride can be used if the trace is very large.
                        It results in sampled rendering
        """

        self._fig_name = self._generate_fig_name
        self._html = []
        self._fig_name = self._generate_fig_name()
        avgFunc = lambda x: sum([(evt[1] - evt[0]) for evt in x]) / len(x)
        avg = {k: avgFunc(v) for k, v in data.iteritems()}
        graph = {}
        graph["data"] = data
        graph["lanes"] = self._get_lanes(lane_prefix, num_lanes)
        graph["xDomain"] = domain
        graph["keys"] = sorted(avg, key=lambda x: avg[x], reverse=True)
        graph["showSummary"] = summary
        graph["stride"] = AttrConf.EVENT_PLOT_STRIDE

        json_file = os.path.join(
            AttrConf.PLOTTER_STATIC_DATA_DIR,
            self._fig_name +
            ".json")

        with open(json_file, "w") as json_fh:
            json.dump(graph, json_fh)

        # Initialize the HTML, CSS and JS Components
        self._add_css()
        self._init_html()

    def view(self):
        """Views the Graph Object"""
        display(HTML(self.html()))

    def savefig(self, path):
        """Save the plot in the provided path"""

        raise NotImplementedError(
            "Save is not currently implemented for EventPlot")

    def _get_lanes(self, lane_prefix, num_lanes):
        """Populate the lanes for the plot"""

        lanes = []
        for idx in range(num_lanes):
            lanes.append({"id": idx, "label": "{}{}".format(lane_prefix, idx)})
        return lanes

    def _generate_fig_name(self):
        """Generate a unqiue name for the figure"""

        fig_name = "fig_" + uuid.uuid4().hex
        return fig_name

    def _init_html(self):
        """Initialize HTML for the plot"""
        div_js = """
        <script>
            var req = require.config( {

                paths: {

                    "EventPlot": "/static/plotter_scripts/EventPlot/EventPlot",
                    "d3-tip": "/static/plotter_scripts/EventPlot/d3.tip.v0.6.3",
                    "d3": "/static/plotter_scripts/EventPlot/d3.v3.min"
                },
                shim: {
                    "d3-tip": ["d3"],
                    "EventPlot": {

                        "deps": ["d3-tip", "d3" ],
                        "exports":  "EventPlot"
                    }
                }
            });
            req(["require", "EventPlot"], function() {
               EventPlot.generate('""" + self._fig_name + """');
            });
        </script>
        """

        self._html.append(
            '<div id="{}" class="eventplot">{}</div>'.format(self._fig_name,
                                                             div_js))

    def _add_css(self):
        """Append the CSS to the HTML code generated"""

        base_dir = os.path.dirname(os.path.realpath(__file__))
        css_file = os.path.join(base_dir, "css/EventPlot.css")
        css_fh = open(css_file, 'r')
        self._html.append("<style>")
        self._html += css_fh.readlines()
        self._html.append("</style>")
        css_fh.close()

    def html(self):
        """Return a Raw HTML string for the plot"""

        return "\n".join(self._html)
