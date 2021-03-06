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


"""The idea is to create a wrapper class that
returns a Type of a Class dynamically created based
on the input parameters. Similar to a factory design
pattern
"""
from trappy.base import Base
import re
from trappy.run import Run


def default_init(self):
    """Default Constructor for the
       Dynamic MetaClass
    """

    super(type(self), self).__init__(
        unique_word=self.unique_word,
        parse_raw=self.parse_raw
    )


class DynamicTypeFactory(type):

    """Override the type class to create
       a dynamic type on the fly
    """

    def __new__(mcs, name, bases, dct):
        """Override the new method"""
        return type.__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        """Override the constructor"""
        super(DynamicTypeFactory, cls).__init__(name, bases, dct)


def _get_name(name):
    """Internal Method to Change camelcase to
       underscores. CamelCase -> camel_case
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()


def register_dynamic(class_name, unique_word, scope="all",
                     parse_raw=False):
    """Create a Dynamic Type and register
       it with the trappy Framework"""

    dyn_class = DynamicTypeFactory(
        class_name, (Base,), {
            "__init__": default_init,
            "unique_word": unique_word,
            "name": _get_name(class_name),
            "parse_raw" : parse_raw
        }
    )
    Run.register_class(dyn_class, scope)
    return dyn_class


def register_class(cls):
    """Register a new class implementation
       Should be used when the class has
       complex helper methods and does not
       expect to use the default constructor
    """

    # Check the argspec of the class
    Run.register_class(cls)
