# (C) British Crown Copyright 2010 - 2015, Met Office
#
# This file is part of Iris.
#
# Iris is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Iris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Iris.  If not, see <http://www.gnu.org/licenses/>.
"""
A script to convert the standard names information from the provided XML
file into a Python dictionary format.

Takes two arguments: the first is the XML file to process and the second
is the name of the file to write the Python dictionary file into.

By default, Iris will use the source XML file:
    etc/cf-standard-name-table.xml
as obtained from:
    http://cf-pcmdi.llnl.gov/documents/cf-standard-names

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six

import argparse
import pprint
import xml.etree.ElementTree as ET


STD_VALUES_FILE_TEMPLATE = '''
# (C) British Crown Copyright 2010 - 2015, Met Office
#
# This file is part of Iris.
#
# Iris is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Iris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Iris.  If not, see <http://www.gnu.org/licenses/>.
"""
This file contains a dictionary of standard value names that are mapped
to another dictionary of other standard name attributes. Currently only
the `canonical_unit` exists in these attribute dictionaries.

This file is automatically generated. Do not edit this file by hand.

The file will be generated during a standard build/installation:
    python setup.py build
    python setup.py install

Also, the file can be re-generated in the source distribution via:
    python setup.py std_names

Or for more control (e.g. to use an alternative XML file) via:
    python tools/generate_std_names.py XML_FILE MODULE_FILE

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa


STD_NAMES = '''.lstrip()


def process_name_table(tree, element_name, *child_elements):
    """
    Yields a series of dictionaries with the key being the id of the entry element and the value containing
    another dictionary mapping other attributes of the standard name to their values, e.g. units, description, grib value etc.
    """
    for elem in tree.iterfind(element_name):
        sub_section = {}

        for child_elem in child_elements:
            found_elem = elem.find(child_elem)
            sub_section[child_elem] = found_elem.text if found_elem is not None else None

        yield {elem.get("id") : sub_section}


def to_dict(infile, outfile):
    values = {}
    aliases = {}

    tree = ET.parse(infile)

    for section in process_name_table(tree, 'entry', 'canonical_units'):
        values.update(section)

    for section in process_name_table(tree, 'alias', 'entry_id'):
        aliases.update(section)

    for key, valued in six.iteritems(aliases):
        values.update({
                key : {'canonical_units' : values.get(valued['entry_id']).get('canonical_units')}
            })

    outfile.write(STD_VALUES_FILE_TEMPLATE + pprint.pformat(values))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create Python code from CF standard name XML.')
    parser.add_argument('input', metavar='INPUT',
                        help='Path to CF standard name XML')
    parser.add_argument('output', metavar='OUTPUT',
                        help='Path to resulting Python code')
    args = parser.parse_args()

    if six.PY2:
        encoding = {}
    else:
        encoding  = {'encoding': 'utf-8'}

    with open(args.input, 'r', **encoding) as in_fh:
        with open(args.output, 'w', **encoding) as out_fh:
            to_dict(in_fh, out_fh)
