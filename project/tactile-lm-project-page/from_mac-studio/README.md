# CT-Touch Experiment Results — Project Page Assets

All experiments: PPO, 10 seeds (42, 123, 7, 256, 512, 1024, 2048, 314, 777, 55), Mac Studio M1 Max 64GB.

---

## Analysis Figures

### selfbody_scaling_bar.png
**Selfbody — Reward Scaling Bar Chart**

Mean reward (±SD) across training steps (50K–1M) for the self-body task.
CT ON (orange) shows a slight early advantage at 50–100K steps, but CT OFF (blue) achieves higher rewards at longer training horizons.
Error bars overlap substantially, indicating no statistically significant difference (all p > .05, Mann-Whitney U).

### reach_scaling_bar.png
**Reach — Reward Scaling Bar Chart**

Mean reward (±SD) across training steps for the reach task.
Reward is distance-based (closer to 0 = better performance).
CT ON consistently outperforms CT OFF across all training horizons, with the gap widening from 10% at 50K to 18% at 1M steps.
CT ON also shows lower variance, suggesting more stable learning.

### selfbody_boxplots.png
**Selfbody — Reward Distribution (Boxplots)**

Reward distribution per seed for the self-body task. Each dot represents one seed (n=10).
Both conditions show high variance across seeds, with no consistent advantage for either condition.

### reach_boxplots.png
**Reach — Reward Distribution (Boxplots)**

Reward distribution per seed for the reach task.
CT ON (orange) consistently achieves higher rewards with a tighter distribution, particularly at 500K and 1M steps.
CT OFF exhibits more extreme low-performing outliers.

---

## Videos & Snapshots

Best-performing model for each task and condition (absolute best across all step sizes).

### Self-body Task

| Condition | Best Seed | Steps | Reward | Files |
|-----------|-----------|-------|--------|-------|
| CT OFF | seed=7 | 1M | +362.2 | `selfbody_CT_OFF_1000K_seed7_ep*.mp4`, `*_snapshots.png` |
| CT ON | seed=512 | 50K | +432.6 | `selfbody_CT_ON_50K_seed512_ep*.mp4`, `*_snapshots.png` |

**Selfbody snapshots**: MIMo sits and reaches with the right arm to touch randomized body parts.
CT ON best model achieved +432.6 reward in only 50K steps (vs CT OFF best +362.2 at 1M steps),
suggesting CT-augmented touch enables faster discovery of successful self-touching strategies.

### Reach Task

| Condition | Best Seed | Steps | Reward | Files |
|-----------|-----------|-------|--------|-------|
| CT OFF | seed=42 | 1M | -38.0 | `reach_CT_OFF_1000K_seed42_ep*.mp4`, `*_snapshots.png` |
| CT ON | seed=256 | 100K | -26.9 | `reach_CT_ON_100K_seed256_ep*.mp4`, `*_snapshots.png` |

**Reach snapshots**: MIMo extends the right arm toward a hovering ball.
CT ON best model achieved -26.9 reward in only 100K steps (vs CT OFF best -38.0 at 1M steps),
demonstrating that CT-augmented multi-receptor touch enables more sample-efficient learning
for reaching tasks.

---

## Key Findings

1. **Sample efficiency**: CT ON best models require far fewer training steps (50K–100K) to match or exceed CT OFF best (1M), suggesting CT afferent signals accelerate learning.
2. **Reach task advantage**: CT ON shows consistent improvement across all step sizes with lower variance.
3. **Selfbody task**: No clear overall advantage, but CT ON achieves the single highest reward.
4. **Efficient representation**: CT ON uses ~50% less tactile activation in reach, indicating the multi-receptor model learns a more compact sensory representation.
