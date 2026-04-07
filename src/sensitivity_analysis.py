# -*- coding: utf-8 -*-
"""
参数敏感性分析 - 简化版
输出每个岩石、每个有效应力的S1/ST指标，以及4x4相对误差图
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from SALib.sample import saltelli
from SALib.analyze import sobol
import seaborn as sns

# ====================== 岩性顺序 ======================
ROCK_ORDER = [
    "Granite", "Quartz monzonite", "Quartz diorite", "Albitite",
    "Anorthosite", "Diabase", "Norite", "Amphibolite",
    "Serpentinite", "Dunite", "Bronzitite", "Eclogite", "Jadeite"
]

# ====================== 模型 ======================
def vp_model(sig, vlm, cl, phi0, c):
    phi = phi0 * np.exp(-c * sig)
    return vlm * np.sqrt((1.0 - cl * phi) * (1.0 - phi))

def vs_model(sig, vsm, cs, phi0, c):
    phi = phi0 * np.exp(-c * sig)
    return vsm * np.sqrt((1.0 - cs * phi) * (1.0 - phi))

# ====================== 读取数据 ======================
df = pd.read_excel("data/birch1960_Simmons1964.xlsx")
df["sig_vp"] = df["effective stress (MPa)"]
df["sig_vs"] = df["effective stress (MPa)"].replace(1.0, 0.0)

# 存储汇总结果
all_sensitivity_results = []  # 存储所有敏感性指标
all_error_data = []  # 存储所有误差点（用于绘图）

# ====================== 逐岩性分析 ======================
for rock in ROCK_ORDER:
    d = df[df["ID"].str.startswith(rock)]
    if d.empty:
        continue

    # Vp数据
    g_vp = d.groupby("sig_vp")["measured vp (km/s)"].agg(["mean", "std"])
    sig_vp = g_vp.index.values
    vp_m = g_vp["mean"].values
    
    # Vs数据
    g_vs = d.groupby("sig_vs")["measured vs (km/s)"].agg(["mean", "std"])
    sig_vs = g_vs.index.values
    vs_m = g_vs["mean"].values
    
    # 计算初始值
    ratio = ((vp_m/vs_m) ** 2 - 2) / (2*((vp_m/vs_m) ** 2 - 1))
    c_s = (8 - 10*ratio[-1]) / (7 - 5*ratio[-1])
    c_l = (13 - 40*ratio[-1] + 55*ratio[-1]**2) / (2 * (1 - 2*ratio[-1]) * (7 - 5*ratio[-1]))

    # ---------- 拟合Vp ----------
    try:
        popt_vp, _ = curve_fit(vp_model, sig_vp, vp_m,
                               p0=[6.0, c_l, 0.05, 0.001],
                               bounds=([0, c_l-1e-8, 0, 0],
                                       [np.inf, c_l, 1, np.inf]),
                               maxfev=20000)
        vlm, cl, phi0_vp, c_vp = popt_vp
        
        # Vp敏感性分析（每个压力点）
        problem_vp = {
            'num_vars': 4,
            'names': ['vlm', 'cl', 'phi0', 'c'],
            'bounds': [[vlm*0.95, vlm*1.05],
                       [cl*0.95, cl*1.05],
                       [phi0_vp*0.95, phi0_vp*1.05],
                       [c_vp*0.95, c_vp*1.05]]
        }
        param_values_vp = saltelli.sample(problem_vp, 100)  # 100个样本
        
        for i, pressure in enumerate(sig_vp):
            # 计算模型输出（多个采样值）
            Y = np.array([vp_model(pressure, *params) for params in param_values_vp])
            
            # Sobol分析
            Si = sobol.analyze(problem_vp, Y)
            
            # 保存敏感性指标
            all_sensitivity_results.append({
                'rock': rock,
                'wave_type': 'Vp',
                'pressure': pressure,
                'observed_value': vp_m[i],
                'S1_vlm': Si['S1'][0], 'ST_vlm': Si['ST'][0],
                'S1_cl': Si['S1'][1], 'ST_cl': Si['ST'][1],
                'S1_phi0': Si['S1'][2], 'ST_phi0': Si['ST'][2],
                'S1_c': Si['S1'][3], 'ST_c': Si['ST'][3]
            })
            
            # 保存误差数据（每个采样点一个误差值，用于绘图）
            rel_errors = (Y - vp_m[i]) / vp_m[i]
            for j, (y_pred, rel_err) in enumerate(zip(Y, rel_errors)):
                all_error_data.append({
                    'rock': rock,
                    'wave_type': 'Vp',
                    'pressure': pressure,
                    'observed': vp_m[i],
                    'predicted': y_pred,
                    'relative_error': rel_err,
                    'sample_id': j
                })
                
    except Exception as e:
        print(f"{rock} Vp分析失败: {e}")
        continue

    # ---------- 拟合Vs ----------
    try:
        popt_vs, _ = curve_fit(vs_model, sig_vs, vs_m,
                               p0=[4, c_s, phi0_vp, c_vp],
                               bounds=([0, c_s, phi0_vp, c_vp],
                                       [np.inf, c_s+1e-8, phi0_vp+1e-8, c_vp+1e-8]),
                               maxfev=20000)
        vsm, cs, phi0_vs, c_vs = popt_vs
        
        # Vs敏感性分析
        problem_vs = {
            'num_vars': 4,
            'names': ['vsm', 'cs', 'phi0', 'c'],
            'bounds': [[vsm*0.95, vsm*1.05],
                       [cs*0.95, cs*1.05],
                       [phi0_vs*0.95, phi0_vs*1.05],
                       [c_vs*0.95, c_vs*1.05]]
        }
        param_values_vs = saltelli.sample(problem_vs, 100)
        
        for i, pressure in enumerate(sig_vs):
            Y = np.array([vs_model(pressure, *params) for params in param_values_vs])
            Si = sobol.analyze(problem_vs, Y)
            
            all_sensitivity_results.append({
                'rock': rock,
                'wave_type': 'Vs',
                'pressure': pressure,
                'observed_value': vs_m[i],
                'S1_vsm': Si['S1'][0], 'ST_vsm': Si['ST'][0],
                'S1_cs': Si['S1'][1], 'ST_cs': Si['ST'][1],
                'S1_phi0': Si['S1'][2], 'ST_phi0': Si['ST'][2],
                'S1_c': Si['S1'][3], 'ST_c': Si['ST'][3]
            })
            
            # 保存Vs误差数据
            rel_errors = (Y - vs_m[i]) / vs_m[i]
            for j, (y_pred, rel_err) in enumerate(zip(Y, rel_errors)):
                all_error_data.append({
                    'rock': rock,
                    'wave_type': 'Vs',
                    'pressure': pressure,
                    'observed': vs_m[i],
                    'predicted': y_pred,
                    'relative_error': rel_err,
                    'sample_id': j
                })
                
    except Exception as e:
        print(f"{rock} Vs分析失败: {e}")

# ====================== 保存敏感性汇总表 ======================
sens_df = pd.DataFrame(all_sensitivity_results)
sens_df.to_excel('sensitivity_summary.xlsx', index=False)
print(f"敏感性汇总已保存到 sensitivity_summary.xlsx (共{len(sens_df)}条记录)")

# ====================== 4x4相对误差图 - Vp ======================
error_df = pd.DataFrame(all_error_data)

# Vp图
vp_error_df = error_df[error_df['wave_type'] == 'Vp']
rocks_to_plot = vp_error_df['rock'].unique()[:16]
n_rocks = len(rocks_to_plot)
n_cols = 4
n_rows = (n_rocks + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 14))
if n_rocks == 1:
    axes = [axes]
else:
    axes = axes.flatten()

for idx, rock in enumerate(rocks_to_plot):
    ax = axes[idx]
    rock_data = vp_error_df[vp_error_df['rock'] == rock]
    
    sns.scatterplot(data=rock_data, x='predicted', y='relative_error',
                    hue='pressure', ax=ax, alpha=0.8, s=10,
                    palette='plasma', legend='brief')
    
    ax.axhline(0, color='red', linestyle='--', alpha=0.7, linewidth=1)
    ax.set_xlabel('Predicted Vp (km/s)', fontsize=9)
    ax.set_ylabel('Relative Error', fontsize=9)
    ax.set_title(f'{rock} - Vp', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(title='Pressure (MPa)', loc='best', fontsize=8, 
              title_fontsize=9, framealpha=0.8)

for idx in range(len(rocks_to_plot), len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('relative_errors_4x4_Vp.pdf', dpi=300, bbox_inches='tight')
plt.show()

# ====================== 4x4相对误差图 - Vs ======================
vs_error_df = error_df[error_df['wave_type'] == 'Vs']
rocks_to_plot_vs = vs_error_df['rock'].unique()[:16]
n_rocks_vs = len(rocks_to_plot_vs)
n_rows_vs = (n_rocks_vs + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows_vs, n_cols, figsize=(18, 14))
if n_rocks_vs == 1:
    axes = [axes]
else:
    axes = axes.flatten()

for idx, rock in enumerate(rocks_to_plot_vs):
    ax = axes[idx]
    rock_data = vs_error_df[vs_error_df['rock'] == rock]
    
    sns.scatterplot(data=rock_data, x='predicted', y='relative_error',
                    hue='pressure', ax=ax, alpha=0.8, s=10,
                    palette='plasma', legend='brief')
    
    ax.axhline(0, color='red', linestyle='--', alpha=0.7, linewidth=1)
    ax.set_xlabel('Predicted Vs (km/s)', fontsize=9)
    ax.set_ylabel('Relative Error', fontsize=9)
    ax.set_title(f'{rock} - Vs', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(title='Pressure (MPa)', loc='best', fontsize=8, 
              title_fontsize=9, framealpha=0.8)

for idx in range(len(rocks_to_plot_vs), len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('relative_errors_4x4_Vs.pdf', dpi=300, bbox_inches='tight')
plt.show()

print(f"Vp误差图已保存 (共{len(vp_error_df)}个误差点)")
print(f"Vs误差图已保存 (共{len(vs_error_df)}个误差点)")


# ====================== 计算最大相对误差 ======================
print("\n" + "=" * 60)
print("最大相对误差统计")
print("=" * 60)

# 计算Vp的最大相对误差
vp_error_df = error_df[error_df['wave_type'] == 'Vp']
vp_max_rel_error = vp_error_df['relative_error'].abs().max()
vp_max_pos_error = vp_error_df['relative_error'].max()
vp_max_neg_error = vp_error_df['relative_error'].min()
vp_percentile_95 = vp_error_df['relative_error'].abs().quantile(0.95)

print(f"\nVp (纵波) 相对误差:")
print(f"  最大绝对值误差: {vp_max_rel_error:.3%} (±{vp_max_rel_error*100:.2f}%)")
print(f"  最大正误差: {vp_max_pos_error:.3%} ({vp_max_pos_error*100:.2f}%)")
print(f"  最大负误差: {vp_max_neg_error:.3%} ({vp_max_neg_error*100:.2f}%)")
print(f"  95%分位数绝对值误差: {vp_percentile_95:.3%} (±{vp_percentile_95*100:.2f}%)")

# 计算Vs的最大相对误差
vs_error_df = error_df[error_df['wave_type'] == 'Vs']
vs_max_rel_error = vs_error_df['relative_error'].abs().max()
vs_max_pos_error = vs_error_df['relative_error'].max()
vs_max_neg_error = vs_error_df['relative_error'].min()
vs_percentile_95 = vs_error_df['relative_error'].abs().quantile(0.95)

print(f"\nVs (横波) 相对误差:")
print(f"  最大绝对值误差: {vs_max_rel_error:.3%} (±{vs_max_rel_error*100:.2f}%)")
print(f"  最大正误差: {vs_max_pos_error:.3%} ({vs_max_pos_error*100:.2f}%)")
print(f"  最大负误差: {vs_max_neg_error:.3%} ({vs_max_neg_error*100:.2f}%)")
print(f"  95%分位数绝对值误差: {vs_percentile_95:.3%} (±{vs_percentile_95*100:.2f}%)")

# ====================== 按岩石类型统计 ======================
print("\n" + "-" * 40)
print("各岩石类型最大绝对误差 (Vp):")
rock_vp_max = vp_error_df.groupby('rock')['relative_error'].apply(lambda x: x.abs().max())
for rock, max_err in rock_vp_max.sort_values(ascending=False).items():
    print(f"  {rock:25s}: {max_err:.3%} (±{max_err*100:.2f}%)")

print("\n各岩石类型最大绝对误差 (Vs):")
rock_vs_max = vs_error_df.groupby('rock')['relative_error'].apply(lambda x: x.abs().max())
for rock, max_err in rock_vs_max.sort_values(ascending=False).items():
    print(f"  {rock:25s}: {max_err:.3%} (±{max_err*100:.2f}%)")

# ====================== 按压力统计 ======================
print("\n" + "-" * 40)
print("各压力点最大绝对误差 (Vp):")
pressure_vp_max = vp_error_df.groupby('pressure')['relative_error'].apply(lambda x: x.abs().max())
for pressure, max_err in pressure_vp_max.items():
    print(f"  {pressure:3d} MPa: {max_err:.3%} (±{max_err*100:.2f}%)")

print("\n各压力点最大绝对误差 (Vs):")
pressure_vs_max = vs_error_df.groupby('pressure')['relative_error'].apply(lambda x: x.abs().max())
for pressure, max_err in pressure_vs_max.items():
    print(f"  {pressure:3d} MPa: {max_err:.3%} (±{max_err*100:.2f}%)")

# ====================== 保存到文件 ======================
summary_stats = {
    'wave_type': ['Vp', 'Vs'],
    'max_absolute_error': [vp_max_rel_error, vs_max_rel_error],
    'max_positive_error': [vp_max_pos_error, vs_max_pos_error],
    'max_negative_error': [vp_max_neg_error, vs_max_neg_error],
    '95th_percentile_error': [vp_percentile_95, vs_percentile_95]
}
stats_df = pd.DataFrame(summary_stats)
stats_df.to_excel('error_statistics.xlsx', index=False)
print("\n" + "=" * 60)
print("误差统计已保存到 error_statistics.xlsx")