# -*- coding: utf-8 -*-
"""
Discrete heatmap for Poisson's ratio (based on experimental points)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ====================== 岩性顺序 ======================
ROCK_ORDER = [
    "Granite", "Quartz monzonite", "Quartz diorite", "Albitite", "Anorthosite",
    "Diabase", "Norite", "Amphibolite", "Serpentinite", "Dunite",
    "Bronzitite", "Eclogite", "Jadeite"
]

# ====================== 读取数据 ======================
df = pd.read_excel("data/birch1960_Simmons1964.xlsx")
df["sig_vp"] = df["effective stress (MPa)"]
df["sig_vs"] = df["effective stress (MPa)"].replace(1.0, 0.0)

# ====================== 构建离散矩阵 ======================
# 先找出所有实验应力点（并排序）
all_stress = np.sort(df["sig_vp"].unique())
stress_idx = {s: i for i, s in enumerate(all_stress)}
n_stress = len(all_stress)

poisson_matrix = []
rock_names = []

for rock in ROCK_ORDER:
    d = df[df["ID"].str.startswith(rock)]
    if d.empty:
        continue

    # 初始化一行
    row = np.full(n_stress, np.nan)

    for _, r in d.iterrows():
        s = r["sig_vp"]
        vp = r["measured vp (km/s)"]
        vs = r["measured vs (km/s)"]
        pr = (vp**2 - 2*vs**2)/(2*(vp**2 - vs**2))
        idx = stress_idx[s]
        row[idx] = pr

    poisson_matrix.append(row)
    rock_names.append(rock)

poisson_matrix = np.array(poisson_matrix)

# ====================== 绘制热力图并标注数值 ======================
fig, ax = plt.subplots()

im = ax.imshow(poisson_matrix, aspect='auto', cmap='RdYlBu_r',
               origin='upper', interpolation='none',
               vmin=0.2, vmax=0.4)

# 坐标轴
ax.set_yticks(np.arange(len(rock_names)))
ax.set_yticklabels(rock_names, fontsize=10)
ax.set_xlabel("Effective Stress (MPa)", fontsize=13)
# ax.set_ylabel("Rock Type", fontsize=13)

# X轴对应实验应力
ax.set_xticks(np.arange(n_stress))
ax.set_xticklabels([f"{s:.0f}" for s in all_stress])

# 颜色条
cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.05)
cbar.set_label("Dynamic Poisson's Ratio", fontsize=12)

# ====================== 在每个方格上标注数值 ======================
for i in range(len(rock_names)):
    for j in range(n_stress):
        val = poisson_matrix[i, j]
        if not np.isnan(val):
            ax.text(j, i, f"{val:.3f}", ha='center', va='center', fontsize=8, color='black')

# ax.set_title("Discrete Heatmap of Poisson's Ratio (Experimental Points)", fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig("Poisson_ratio_discrete_matrix_annotated.png", dpi=300, bbox_inches="tight")
plt.show()