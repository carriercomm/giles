# Giles: utils.py
# Copyright 2012 Phil Bordelon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def booleanize(msg):
    # This returns:
    # -1 for False
    # 1 for True
    # 0 for invalid input.

    if type(msg) != str:
        return 0

    msg = msg.strip().lower()
    if (msg == "on" or msg == "true" or msg == "yes" or msg == "y"
       or msg == "t" or msg == "1"):
        return 1
    elif (msg == "off" or msg == "false" or msg == "no" or msg == "n"
       or msg == "f" or msg == "0"):
        return -1

    return 0