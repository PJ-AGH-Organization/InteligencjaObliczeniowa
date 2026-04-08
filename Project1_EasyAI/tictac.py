import random
from copy import deepcopy
from easyAI import TwoPlayerGame


class TicTacDoh(TwoPlayerGame):
    def __init__(self, players, probabilistic=True):
        self.players = players
        self.board = [0 for i in range(9)]
        self.current_player = 1
        self.probabilistic = probabilistic
        self._apply_failure = False
        self.last_move_failed = False
        self.moves_attempted = 0
        self.moves_failed = 0
        self.total_moves = 0

    def possible_moves(self):
        return [i + 1 for i, e in enumerate(self.board) if e == 0]

    FAIL_CHANCE = 0.20

    def make_move(self, move):
        self.last_move_failed = False
        if self.probabilistic and self._apply_failure:
            self.moves_attempted += 1
            if random.random() < self.FAIL_CHANCE:
                self.last_move_failed = True
                self.moves_failed += 1
                return
        self.board[int(move) - 1] = self.current_player

    def play(self, nmoves=1000, verbose=True):
        history = []

        if verbose:
            self.show()

        for self.nmove in range(1, nmoves + 1):
            if self.is_over():
                break

            move = self.player.ask_move(self)
            history.append((deepcopy(self), move))

            self._apply_failure = True
            try:
                self.make_move(move)
            finally:
                self._apply_failure = False
            self.total_moves += 1

            if verbose:
                failed_suffix = " (FAILED)" if self.last_move_failed else ""
                print(
                    "\nMove #%d: player %d plays %s%s :"
                    % (self.nmove, self.current_player, str(move), failed_suffix)
                )
                if self.last_move_failed:
                    print(
                        "  [Tic-tac-doh] Move failed: no mark placed; opponent moves now."
                    )
                self.show()

            self.switch_player()

        if verbose and self.moves_attempted > 0:
            pct = 100 * self.moves_failed / self.moves_attempted
            print(f"\n--- Statystyka: {self.moves_failed}/{self.moves_attempted} ruchów nieudanych ({pct:.0f}%) ---")
        history.append(deepcopy(self))
        return history

    def unmake_move(self, move):
        self.board[int(move) - 1] = 0

    def lose(self):
        """ Has the opponent "three in line ?" """
        return any(
            [
                all([(self.board[c - 1] == self.opponent_index) for c in line])
                for line in [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9],
                    [1, 4, 7],
                    [2, 5, 8],
                    [3, 6, 9],
                    [1, 5, 9],
                    [3, 5, 7],
                ]
            ]
        )

    def is_over(self):
        return (self.possible_moves() == []) or self.lose()

    def get_winner(self):
        if self.lose():
            return self.opponent_index
        if self.possible_moves() == []:
            return 0
        return None

    def show(self):
        print(
            "\n"
            + "\n".join(
                [
                    " ".join([[".", "O", "X"][self.board[3 * j + i]] for i in range(3)])
                    for j in range(3)
                ]
            )
        )

    def scoring(self):
        return -100 if self.lose() else 0


if __name__ == "__main__":
    from easyAI import AI_Player, Negamax

    ai_algo = Negamax(6)
    game = TicTacDoh([AI_Player(ai_algo), AI_Player(ai_algo)], probabilistic=True)
    print("Tic-tac-doh: Dwa AI grają ze sobą (20% szans że ruch się nie uda)\n")
    game.play()