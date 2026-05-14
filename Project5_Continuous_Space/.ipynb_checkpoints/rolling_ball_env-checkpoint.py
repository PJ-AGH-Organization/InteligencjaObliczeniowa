import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import pygame

WORLD_W      = 600.0
WORLD_H      = 600.0
BALL_RADIUS  = 12.0
GOAL_RADIUS  = 18.0
FRICTION     = 0.92
FORCE_SCALE  = 0.4
V_MAX        = 8.0
MAX_STEPS    = 500
RAY_MAX      = 500.0
DIAGONAL     = math.sqrt(WORLD_W ** 2 + WORLD_H ** 2)
RAY_ANGLES   = [0, 45, 90, 135, 180, 225, 270, 315]

# Static obstacle layout: (left_x, top_y, width, height)
OBSTACLES = [
    ( 80,  80,  80, 200),
    (280,  40,  80, 160),
    (440, 100, 100,  60),
    (140, 340, 160,  60),
    (350, 280,  60, 200),
    (460, 380,  90, 130),
]


class RollingBallEnv(gym.Env):

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode=None):
        super().__init__()
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self._window = None
        self._clock  = None

        low  = np.array([-1., -1., -1., -1., 0.] + [0.] * 8, dtype=np.float32)
        high = np.array([ 1.,  1.,  1.,  1., 1.] + [1.] * 8, dtype=np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self.action_space = spaces.Box(
            np.array([-1.0, -1.0], dtype=np.float32),
            np.array([ 1.0,  1.0], dtype=np.float32),
            dtype=np.float32,
        )

        self._pos        = np.zeros(2, dtype=np.float32)
        self._vel        = np.zeros(2, dtype=np.float32)
        self._goal       = np.zeros(2, dtype=np.float32)
        self._step_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        while True:
            p = np.array([
                self.np_random.uniform(BALL_RADIUS, WORLD_W - BALL_RADIUS),
                self.np_random.uniform(BALL_RADIUS, WORLD_H - BALL_RADIUS),
            ], dtype=np.float32)
            if self._is_free(p, BALL_RADIUS):
                self._pos = p
                break

        while True:
            g = np.array([
                self.np_random.uniform(GOAL_RADIUS, WORLD_W - GOAL_RADIUS),
                self.np_random.uniform(GOAL_RADIUS, WORLD_H - GOAL_RADIUS),
            ], dtype=np.float32)
            if self._is_free(g, GOAL_RADIUS) and np.linalg.norm(g - self._pos) > 100.0:
                self._goal = g
                break

        self._vel        = np.zeros(2, dtype=np.float32)
        self._step_count = 0

        obs  = self._get_obs()
        info = self._get_info()
        if self.render_mode == "human":
            self._render_frame()
        return obs, info

    def step(self, action):
        action = np.clip(action, -1.0, 1.0).astype(np.float32)

        prev_dist = float(np.linalg.norm(self._pos - self._goal))

        self._vel  = np.clip(self._vel + action * FORCE_SCALE, -V_MAX, V_MAX)
        self._vel *= FRICTION
        self._pos += self._vel

        self._resolve_walls()
        for obs_rect in OBSTACLES:
            self._resolve_obstacle(obs_rect)

        self._step_count += 1

        dist       = float(np.linalg.norm(self._pos - self._goal))
        terminated = dist <= GOAL_RADIUS + BALL_RADIUS
        truncated  = self._step_count >= MAX_STEPS

        reward = -0.01 + 0.02 * (prev_dist - dist)
        if terminated:
            reward += 50.0

        obs  = self._get_obs()
        info = self._get_info()
        if self.render_mode == "human":
            self._render_frame()
        return obs, float(reward), terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def close(self):
        if self._window is not None:
            pygame.display.quit()
            pygame.quit()
            self._window = None
            self._clock  = None

    def _is_free(self, pos: np.ndarray, radius: float) -> bool:
        if (
            pos[0] - radius < 0 or pos[0] + radius > WORLD_W
            or pos[1] - radius < 0 or pos[1] + radius > WORLD_H
        ):
            return False
        for ox, oy, ow, oh in OBSTACLES:
            cx = float(np.clip(pos[0], ox, ox + ow))
            cy = float(np.clip(pos[1], oy, oy + oh))
            if math.sqrt((pos[0] - cx) ** 2 + (pos[1] - cy) ** 2) < radius + 2.0:
                return False
        return True

    def _resolve_walls(self) -> None:
        if self._pos[0] - BALL_RADIUS < 0:
            self._pos[0] = BALL_RADIUS
            self._vel[0] = abs(self._vel[0])
        elif self._pos[0] + BALL_RADIUS > WORLD_W:
            self._pos[0] = WORLD_W - BALL_RADIUS
            self._vel[0] = -abs(self._vel[0])
        if self._pos[1] - BALL_RADIUS < 0:
            self._pos[1] = BALL_RADIUS
            self._vel[1] = abs(self._vel[1])
        elif self._pos[1] + BALL_RADIUS > WORLD_H:
            self._pos[1] = WORLD_H - BALL_RADIUS
            self._vel[1] = -abs(self._vel[1])

    def _resolve_obstacle(self, rect) -> None:
        ox, oy, ow, oh = rect
        cx = float(np.clip(self._pos[0], ox, ox + ow))
        cy = float(np.clip(self._pos[1], oy, oy + oh))
        dx = self._pos[0] - cx
        dy = self._pos[1] - cy
        dist_sq = dx * dx + dy * dy

        if dist_sq >= BALL_RADIUS * BALL_RADIUS:
            return

        dist = math.sqrt(dist_sq)
        nx, ny = (dx / dist, dy / dist) if dist > 1e-6 else (1.0, 0.0)

        overlap = BALL_RADIUS - dist
        self._pos[0] += nx * (overlap + 0.5)
        self._pos[1] += ny * (overlap + 0.5)

        dot = self._vel[0] * nx + self._vel[1] * ny
        if dot < 0:
            self._vel[0] -= 2.0 * dot * nx
            self._vel[1] -= 2.0 * dot * ny

    def _cast_ray(self, angle_deg: float) -> float:
        rad = math.radians(angle_deg)
        dx  =  math.cos(rad)
        dy  = -math.sin(rad)
        ox, oy = float(self._pos[0]), float(self._pos[1])

        t = RAY_MAX
        if dx > 1e-9:
            t = min(t, (WORLD_W - ox) / dx)
        elif dx < -1e-9:
            t = min(t, -ox / dx)
        if dy > 1e-9:
            t = min(t, (WORLD_H - oy) / dy)
        elif dy < -1e-9:
            t = min(t, -oy / dy)

        for obs_rect in OBSTACLES:
            t_obs = self._ray_aabb(ox, oy, dx, dy, obs_rect)
            if t_obs < t:
                t = t_obs

        return float(np.clip(t, 0.0, RAY_MAX))

    @staticmethod
    def _ray_aabb(ox: float, oy: float, dx: float, dy: float, rect) -> float:
        rx, ry, rw, rh = rect
        t_near, t_far = -1e30, 1e30

        if abs(dx) > 1e-9:
            tx1 = (rx      - ox) / dx
            tx2 = (rx + rw - ox) / dx
            t_near = max(t_near, min(tx1, tx2))
            t_far  = min(t_far,  max(tx1, tx2))
        elif ox < rx or ox > rx + rw:
            return RAY_MAX

        if abs(dy) > 1e-9:
            ty1 = (ry      - oy) / dy
            ty2 = (ry + rh - oy) / dy
            t_near = max(t_near, min(ty1, ty2))
            t_far  = min(t_far,  max(ty1, ty2))
        elif oy < ry or oy > ry + rh:
            return RAY_MAX

        if t_far < t_near or t_near <= 0.0:
            return RAY_MAX
        return float(np.clip(t_near, 0.0, RAY_MAX))

    def _get_obs(self) -> np.ndarray:
        ddx = self._goal[0] - self._pos[0]
        ddy = self._goal[1] - self._pos[1]
        dist = math.sqrt(ddx * ddx + ddy * ddy)
        if dist > 1e-9:
            ndx = ddx / dist
            ndy = -ddy / dist
        else:
            ndx = ndy = 0.0

        rays = [self._cast_ray(a) for a in RAY_ANGLES]
        return np.array([
            self._vel[0] / V_MAX,
            self._vel[1] / V_MAX,
            ndx,
            ndy,
            dist / DIAGONAL,
            *[r / RAY_MAX for r in rays],
        ], dtype=np.float32)

    def _get_info(self) -> dict:
        return {
            "distance_to_goal": float(np.linalg.norm(self._pos - self._goal)),
            "step": self._step_count,
        }

    def _render_frame(self):
        if not pygame.get_init():
            pygame.init()
        if self.render_mode == "human":
            if self._window is None:
                pygame.display.init()
                self._window = pygame.display.set_mode((int(WORLD_W), int(WORLD_H)))
                pygame.display.set_caption("Rolling Ball Navigator")
            if self._clock is None:
                self._clock = pygame.time.Clock()

        canvas = pygame.Surface((int(WORLD_W), int(WORLD_H)))
        TILE = 40
        for ty in range(0, int(WORLD_H), TILE):
            for tx in range(0, int(WORLD_W), TILE):
                shade = (42, 33, 24) if (tx // TILE + ty // TILE) % 2 == 0 else (50, 40, 29)
                pygame.draw.rect(canvas, shade, (tx, ty, TILE, TILE))
                pygame.draw.rect(canvas, (28, 20, 14), (tx, ty, TILE, TILE), 1)

        pygame.draw.rect(canvas, (110, 88, 64), (0, 0, int(WORLD_W), int(WORLD_H)), 6)
        pygame.draw.rect(canvas, (70, 54, 38), (3, 3, int(WORLD_W) - 6, int(WORLD_H) - 6), 2)

        for ox, oy, ow, oh in OBSTACLES:
            r = pygame.Rect(int(ox), int(oy), int(ow), int(oh))
            pygame.draw.rect(canvas, (78, 64, 48), r)
            pygame.draw.rect(canvas, (108, 90, 66), r, 2)
            pygame.draw.line(canvas, (48, 38, 28), (r.right - 1, r.top), (r.right - 1, r.bottom), 2)
            pygame.draw.line(canvas, (48, 38, 28), (r.left, r.bottom - 1), (r.right, r.bottom - 1), 2)


        obs_vec = self._get_obs()
        for i, angle_deg in enumerate(RAY_ANGLES):
            rad = math.radians(angle_deg)
            rdx =  math.cos(rad)
            rdy = -math.sin(rad)
            ray_len = float(obs_vec[5 + i]) * RAY_MAX
            ex = int(self._pos[0] + rdx * ray_len)
            ey = int(self._pos[1] + rdy * ray_len)
            pygame.draw.line(
                canvas, (210, 158, 38),
                (int(self._pos[0]), int(self._pos[1])), (ex, ey), 1,
            )

        if not hasattr(self, "_goal_img"):
            def _load_sprite(path, size):
                raw = pygame.image.load(path)
                surf = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
                surf.blit(raw, (0, 0))
                return pygame.transform.scale(surf, size)
            self._goal_img  = _load_sprite("sprites/goal.png",  (int(GOAL_RADIUS * 2), int(GOAL_RADIUS * 2)))
            self._agent_img = _load_sprite("sprites/agent.png", (int(BALL_RADIUS * 2), int(BALL_RADIUS * 2)))

        canvas.blit(self._goal_img,
            (int(self._goal[0] - GOAL_RADIUS), int(self._goal[1] - GOAL_RADIUS)))
        canvas.blit(self._agent_img,
            (int(self._pos[0] - BALL_RADIUS), int(self._pos[1] - BALL_RADIUS)))

        if self.render_mode == "human":
            self._window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self._clock.tick(self.metadata["render_fps"])
        else:
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )