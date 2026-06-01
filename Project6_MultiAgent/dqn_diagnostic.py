"""Diagnostyka wytrenowanego DQN: rozkład akcji w ewaluacji vs random.
Reużywa silnik/env z notebooka (komórki definicyjne 0-7), bez retreningu."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

# --- wczytaj i wykonaj komórki definicyjne z notebooka (bez .learn) ---
nb = json.load(open('uno_multiagent.ipynb'))
code = [c for c in nb['cells'] if c['cell_type'] == 'code']
g = {}
for i in (0, 1, 2, 4, 5, 6, 7):       # pomijamy 3 (smoke) i 8-17 (trening/wykresy)
    exec(''.join(code[i]['source']), g)

DQN = g['DQN']; UnoGymEnv = g['UnoGymEnv']; random_policy = g['random_policy']
DRAW_ACTION = g['DRAW_ACTION']; card_name = g['card_name']; COLOR_NAMES = g['COLOR_NAMES']

def act_name(a):
    if a < 54: return card_name(a)
    if a == 54: return 'DRAW'
    return f'COLOR-{COLOR_NAMES[a-55]}'

dqn = DQN.load('models/dqn.zip')

# Ewaluacja deterministyczna (jak w raportowanej krzywej) – rejestrujemy AKCJE WYBRANE przez sieć
N_EP = 200
chosen = Counter()        # co sieć chciała zagrać (predict)
executed = Counter()      # co faktycznie wykonano (po podmianie nielegalnych)
illegal = 0; total = 0; wins = 0
env = UnoGymEnv(opponent_policy=random_policy, seed=0)
for ep in range(N_EP):
    obs, info = env.reset(seed=ep)
    done = False; last_r = 0.0
    while not done:
        mask = info['action_mask']
        a_net, _ = dqn.predict(obs, deterministic=True)
        a_net = int(a_net)
        chosen[a_net] += 1
        total += 1
        if not mask[a_net]:
            illegal += 1
            legal = np.flatnonzero(mask)
            a_exec = int(np.random.choice(legal))
        else:
            a_exec = a_net
        executed[a_exec] += 1
        obs, r, done, _, info = env.step(a_exec)
        last_r = r if r != 0 else last_r
    if last_r > 0: wins += 1

print(f'=== DQN diagnostic ({N_EP} epizodów vs random) ===')
print(f'Winrate: {wins/N_EP:.3f}')
print(f'Decyzji łącznie: {total} | nielegalnych wyborów sieci: {illegal} ({100*illegal/total:.1f}%)')
print('\nTOP akcje, które sieć CHCIAŁA zagrać (predict):')
for a, c in chosen.most_common(8):
    print(f'  {act_name(a):>8} (id {a:2d}): {c:5d}  {100*c/total:5.1f}%')
print('\nTOP akcje FAKTYCZNIE wykonane (po podmianie nielegalnych):')
for a, c in executed.most_common(8):
    print(f'  {act_name(a):>8} (id {a:2d}): {c:5d}  {100*c/total:5.1f}%')

# wykres
top_chosen = chosen.most_common(6)
labels = [act_name(a) for a, _ in top_chosen]
vals = [100*c/total for _, c in top_chosen]
fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.bar(labels, vals, color='#d9534f')
ax.set_ylabel('% decyzji sieci (predict)')
ax.set_title(f'DQN: rozkład akcji wybieranych przez sieć\n(winrate {wins/N_EP:.2f}, {100*illegal/total:.0f}% wyborów nielegalnych → podmienianych)')
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.5, f'{v:.0f}%', ha='center', fontsize=9)
ax.set_ylim(0, max(vals)*1.15)
plt.tight_layout()
plt.savefig('dqn_action_dist.png', dpi=130)
print('\nZapisano dqn_action_dist.png')
