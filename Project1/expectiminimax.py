"""
Expecti-Minimax with alpha-beta pruning (Star1 pruning).

Designed for games with chance nodes (e.g., Tic-tac-doh where moves fail
with some probability).

For each move, the algorithm considers two outcomes:
  - success (probability 1 - fail_chance): the move is placed on the board
  - failure (probability fail_chance): no mark placed, opponent moves

The expected value of a move is:
  V(move) = (1 - p) * V(success) + p * V(failure)

Alpha-beta pruning on chance nodes uses Star1 bounds:
  lower = (1-p)*worst + p*V(fail)  or  (1-p)*V(success) + p*worst
  upper = (1-p)*best  + p*V(fail)  or  (1-p)*V(success) + p*best
"""

from copy import deepcopy

inf = float("infinity")


def _expectiminimax(game, depth, orig_depth, scoring, alpha, beta,
                    fail_chance, score_bounds):
    """
    Expecti-negamax with alpha-beta (Star1) pruning.

    Parameters
    ----------
    game : TwoPlayerGame
    depth : int — remaining depth
    orig_depth : int — original depth (to identify root)
    scoring : callable(game) -> float
    alpha, beta : float — pruning bounds
    fail_chance : float — probability of move failure (0.0 = deterministic)
    score_bounds : tuple (min_score, max_score) — bounds on the scoring function
    """

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
            # --- Chance node: compute expected value ---
            p_fail = fail_chance
            p_success = 1.0 - fail_chance

            # ------ Outcome 1: move SUCCEEDS ------
            if not unmake_move:
                game_success = state.copy()
            else:
                game_success = state

            game_success.make_move(move)
            game_success.switch_player()

            # Star1 pruning: narrow alpha-beta for the success branch
            # based on the bounds of the fail branch
            # V = p_success * V_s + p_fail * V_f
            # We know V_f is in [min_score, max_score]
            # So for pruning: alpha_s = (alpha - p_fail * max_score) / p_success
            #                  beta_s  = (beta  - p_fail * min_score) / p_success
            alpha_s = (alpha - p_fail * (-min_score)) / p_success
            beta_s = (beta - p_fail * (-max_score)) / p_success

            v_success = -_expectiminimax(
                game_success, depth - 1, orig_depth, scoring,
                -beta_s, -alpha_s, fail_chance, score_bounds
            )

            if unmake_move:
                game_success.switch_player()
                game_success.unmake_move(move)

            # ------ Outcome 2: move FAILS (no change, opponent moves) ------
            if not unmake_move:
                game_fail = state.copy()
            else:
                game_fail = state

            # No board change — just switch player
            game_fail.switch_player()

            # Star1 bounds for fail branch
            alpha_f = (alpha - p_success * v_success) / p_fail
            beta_f = (beta - p_success * v_success) / p_fail

            # Clamp to valid score range
            alpha_f = max(alpha_f, -(-min_score))
            beta_f = min(beta_f, -(-max_score))

            if alpha_f < beta_f:
                v_fail = -_expectiminimax(
                    game_fail, depth - 1, orig_depth, scoring,
                    -beta_f, -alpha_f, fail_chance, score_bounds
                )
            else:
                # Star1 pruning: fail branch pruned — no v_fail in
                # [min_score, max_score] can place move_value inside
                # [alpha, beta].  Use a bound-based estimate.
                move_upper = p_success * v_success + p_fail * max_score
                if move_upper <= alpha:
                    v_fail = max_score   # optimistic, still below alpha
                else:
                    v_fail = min_score   # pessimistic, still above beta

            if unmake_move:
                game_fail.switch_player()

            move_value = p_success * v_success + p_fail * v_fail

        else:
            # --- Deterministic: standard negamax ---
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
    """
    Expecti-Minimax with alpha-beta (Star1) pruning.

    Models chance nodes in the game tree — each move has a probability
    of failing (no mark placed, opponent moves). This is the correct
    algorithm for probabilistic games like Tic-tac-doh.

    Parameters
    ----------
    depth : int
        How many moves ahead the AI analyses.
    scoring : callable, optional
        f(game) -> score. Uses game.scoring() if None.
    fail_chance : float
        Probability of move failure (default: 0.20 for Tic-tac-doh).
    win_score : float
        Absolute bound on the scoring function (default: 100).
    """

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
