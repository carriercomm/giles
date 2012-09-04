# Giles: whist.py
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

from giles.games.game import Game
from giles.games.hand import Hand
from giles.games.playing_card import new_deck, str_to_card, card_to_str, SHORT, LONG, HEARTS, DIAMONDS
from giles.games.seat import Seat
from giles.games.trick import handle_trick, hand_has_suit, sorted_hand
from giles.state import State
from giles.utils import Struct

class Whist(Game):
    """A Whist game table implementation.  Whist came about sometime in the
    18th century.  This implementation does not (currently) score honours,
    because honours are boring.
    """

    def __init__(self, server, table_name):

        super(Whist, self).__init__(server, table_name)

        self.game_display_name = "Whist"
        self.game_name = "whist"
        self.seats = [
            Seat("North"),
            Seat("East"),
            Seat("South"),
            Seat("West"),
        ]

        self.min_players = 4
        self.max_players = 4
        self.state = State("need_players")
        self.prefix = "(^RWhist^~): "
        self.log_prefix = "%s/%s: " % (self.table_display_name, self.game_display_name)

        # Whist-specific guff.
        self.ns = Struct()
        self.ns.score = 0
        self.ew = Struct()
        self.ew.score = 0

        self.goal = 5
        self.trick = None
        self.trump_suit = None
        self.led_suit = None
        self.turn = None
        self.dealer = None
        self.winner = None

    def show_help(self, player):

        super(Whist, self).show_help(player)
        player.tell_cc("\nWHIST SETUP PHASE:\n\n")
        player.tell_cc("          ^!setup^., ^!config^., ^!conf^.     Enter setup phase.\n")
        player.tell_cc("            ^!goal^. <num>, ^!score^.     Set the goal score to <num>.\n")
        player.tell_cc("            ^!ready^., ^!done^., ^!r^., ^!d^.     End setup phase.\n")
        player.tell_cc("\nWHIST PLAY:\n\n")
        player.tell_cc("              ^!play^. <card>, ^!pl^.     Play <card> from your hand.\n")
        player.tell_cc("                 ^!hand^., ^!inv^., ^!i^.     Look at the cards in your hand.\n")

    def get_point_str(self, num):

        if num == 1:
            return "1 point"
        return "%d points" % num

    def display(self, player):

        if not self.turn:
            player.tell_cc("   A shuffled deck of playing cards lies face-down on the table.\n")
        else:
            if self.turn == self.seats[0]:
                mid_chars = "^^^^"
            elif self.turn == self.seats[1]:
                mid_chars = ">>"
            elif self.turn == self.seats[2]:
                mid_chars = "vv"
            else:
                mid_chars = "<<"
            to_print = "\n                  ^RNN^~\n\n"
            to_print += "                  %s\n\n" % card_to_str(self.seats[0].data.card)
            to_print += "          ^MWW^~  %s  %s  %s  ^MEE^~\n\n" % (card_to_str(self.seats[3].data.card), mid_chars, card_to_str(self.seats[1].data.card))
            to_print += "                  %s\n\n" % card_to_str(self.seats[2].data.card)
            to_print += "                  ^RSS^~\n\n"
            player.tell_cc(to_print)

    def get_metadata(self):

        to_return = "\n\n"
        if self.turn:
            if self.turn == self.seats[0] or self.turn == self.seats[2]:
                seat_color = "^R"
            else:
                seat_color = "^M"
            to_return = "It is ^Y%s^~'s turn (%s%s^~).  Trumps are ^C%s^~.\n" % (self.turn.player_name, seat_color, self.turn, self.trump_suit)
            to_return += "Tricks:   ^RNorth/South^~: %d    ^MEast/West^~: %d\n" % (self.ns.tricks, self.ew.tricks)
        to_return += "The goal score for this game is ^C%s^~.\n" % self.get_point_str(self.goal)
        to_return += "          ^RNorth/South^~: %d    ^MEast/West^~: %d\n" % (self.ns.score, self.ew.score)

        return to_return

    def show(self, player):
        self.display(player)
        player.tell_cc(self.get_metadata())

    def set_goal(self, player, goal_str):

        if not goal_str.isdigit():
            self.tell_pre(player, "You didn't even send a number!\n")
            return False

        new_goal = int(goal_str)
        if new_goal < 1:
            self.tell_pre(player, "The goal must be at least one point.\n")
            return False

        # Got a valid goal.
        self.goal = new_goal
        self.bc_pre("^M%s^~ has changed the goal to ^G%s^~.\n" % (player, self.get_point_str(new_goal)))

    def clear_trick(self):

        # Set the current trick to an empty hand...
        self.trick = Hand()
        self.led_suit = None

        # ...and set everyone's played card to None.
        for seat in self.seats:
            seat.data.card = None

    def new_deal(self):

        dealer_name = self.dealer.player_name

        self.bc_pre("^R%s^~ (^C%s^~) gives the cards a good shuffle...\n" % (dealer_name, self.dealer))
        deck = new_deck()
        deck.shuffle()

        # Deal out all of the cards.  We'll flip the last one; that determines
        # the trump suit for the hand.
        self.bc_pre("^R%s^~ deals the cards out to all the players.\n" % dealer_name)
        for seat in self.seats:
            seat.data.hand = Hand()
        for i in range(13):
            for seat in self.seats:
                this_card = deck.discard()
                if i == 12 and seat == self.dealer:

                    # Trump determiner.  Show it to everyone and set the trump suit.
                    self.bc_pre("^R%s^~ flips their last card; it is ^C%s^~.\n" % (dealer_name,
                       card_to_str(this_card, LONG)))
                    self.trump_suit = this_card.suit

                seat.data.hand.draw(this_card)

        # Sort everyone's hands.
        for seat in self.seats:
            seat.data.hand = sorted_hand(seat.data.hand, self.trump_suit)

        # Show everyone their hands.
        for seat in self.seats:
            if seat.player:
                self.show_hand(seat.player)

        # Set the trick counts to zero.
        self.ns.tricks = 0
        self.ew.tricks = 0

    def show_hand(self, player):

        seat = self.get_seat_of_player(player)

        if not seat:
            self.tell_pre(player, "You're not playing!\n")
            return

        print_str = "\nYour current hand:\n   "
        last_suit = None
        for card in seat.data.hand:
            if card.suit != last_suit:
                if last_suit:
                   print_str += "/ "
                last_suit = card.suit
            if card.suit == self.trump_suit:
                color_code = "^W"
            elif card.suit == HEARTS or card.suit == DIAMONDS:
                color_code = "^R"
            else:
                color_code = "^w"
            print_str += "%s%s^~ " % (color_code, card_to_str(card))
        print_str += "\n"
        self.tell_pre(player, print_str)

    def play(self, player, play_str):

        seat = self.get_seat_of_player(player)
        if not seat:
            self.tell_pre(player, "You're not playing!\n")
            return False

        elif seat != self.turn:
            self.tell_pre(player, "It's not your turn!\n")
            return False

        # Translate the play string into an actual card.
        potential_card = str_to_card(play_str)

        if not potential_card:
            self.tell_pre(player, "That's not a valid card!\n")
            return False

        # Do they even have this card?
        if potential_card not in seat.data.hand:
            self.tell_pre(player, "You don't have that card!\n")
            return False

        # Okay, it's a card in their hand.  First, let's do the "follow the
        # led suit" business.
        action_str = "^Wplays^~"
        if self.led_suit:

            this_suit = potential_card.suit
            if (this_suit != self.led_suit and
               hand_has_suit(seat.data.hand, self.led_suit)):

                # You can't play off-suit if you can match the led suit.
                self.tell_pre(player, "You can't throw off; you have the led suit.\n")
                return False

        else:

            # No led suit; they're the leader.
            action_str = "^Yleads^~ with"
            self.led_suit = potential_card.suit

        # They either matched the led suit, didn't have any of it, or they
        # are themselves the leader.  Nevertheless, their play is valid.
        seat.data.card = potential_card
        self.trick.draw(seat.data.hand.discard_specific(potential_card))
        self.bc_pre("^G%s^~ (^C%s^~) %s ^C%s^~.\n" % (seat.player_name, seat, action_str, card_to_str(potential_card, LONG)))
        return potential_card

    def tick(self):

        # If all seats are full and active, autostart.
        if (self.state.get() == "need_players" and self.seats[0].player and
           self.seats[1].player and self.seats[2].player and
           self.seats[3].player and self.active):
            self.state.set("playing")
            self.bc_pre("The game has begun.\n")

            # Initialize everything by clearing the (non-existent) trick.
            self.clear_trick()

            # Make a new deal.
            self.dealer = self.seats[0]
            self.new_deal()

            # Eldest leads to the first trick.
            self.turn = self.next_seat(self.dealer)

    def handle(self, player, command_str):

        # Handle common commands.
        handled = self.handle_common_commands(player, command_str)

        if not handled:

            state = self.state.get()

            command_bits = command_str.split()
            primary = command_bits[0].lower()

            if state == "setup":

                if primary in ("goal", "score", "sc", "g",):
                    if len(command_bits) == 2:
                        self.set_goal(player, command_bits[1])
                    else:
                        self.tell_pre(player, "Invalid goal command.\n")
                    handled = True

                elif primary in ("done", "ready", "d", "r",):
                    self.bc_pre("The game is now looking for players.\n")
                    self.state.set("need_players")
                    handled = True

            elif state == "need_players":

                if primary in ("config", "setup", "conf",):
                    self.state.set("setup")
                    self.bc_pre("^R%s^~ has switched the game to setup mode.\n" % player)
                    handled = True

            elif state == "playing":

                card_played = False
                if primary in ("hand", "inventory", "inv", "i",):
                    self.show_hand(player)
                    handled = True

                elif primary in ("play", "move", "pl", "mv",):
                    if len(command_bits) == 2:
                        card_played = self.play(player, command_bits[1])
                    else:
                        self.tell_pre(player, "Invalid play command.\n")
                    handled = True

                if card_played:

                    # A card hit the table.  We need to do stuff.
                    if len(self.trick) == 4:

                        # Finish the trick up.
                        self.finish_trick()

                        # Is that the last trick of this hand?
                        if self.ns.tricks + self.ew.tricks == 13:

                            # Yup.  Finish the hand up.
                            self.finish_hand()

                            # Did someone win the overall game?
                            winner = self.find_winner()
                            if winner:

                                # Yup.  Finish.
                                self.resolve(winner)
                                self.finish()

                            else:

                                # Nope.  Pass the deal to the next dealer...
                                self.dealer = self.next_seat(self.dealer)

                                # Deal and set up the first player.
                                self.new_deal()
                                self.turn = self.next_seat(self.dealer)
                    else:

                        # Trick not over.  Rotate.
                        self.turn = self.next_seat(self.turn)

        if not handled:
            self.tell_pre(player, "Invalid command.\n")

    def finish_trick(self):

        # Okay, we have a trick with four cards.  Which card won?
        winner = handle_trick(self.trick, self.trump_suit)

        # This /should/ just return one seat...
        winning_seat_list = [x for x in self.seats if x.data.card == winner]

        if len(winning_seat_list) != 1:
            self.server.log.log(self.log_prefix + "Something went horribly awry; trick ended without a finish.")
            self.bc_pre("Something went horribly wrong; no one won the trick!  Tell the admin.\n")
            return

        winning_seat = winning_seat_list[0]

        # Print information about the winning card.
        self.bc_pre("^G%s^~ wins the trick with ^C%s^~.\n" % (winning_seat.player_name, card_to_str(winner, LONG)))

        # Give the trick to the correct partnership.
        if winning_seat == self.seats[0] or winning_seat == self.seats[2]:
            self.ns.tricks += 1
        else:
            self.ew.tricks += 1

        # Set the next leader to the player who won.
        self.turn = winning_seat

        # Clear the trick.
        self.clear_trick()

    def finish_hand(self):

        # Which side won more than 6 tricks?
        if self.ns.tricks > 6:
            winning_side = "^RNorth/South^~"
            addend = self.ns.tricks - 6
            self.ns.score += addend
        else:
            winning_side = "^MEast/West^~"
            addend = self.ew.tricks - 6
            self.ew.score += addend

        # Let everyone know.
        self.bc_pre("%s wins the hand and gains ^C%s^~.\n" % (winning_side, self.get_point_str(addend)))

    def find_winner(self):

        # Easy: has one of the sides reached a winning score?
        if self.ns.score >= self.goal:
            return self.ns
        elif self.ew.score >= self.goal:
            return self.ew

        return None

    def resolve(self, winning_partnership):

        if self.ns == winning_partnership:
            name_one = self.seats[0].player_name
            name_two = self.seats[2].player_name
        else:
            name_one = self.seats[1].player_name
            name_two = self.seats[3].player_name
        self.bc_pre("^G%s^~ and ^G%s^~ win!\n" % (name_one, name_two))
