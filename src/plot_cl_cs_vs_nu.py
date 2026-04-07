import numpy as np
import matplotlib.pyplot as plt


def plot_cl_cs_vs_nu_improved():
    """
    改进版：限制Y轴、平滑曲线、仅标注岩石材料
    """
    # 更精细的采样（避开端点附近）
    nu = np.linspace(-0.99, 0.49, 2000)
    
    # 计算公式
    c_l = (13 - 40*nu + 55*nu**2) / (2 * (1 - 2*nu) * (7 - 5*nu))
    c_s = (8 - 10*nu) / (7 - 5*nu)
    
    
    # Nature配色
    color_cl = '#4C72B0'   # 深蓝
    color_cs = '#C44E52'   # 深红
    
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    # 绘制c_l（左轴）
    ax1.plot(nu, c_l, color=color_cl, linewidth=2.5, 
             label=r'$c_l$', zorder=2)
    ax1.set_xlabel(r"$\nu_m$", fontsize=14)
    ax1.set_ylabel(r'$c_l$', color=color_cl, fontsize=14)
    ax1.tick_params(axis='y', labelcolor=color_cl, labelsize=11)
    ax1.set_xlim(-1, 0.5)
    ax1.set_ylim(0, 12)  # 限制Y轴
    
    # 绘制c_s（右轴）
    ax2 = ax1.twinx()
    ax2.plot(nu, c_s, color=color_cs, linewidth=2.5, 
             label=r'$c_s$', zorder=2)
    ax2.set_ylabel(r'$c_s$', color=color_cs, fontsize=14)
    ax2.tick_params(axis='y', labelcolor=color_cs, labelsize=11)
    ax2.set_ylim(0, 2)
    
    # 添加岩石标注区域（只保留岩石）
    # 根据你的描述：0.05到0.45覆盖大部分岩石
    rock_nu_min = 0.05
    rock_nu_max = 0.45
    ax1.axvspan(rock_nu_min, rock_nu_max, facecolor='#CD853F', alpha=0.25, zorder=1)
    ax1.text((rock_nu_min + rock_nu_max)/2, 7.5, 'Most Rocks', 
             ha='center', fontsize=11, fontweight='bold', color='#8B4513')
    
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, 
              loc='upper left',
              ncol=1, fontsize=12, frameon=False)
    
    # 美化边框
    ax1.spines['left'].set_color(color_cl)
    ax1.spines['left'].set_linewidth(1.5)
    ax2.spines['right'].set_color(color_cs)
    ax2.spines['right'].set_linewidth(1.5)
    
    # 网格线（轻量级）
    ax1.grid(True, linestyle=':', alpha=0.3, axis='both')
    ax1.set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()

# 调用
plot_cl_cs_vs_nu_improved()