import tkinter as tk
import re

from random import randint


# Default settings of the game
DEFAULT_GAME_WIDTH = 6
DEFAULT_GAME_HEIGHT = 6
DEFAULT_BOT_TACTIC = 1 # 0 = First empty # 1 = Random empty
TAKE_OBLIQUELY = False # Bere i políčka šikmo? True/False

# Canvas/GUI settings
DEFAULT_FIELD_SIZE = 60  # In Pixels X*Y
MINSIZE_WINDOW = (800, 640)  # In Pixels


class FieldStates:
    EMPTY = 0
    GRABBED = 1
    PLAYER = 2


# Initializing corresponding colors to each FieldState
FIELD_COLORS = {
    FieldStates.EMPTY: "white",
    FieldStates.GRABBED: "gray",
    FieldStates.PLAYER: "lightgray",
}


class Player:
    def __init__(self, game, name="Player"):
        self.game = game
        self.name = name
        self.game.players.append(self)  # Add self to the self.players list / game

    def __str__(self):
        return "Player"


class Bot(Player):
    def __init__(self, game, name="Bot", tactic=None):
        Player.__init__(self, game)
        self.name = name + str(len(self.game.players))
        if tactic == None:
            self.tactic = DEFAULT_BOT_TACTIC
        else:
            self.tactic = tactic

    def play(self):
        if self.tactic == 0:
            self.play_strategy_first_empty()
        elif self.tactic == 1:
            self.play_strategy_random_empty()

    def play_strategy_first_empty(self):
        for y in range(self.game.height.get()):
            for x in range(self.game.width.get()):
                if self.game.matrix[y][x] == FieldStates.EMPTY:
                    self.game.grab_field(x, y)
                    return

    def play_strategy_random_empty(self):
        empty_fields = []

        for y in range(self.game.height.get()):
            for x in range(self.game.width.get()):
                if self.game.matrix[y][x] == FieldStates.EMPTY:
                    empty_fields.append((x, y))

        if len(empty_fields) <= 0:
            return

        coords = empty_fields[randint(0, len(empty_fields) - 1)]
        self.game.grab_field(coords[0], coords[1])

    def __str__(self):
        return "Bot"


class BlockingGame(tk.Tk):
    def __init__(self, title="BlockingGame"):
        tk.Tk.__init__(self)

        self.title(title)  # Sets window's title
        self.minsize(
            MINSIZE_WINDOW[0], MINSIZE_WINDOW[1]
        )  # Sets min-size of the window [pixels]
        self.resizable(False, False)

        # The GUI:
        self.__start_game_pc_button = tk.Button(
            self, text="Start Game PC", command=self.start_game_pc
        )

        self.__start_game_players_button = tk.Button(
            self, text="Start Game Players", command=self.start_game_players
        )

        self.__game_width_label = tk.Label(self, text="Width")

        self.width = tk.IntVar(
            value=DEFAULT_GAME_WIDTH
        )  # This var is binded to the Spinbox Widget

        self.__game_width_entry = tk.Spinbox(
            self, width=5, from_=3, to=13, textvariable=self.width
        )

        self.__game_height_label = tk.Label(self, text="Height")

        self.height = tk.IntVar(value=DEFAULT_GAME_HEIGHT)

        self.__game_height_entry = tk.Spinbox(
            self, width=5, from_=3, to=10, textvariable=self.height
        )

        self.__player_on_turn_label = tk.Label(self, text="Player on turn:")

        self.__canvas = tk.Canvas(
            self, width=MINSIZE_WINDOW[0], height=MINSIZE_WINDOW[1]
        )

        # Grid settings
        val_padding = 3

        # Grid
        self.__start_game_pc_button.grid(
            row=0, column=0, padx=val_padding, pady=val_padding
        )

        self.__start_game_players_button.grid(
            row=0, column=1, padx=val_padding, pady=val_padding
        )

        self.__game_width_label.grid(
            row=1, column=1, padx=val_padding, pady=val_padding, sticky="W"
        )

        self.__game_width_entry.grid(
            row=1, column=0, padx=val_padding, pady=val_padding, sticky="E"
        )

        self.__game_height_label.grid(
            row=2, column=1, padx=val_padding, pady=val_padding, sticky="W"
        )

        self.__game_height_entry.grid(
            row=2, column=0, padx=val_padding, pady=val_padding, sticky="E"
        )

        self.__player_on_turn_label.grid(
            row=3,
            column=0,
            padx=val_padding,
            pady=val_padding,
            sticky="W",
            columnspan=2,
        )

        self.__canvas.grid(row=5, column=0, columnspan=2)

        self.init_game()

    def init_game(self):
        self.players = []  # Initializing list of players
        self.captured_player_fields = {}
        self.matrix = []
        self.field_size = DEFAULT_FIELD_SIZE
        self.turns = 0

    def run(self):
        self.mainloop()

    def on_field_click(self, event):
        """This is on_click event of each square that's drawn on the canvas"""
        current = event.widget.find_withtag("current")
        tag_str = str(event.widget.itemconfig(current)["tags"])
        match = re.search(r".*?\{(.*)}.*", tag_str)
        coords = match.group(1).split(";")
        x, y = int(coords[1]), int(coords[0])
        self.grab_field(x, y)  #  Grab field on click (Player)

    def is_any_field_empty(self) -> bool:
        """This function goes through the list and checks if any field is EMPTY, if yes returns True, else False"""
        for y in range(self.height.get()):
            for x in range(self.width.get()):
                if self.matrix[y][x] == FieldStates.EMPTY:
                    return True
        return False

    def grab_field(self, x, y):
        if self.matrix[y][x] == FieldStates.EMPTY:
            self.matrix[y][x] = FieldStates.PLAYER

            if x - 1 >= 0 and self.matrix[y][x - 1] != FieldStates.PLAYER:
                self.matrix[y][x - 1] = FieldStates.GRABBED

            if (
                x + 1 <= self.width.get() - 1
                and self.matrix[y][x + 1] != FieldStates.PLAYER
            ):
                self.matrix[y][x + 1] = FieldStates.GRABBED

            if y - 1 >= 0:
                if self.matrix[y - 1][x] != FieldStates.PLAYER:
                    self.matrix[y - 1][x] = FieldStates.GRABBED

                if (
                    x - 1 >= 0
                    and TAKE_OBLIQUELY
                    and self.matrix[y - 1][x - 1] != FieldStates.PLAYER
                ):
                    self.matrix[y - 1][x - 1] = FieldStates.GRABBED

                if (
                    x + 1 <= self.width.get() - 1
                    and TAKE_OBLIQUELY
                    and self.matrix[y - 1][x + 1] != FieldStates.PLAYER
                ):
                    self.matrix[y - 1][x + 1] = FieldStates.GRABBED

            if y + 1 <= self.height.get() - 1:
                if self.matrix[y + 1][x] != FieldStates.PLAYER:
                    self.matrix[y + 1][x] = FieldStates.GRABBED

                if (
                    x - 1 >= 0
                    and TAKE_OBLIQUELY
                    and self.matrix[y + 1][x - 1] != FieldStates.PLAYER
                ):
                    self.matrix[y + 1][x - 1] = FieldStates.GRABBED

                if (
                    x + 1 <= self.width.get() - 1
                    and TAKE_OBLIQUELY
                    and self.matrix[y + 1][x + 1] != FieldStates.PLAYER
                ):
                    self.matrix[y + 1][x + 1] = FieldStates.GRABBED

            # Add the player field to dictionary, to be able draw names on the canvas later
            player_now = self.update_current_player()
            self.captured_player_fields[(x, y)] = player_now.name

            # Checking if player won
            if not self.is_any_field_empty():
                self.display_game()
                self.end_game()
                return

            self.display_game()

            # Detect if next player is bot and if yes, let him play
            self.turns += (
                1  # Another turn -> current_player = current_player on next move
            )
            player_next = self.update_current_player()
            if str(player_next) == "Bot":
                player_next.play()

    def display_game(self):
        """Renders game on the canvas"""
        self.__canvas.delete("all")  # Refresh

        for y in range(self.height.get()):
            for x in range(self.width.get()):
                state = self.matrix[y][x]

                fill_color = FIELD_COLORS[state]

                self.__canvas.create_rectangle(
                    x * self.field_size,
                    y * self.field_size,
                    x * self.field_size + self.field_size,
                    y * self.field_size + self.field_size,
                    fill=fill_color,
                    outline="black",
                    width=3,
                    tags=("field", "%s;%s" % (y, x)),
                )

                if state == FieldStates.PLAYER:
                    name = self.captured_player_fields[(x, y)]
                    self.__canvas.create_text(
                        x * self.field_size + self.field_size // 2,
                        y * self.field_size + self.field_size // 2,
                        text=name,
                    )

        self.__canvas.tag_bind("field", "<Button-1>", self.on_field_click)

    def update_current_player(self):
        """Updates player_on_turn_label with a name of a current player and returns a player object on turn"""
        player = self.players[self.turns % len(self.players)]
        self.__player_on_turn_label.config(text="Player on turn: %s" % player.name)
        return player

    def start_game(self, player_count=1, bot_count=1):
        self.__start_game_pc_button["state"] = tk.DISABLED
        self.__start_game_players_button["state"] = tk.DISABLED
        self.__game_height_entry["state"] = tk.DISABLED
        self.__game_width_entry["state"] = tk.DISABLED
        self.__canvas["state"] = tk.NORMAL

        for _ in range(self.height.get()):
            row = []
            for _ in range(self.width.get()):
                row.append(0)
            self.matrix.append(row)

        for i in range(bot_count):
            self.add_bot()

        for i in range(player_count):
            self.add_player(name="Player%s" % i)

        player = self.update_current_player()
        if str(player) == "Bot":
            player.play()

        self.display_game()

    def end_game(self):
        self.__start_game_pc_button["state"] = tk.NORMAL
        self.__start_game_players_button["state"] = tk.NORMAL
        self.__game_height_entry["state"] = tk.NORMAL
        self.__game_width_entry["state"] = tk.NORMAL
        self.__canvas["state"] = tk.DISABLED

        winner_name = self.update_current_player().name

        # Color Outline
        self.__canvas.create_text(
            MINSIZE_WINDOW[0] // 2 + 2,
            MINSIZE_WINDOW[1] // 3 + 2,
            text="%s is the winner!" % winner_name,
            font="Arial 40",
            fill="black",
        )

        # Color fill
        self.__canvas.create_text(
            MINSIZE_WINDOW[0] // 2,
            MINSIZE_WINDOW[1] // 3,
            text="%s is the winner!" % winner_name,
            font="Arial 40",
            fill="cyan",
        )

        self.init_game()  # Init new game

    def add_player(self, name="Player"):
        Player(self, name)

    def add_bot(self):
        Bot(self)

    def start_game_pc(self):
        self.start_game()

    def start_game_players(self):
        self.start_game(player_count=2, bot_count=0)


if __name__ == "__main__":
    bg = BlockingGame()
    bg.run()
