from copy import deepcopy

inf = float("infinity")

def _expectiminimax(game, depth, orig_depth, scoring, alpha, beta,
                    fail_chance, score_bounds):

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

    min_score, max_score = score_bounds

    for move in possible_moves:
        if fail_chance > 0 and depth > 0:
            p_fail = fail_chance
            p_success = 1.0 - fail_chance

            if not unmake_move:
                game_success = state.copy()
            else:
                game_success = state

            game_success.make_move(move)
            game_success.switch_player()

            alpha_s = (alpha - p_fail * (-min_score)) / p_success
            beta_s = (beta - p_fail * (-max_score)) / p_success

            v_success = -_expectiminimax(
                game_success, depth - 1, orig_depth, scoring,
                -beta_s, -alpha_s, fail_chance, score_bounds
            )

            if unmake_move:
                game_success.switch_player()
                game_success.unmake_move(move)

            if not unmake_move:
                game_fail = state.copy()
            else:
                game_fail = state

            game_fail.switch_player()

            alpha_f = (alpha - p_success * v_success) / p_fail
            beta_f = (beta - p_success * v_success) / p_fail

            alpha_f = max(alpha_f, -(-min_score))
            beta_f = min(beta_f, -(-max_score))

            if alpha_f < beta_f:
                v_fail = -_expectiminimax(
                    game_fail, depth - 1, orig_depth, scoring,
                    -beta_f, -alpha_f, fail_chance, score_bounds
                )
            else:
                move_upper = p_success * v_success + p_fail * max_score
                if move_upper <= alpha:
                    v_fail = max_score
                else:
                    v_fail = min_score

            if unmake_move:
                game_fail.switch_player()

            move_value = p_success * v_success + p_fail * v_fail

        else:
            if not unmake_move:
                game = state.copy()
            else:
                game = state

            game.make_move(move)
            game.switch_player()

            move_value = -_expectiminimax(
                game, depth - 1, orig_depth, scoring,
                -beta, -alpha, fail_chance, score_bounds
            )

            if unmake_move:
                game.switch_player()
                game.unmake_move(move)

        if best_value < move_value:
            best_value = move_value
            best_move = move
            if depth == orig_depth:
                state.ai_move = move

        if alpha < move_value:
            alpha = move_value
            if alpha >= beta:
                break

    return best_value


class ExpectiMinimax:
    def __init__(self, depth, scoring=None, fail_chance=0.20, win_score=100):
        self.depth = depth
        self.scoring = scoring
        self.fail_chance = fail_chance
        self.win_score = win_score

    def __call__(self, game):
        scoring = self.scoring if self.scoring else (lambda g: g.scoring())

        score_bounds = (-self.win_score, self.win_score)

        self.alpha = _expectiminimax(
            game, self.depth, self.depth, scoring,
            -inf, +inf,
            self.fail_chance, score_bounds
        )
        return game.ai_move
