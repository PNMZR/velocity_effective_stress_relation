# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 15:58:08 2025.

计算三口井的地层压力.
@author: 67573
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def proposed_euqation(peff, vm, c1, phi0, c2):
    """所提模型."""
    phi = phi0*np.exp(-c2*peff)
    v = vm*np.sqrt((1 - c1*phi)*(1 - phi))
    return v


def r_squared(data, pridicted_data):
    """计算确定性系数."""
    SSE = np.sum((data - pridicted_data) ** 2)
    SST = np.sum((data - np.mean(data)) ** 2)
    r_squared = 1 - SSE/SST
    return r_squared

def calculate_overburden_pressure(density_log, depth, gravity=9.81):
    """
    计算上覆岩层压力（Overburden Pressure）.

    参数：
    density_log: list or np.array，密度测井数据（g/cm³）。
    depth: list or np.array，对应深度（m）。
    gravity: float，重力加速度（m/s²），默认 9.81。

    返回：
    np.array，上覆岩层压力（Pa）。
    """
    density_log = np.array(density_log) * 1000  # 转换为 kg/m³
    depth = np.array(depth)

    overburden_pressure = np.cumsum(density_log * gravity * np.gradient(depth))

    return overburden_pressure

def convert_units(file_path, sheet_name=0):
    """
    读取Excel文件并转换单位。
    
    参数：
    file_path: str，Excel文件路径。
    sheet_name: str or int，Excel工作表名称或索引。
    
    返回：
    pd.DataFrame，转换单位后的数据。
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # 假设第一列是深度（feet），转换为米
    df.iloc[:, 0] = df.iloc[:, 0] * 0.3048

    # 假设第三列是声波时差（us/ft），转换为波速（km/s）
    df.iloc[:, 2] = 1 / (df.iloc[:, 2] * 1e-3/0.3048)

    # 假设最后一列是孔隙压力（psi），转换为MPa
    df.iloc[:, -1] = df.iloc[:, -1] * 0.00689476

    return df


file_path1 = 'data/WILCOX-1.xlsx'
file_path2 = 'data/WILCOX-2.xlsx'
file_path3 = 'data/GOODWYN-6.xlsx'
file_paths = [file_path1, file_path2, file_path3]
indexes = [4200, 3000, 7000]
guesses = [[1, 0, 0, 0.0], [0, 1, 1, -0.5], [0, 0, 5, 0.5]]

vps = []
vps_pri = []
depths = []
r_squared_list = []
for file_path, index, guess in zip(file_paths, indexes, guesses):
    df = convert_units(file_path=file_path)
    op = calculate_overburden_pressure(df.iloc[:, 4], df.iloc[:, 0]) * 1e-6
    depth = np.array(df.iloc[:, 0])[index:]
    depths.append(depth)
    eff = op - np.array(df.iloc[:, -1])
    vp = np.array(df.iloc[:, 2])[index:]
    vps.append(vp)
    eff = eff[index:]

    popt1, pcov1 = curve_fit(proposed_euqation, eff, vp, guess)
    vp_pridicted = proposed_euqation(eff, *popt1)
    vps_pri.append(vp_pridicted)
    r_squared_list.append(r_squared(vp, vp_pridicted))

wells = ["WILCOX-1", "WILCOX-2", "GOODWYN-6"]


fig, axes = plt.subplots(1, 3, figsize=(10, 8), facecolor='#F8F9FA')  # 修改背景色为极浅灰

# Loop Over Each Gamma Ray Log
for ax, vp, vp_pri, depth, well in zip(axes, vps, vps_pri, depths, wells):
    ax.plot(vp, depth, label='Field measurent', color='#2C3E50')  # 深灰蓝
    ax.plot(vp_pri, depth, label='Estimated using Eq.(10)', color='#E74C3C')  # 珊瑚红
    ax.set_facecolor('#FFFFFF')  # 设置子图背景为白色
    ax.xaxis.label.set_color("k")
    ax.tick_params(axis='x', colors="k", width=5)
    ax.spines["top"].set_edgecolor("k")
    ax.set_xlabel('$V_p$ (km/s)')

    ax.set_ylabel("Depth (m)")
    if well == wells[0]:
        ax.set_ylim(2560, 4250)
    elif well == wells[1]:
        ax.set_ylim(2975, 4250)
    else:
        ax.set_ylim(3770, 4750)
    ax.invert_yaxis()
    ax.set_xlim(2, 5)
    ax.set_xticks([2, 3, 4, 5])
    ax.spines["top"].set_position(("axes", 1.02))
    ax.legend(loc='lower right')
    ax.set_title(label=well, fontsize=10, loc="center", color="k")

# Add Gidlines, Ticks, & Labels
for ax in axes:
    ax.grid(which='major', color='lightgrey', linestyle='-')
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.spines["top"].set_position(("axes", 1.02))

plt.tight_layout()
plt.show()