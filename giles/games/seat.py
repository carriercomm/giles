# Giles: seat.py
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

from giles.state import State

class Seat(object):
    """A seat at a game.  Seats can be named, be active or inactive, and
    have players or not.
    """

    def __init__(self, name):

        self.display_name = name
        self.name = name.lower()
        self.active = False
        self.player = None

    def sit(self, player, activate = True):

        # By default, sitting a player down in a seat activates that
        # seat.  That can be overridden.

        if not self.player:
            self.player = player
            if activate:
                self.active = True
            return True
        return False

    def stand(self):

        if self.player:
            self.player = None
            return True
        return False