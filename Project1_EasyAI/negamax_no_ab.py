inf = float("infinity")

def _negamax_no_ab(game, depth, orig_depth, scoring):
    if (depth == 0) or game.is_over():
        score = scoring(game)
        if score == 0:
            return score
        return score - 0.01 * depth * abs(score) / score

    possible_moves = game.possible_moves()
    best_move = possible_moves[0]

    if depth == orig_depth:
        game.ai_move = possible_moves[0]

    best_value = -inf
    unmake_move = hasattr(game, "unmake_move")
    state = game

    for move in possible_moves:
        if not unmake_move:
            game = state.copy()

        game.make_move(move)
        game.switch_player()

        move_value = -_negamax_no_ab(game, depth - 1, orig_depth, scoring)

        if unmake_move:
            game.switch_player()
            game.unmake_move(move)

        if best_value < move_value:
            best_value = move_value
            best_move = move
            if depth == orig_depth:
                state.ai_move = move

    return best_value

class NegamaxNoAB:
    def __init__(self, depth, scoring=None):
        self.depth = depth
        self.scoring = scoring

    def __call__(self, game):
        scoring = self.scoring if self.scoring else (lambda g: g.scoring())
        self.alpha = _negamax_no_ab(game, self.depth, self.depth, scoring)
        return game.ai_move
