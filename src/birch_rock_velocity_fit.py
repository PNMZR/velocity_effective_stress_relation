# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 15:07:31 2026

@author: 67573
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error

# ====================== 岩性顺序（固定）======================
ROCK_ORDER = [
    "Granite",
    "Quartz monzonite",
    "Quartz diorite",
    "Albitite",
    "Anorthosite",
    "Diabase",
    "Norite",
    "Amphibolite",
    "Serpentinite",
    "Dunite",
    "Bronzitite",
    "Eclogite",
    "Jadeite"
]

# ====================== 模型（无需 Km, Gm）======================
def vp_model(sig, vlm, cl, phi0, c):
    phi = phi0 * np.exp(-c * sig)
    return vlm * np.sqrt((1.0 - cl * phi) * (1.0 - phi))

def vs_model(sig, vsm, cs, phi0, c):
    phi = phi0 * np.exp(-c * sig)
    return vsm * np.sqrt((1.0 - cs * phi) * (1.0 - phi))


# ====================== 读取数据 ======================
df = pd.read_excel("data/birch1960_Simmons1964.xlsx")

# ====================== 关键修正 ======================
# 规则：Vp 用原应力；Vs 若应力=1，则替换为 0
df["sig_vp"] = df["effective stress (MPa)"]
df["sig_vs"] = df["effective stress (MPa)"].replace(1.0, 0.0)

results = []
# ====================== 逐岩性拟合 ======================
for rock in ROCK_ORDER:
    d = df[df["ID"].str.startswith(rock)]
    if d.empty:
        continue

    # 对 Vp：按 sig_vp 分组平均
    g_vp = d.groupby("sig_vp").agg({
        "measured vp (km/s)": ["mean", "std"]
    })
    g_vp.columns = ["vp_mean", "vp_std"]
    sig_vp = g_vp.index.values
    vp_m = g_vp["vp_mean"].values
    vp_e = g_vp["vp_std"].values

    # 对 Vs：按 sig_vs 分组平均（已把1→0）
    g_vs = d.groupby("sig_vs").agg({
        "measured vs (km/s)": ["mean", "std"]
    })
    g_vs.columns = ["vs_mean", "vs_std"]
    sig_vs = g_vs.index.values
    vs_m = g_vs["vs_mean"].values
    vs_e = g_vs["vs_std"].values
    
    ratio = ((vp_m/vs_m) ** 2 - 2) / (2*((vp_m/vs_m) ** 2 - 1))
    c_s = (8 - 10*ratio[-1]) / (7 - 5*ratio[-1])
    c_l = (13 - 40*ratio[-1] + 55*ratio[-1]**2) / (2 * (1 - 2*ratio[-1]) * (7 - 5*ratio[-1]))

    # ---------- 拟合 Vp ----------
    try:
        popt_vp, pcov_vp = curve_fit(
            vp_model,
            sig_vp,
            vp_m,
            p0=[6.0, c_l, 0.05, 0.001],
            bounds=([0, c_l-1e-8, 0, 0],
                    [np.inf, c_l, 1, np.inf]),
            maxfev=20000
        )
        vlm, cl, phi0, c = popt_vp
        vp_fit = vp_model(sig_vp, *popt_vp)
        r2_vp = r2_score(vp_m, vp_fit)
        rmse_vp = np.sqrt(mean_squared_error(vp_m, vp_fit))
        maxpe_vp = np.max(np.abs((vp_m - vp_fit) / vp_m)) * 100
        
    except Exception as e:
        print(f"{rock} Vp 拟合失败：{e}")
        continue

    # ---------- 拟合 Vs ----------
    try:
        popt_vs, pcov_vs = curve_fit(
            vs_model,
            sig_vs,
            vs_m,
            p0=[4, c_s, phi0, c],
            bounds=([0, c_s, phi0, c],
                    [np.inf, c_s+1e-8, phi0+1e-8, c+1e-8]),
            maxfev=20000
        )
        vsm, cs, phi0_vs, c_vs = popt_vs
        vs_fit = vs_model(sig_vs, *popt_vs)
        r2_vs = r2_score(vs_m, vs_fit)
        rmse_vs = np.sqrt(mean_squared_error(vs_m, vs_fit))
        maxpe_vs = np.max(np.abs((vs_m - vs_fit) / vs_m)) * 100
    except Exception as e:
        print(f"{rock} Vs 拟合失败：{e}")
        continue

    # 保存结果
    results.append([
        rock, vlm, cl, c_l, vsm, cs, c_s, phi0, phi0_vs, c, c_vs, r2_vp, r2_vs,
        rmse_vp, rmse_vs, maxpe_vp, maxpe_vs
    ])


# ====================== 4×4布局绘制所有岩性 ======================

# Nature 风格配色方案
NATURE_COLORS = {
    'Vp_data': '#E69F00',      # 橙色
    'Vp_fit': '#E69F00',       # 橙色
    'Vs_data': '#56B4E9',      # 天蓝
    'Vs_fit': '#56B4E9',       # 天蓝
}

# 标记样式
VP_MARKER = 'o'    # Vp使用圆形
VS_MARKER = 's'    # Vs使用方形

# 创建4×4的子图布局（4行4列）
fig, axes = plt.subplots(4, 4, figsize=(18, 14))
axes = axes.flatten()  # 展平为1维数组，方便索引

# 为每个岩性绘制子图
for idx, rock in enumerate(ROCK_ORDER):
    d = df[df["ID"].str.startswith(rock)]
    if d.empty:
        continue

    # 获取该岩石的拟合参数
    res = [r for r in results if r[0] == rock]
    if not res:
        continue
    r = res[0]
    rock_name, vlm, cl, _, vsm, cs, _, phi0, phi0_vs, c, c_vs, r2_vp, r2_vs, rmse_vp, rmse_vs, maxpe_vp, maxpe_vs = r

    # 获取数据
    g_vp = d.groupby("sig_vp").agg({
        "measured vp (km/s)": ["mean", "std"]
    })
    g_vp.columns = ["vp_mean", "vp_std"]
    sig_vp = g_vp.index.values
    vp_m = g_vp["vp_mean"].values
    vp_e = g_vp["vp_std"].values

    g_vs = d.groupby("sig_vs").agg({
        "measured vs (km/s)": ["mean", "std"]
    })
    g_vs.columns = ["vs_mean", "vs_std"]
    sig_vs = g_vs.index.values
    vs_m = g_vs["vs_mean"].values
    vs_e = g_vs["vs_std"].values

    # 创建光滑的拟合曲线
    sig_vp_smooth = np.linspace(max(0, sig_vp.min()), sig_vp.max(), 100)
    vp_fit_smooth = vp_model(sig_vp_smooth, vlm, cl, phi0, c)
    
    sig_vs_smooth = np.linspace(max(0, sig_vs.min()), sig_vs.max(), 100)
    vs_fit_smooth = vs_model(sig_vs_smooth, vsm, cs, phi0_vs, c_vs)

    # 选择当前子图
    ax = axes[idx]
    
    # ===== 绘制Vp =====
    # Vp实验数据（散点+误差棒）
    ax.errorbar(sig_vp, vp_m, yerr=vp_e, fmt=VP_MARKER, 
                ms=5, capsize=3, capthick=1.0, 
                color=NATURE_COLORS['Vp_data'], alpha=0.7, 
                ecolor=NATURE_COLORS['Vp_data'], elinewidth=1.0, 
                markeredgewidth=0.8, markeredgecolor=NATURE_COLORS['Vp_data'],
                markerfacecolor='none', label=f'$v_p$ data ({rock})')
    
    # Vp拟合曲线
    ax.plot(sig_vp_smooth, vp_fit_smooth, '-', 
            lw=1.5, color=NATURE_COLORS['Vp_fit'], alpha=0.9,
            label=f'$v_p$ fit ($R^2$={r2_vp:.3f})')
    
    # ===== 绘制Vs =====
    # Vs实验数据（散点+误差棒）
    ax.errorbar(sig_vs, vs_m, yerr=vs_e, fmt=VS_MARKER, 
                ms=5, capsize=3, capthick=1.0, 
                color=NATURE_COLORS['Vs_data'], alpha=0.7, 
                ecolor=NATURE_COLORS['Vs_data'], elinewidth=1.0, 
                markeredgewidth=0.8, markeredgecolor=NATURE_COLORS['Vs_data'],
                markerfacecolor='none', label=f'$v_s$ data ({rock})')
    
    # Vs拟合曲线
    ax.plot(sig_vs_smooth, vs_fit_smooth, '-', 
            lw=1.5, color=NATURE_COLORS['Vs_fit'], alpha=0.9,
            label=f'$v_s$ fit ($R^2$={r2_vs:.3f})')

    # 设置坐标轴
    ax.set_xlabel("Effective Stress (MPa)", fontsize=10, fontname='Arial')
    ax.set_ylabel("Velocity (km/s)", fontsize=10, fontname='Arial')
    ax.set_xlim(-10, 1050)
    
    # 动态设置Y轴范围（根据数据调整）
    y_min = min(vp_m.min(), vs_m.min()) - 0.5
    y_max = max(vp_m.max(), vs_m.max()) + 0.5
    ax.set_ylim(y_min, y_max)
    
    # 设置标题（岩性名称）
    # ax.set_title(rock_name, fontsize=10, fontweight='bold', fontname='Arial')
    
    # 设置刻度
    ax.tick_params(axis='both', which='major', labelsize=8, 
                   width=0.8, length=4, direction='out')
    ax.tick_params(axis='both', which='minor', width=0.6, length=2)
    
    # 添加图例（放在左上角）
    legend = ax.legend(loc='best', fontsize=10, frameon=True, 
                       fancybox=True, shadow=False, 
                       edgecolor='gray', facecolor='white', ncol=1)
    legend.get_frame().set_linewidth(0.5)
    
    # 添加网格线（淡灰色虚线）
    ax.grid(True, linestyle=':', alpha=0.3, linewidth=0.5, color='gray')

# 隐藏多余的子图（因为只有13个岩性，第14-16个子图是空的）
for i in range(len(ROCK_ORDER), len(axes)):
    axes[i].axis('off')

# 调整整体布局
# 更精细的间距控制
# plt.subplots_adjust(hspace=0.45, wspace=0.25, bottom=0.18, top=0.95)
plt.tight_layout()

# 保存图片（可以保存为PDF和PNG格式）
plt.savefig("all_rocks_4x4.pdf", dpi=300, bbox_inches='tight')
plt.savefig("all_rocks_4x4.png", dpi=300, bbox_inches='tight')
plt.show()

print("\n所有岩性已绘制在4×4布局的图片中！")

# ====================== 输出参数表 ======================
res_df = pd.DataFrame(results, columns=[
    "rock", "vlm", "cl", "c_l", "vsm", "cs", "c_s", "phi0", "phi0_vs", "c",
    "c_vs", "R2_Vp", "R2_Vs", "RMSE_Vp", "RMSE_Vs", "MaxPE_Vp", "MaxPE_Vs"
])

res_df = res_df.round(4)
res_df.to_csv("fitted_parameters.csv", index=False)
print("\n========== 拟合结果 ==========")
print(res_df)