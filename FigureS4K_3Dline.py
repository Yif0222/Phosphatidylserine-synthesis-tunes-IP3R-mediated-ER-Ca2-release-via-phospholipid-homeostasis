import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
from matplotlib.colors import Normalize, to_rgba_array
import os
import sys

# ============================================================
# Usage: python FigureS4K_3Dline.py [input_file] [output_file]
#   input_file:  Excel file with sheets SC8, Dmut, TG-SC8, TG-Dmut
#                (default: "TG-SC8-DMUT.xlsx")
#   output_file: output PNG path (default: "FigureS4K_3Dline.png")
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) >= 2:
    xlsx_path = sys.argv[1]
else:
    xlsx_path = os.path.join(script_dir, 'TG-SC8-DMUT.xlsx')

if len(sys.argv) >= 3:
    out_path = sys.argv[2]
else:
    out_path = os.path.join(script_dir, 'FigureS4K_3Dline.png')
xl = pd.ExcelFile(xlsx_path)

all_data = {}
for sheet in xl.sheet_names:
    df = pd.read_excel(xlsx_path, sheet_name=sheet, header=None)
    df = df.iloc[1:].reset_index(drop=True)
    df = df.dropna(how='all')
    time = pd.to_numeric(df.iloc[:, 0], errors='coerce').values
    series_data = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').values
    mask = ~np.isnan(time)
    time = time[mask]
    series_data = series_data[mask, :]
    all_data[sheet] = {'time': time, 'series': series_data}

# ============================================================
# Unified limits across all 4 subplots
# ============================================================
all_t = np.concatenate([d['time'] for d in all_data.values()])
all_vals = np.concatenate([d['series'].flatten() for d in all_data.values()])
all_vals = all_vals[~np.isnan(all_vals)]

T_MIN, T_MAX = all_t.min(), all_t.max()
Z_MIN, Z_MAX = all_vals.min(), all_vals.max()
N_MAX = max(d['series'].shape[1] for d in all_data.values())

xlim = (T_MIN - 20, T_MAX + 20)
ylim = (-3, N_MAX + 3)
zlim = (Z_MIN - 0.2, Z_MAX + 0.3)

# Common time grid (3-second step, same as original data)
common_t = np.arange(0, T_MAX + 1, 3)

# ============================================================
# Color map: viridis_r → low index = yellow, high index = purple
# ============================================================
cmap = cm.viridis_r
order = ['SC8', 'Dmut', 'TG-SC8', 'TG-Dmut']

fig = plt.figure(figsize=(16, 13))

for idx, sheet_name in enumerate(order):
    ax = fig.add_subplot(2, 2, idx + 1, projection='3d')
    data = all_data[sheet_name]
    time = data['time']
    series_data = data['series']
    n_series = series_data.shape[1]

    # Align each series to the common time grid (linear interpolation)
    Z = np.full((len(common_t), n_series), np.nan)
    for i in range(n_series):
        z = series_data[:, i]
        valid = ~np.isnan(z)
        if valid.sum() < 2:
            continue
        Z[:, i] = np.interp(common_t, time[valid], z[valid])

    # 2D mesh: X = time, Y = series index
    X, Y = np.meshgrid(common_t, np.arange(n_series), indexing='ij')

    # Face colors based on series index (Y)
    norm = Normalize(vmin=0, vmax=N_MAX - 1)
    # Color per row (series)
    row_colors = cmap(norm(np.arange(n_series)))
    # tile to (len(common_t)-1, n_series-1, 4) for each quad
    facecolors = np.zeros((X.shape[0] - 1, X.shape[1] - 1, 4))
    for i in range(facecolors.shape[1]):
        color = to_rgba_array(row_colors[i])[0]
        facecolors[:, i, :] = color

    # Mask out NaN quadrilaterals so different time-length series do not
    # connect across missing data
    valid_mask = ~np.isnan(Z)
    # A quad is valid if all four corners are valid
    quad_valid = (valid_mask[:-1, :-1] & valid_mask[1:, :-1] &
                  valid_mask[:-1, 1:] & valid_mask[1:, 1:])
    # Hide invalid faces by setting alpha to 0
    facecolors[~quad_valid, 3] = 0

    # Draw surface (filled mountain style)
    surf = ax.plot_surface(X, Y, Z, facecolors=facecolors,
                          rstride=1, cstride=1, linewidth=0,
                          antialiased=False, shade=False, alpha=0.95)

    # Optional: thin top edge lines for sharper peaks
    for i in range(n_series):
        z = Z[:, i]
        valid = ~np.isnan(z)
        if valid.sum() < 2:
            continue
        ax.plot(common_t[valid], [i] * valid.sum(), z[valid],
                color='black', linewidth=0.15, alpha=0.3)

    # ---- Clean style ----
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('w')
    ax.yaxis.pane.set_edgecolor('w')
    ax.zaxis.pane.set_edgecolor('w')
    ax.grid(True, alpha=0.15)

    ax.set_title(sheet_name, fontsize=13, fontweight='bold', pad=2)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_zlim(zlim)
    ax.view_init(elev=25, azim=-70)

    ax.xaxis.set_major_locator(plt.MaxNLocator(6))
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))
    ax.zaxis.set_major_locator(plt.MaxNLocator(5))
    ax.tick_params(labelsize=8)

    # Colorbar (based on global N_MAX so all four match)
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.35, aspect=10, pad=0.02)
    cbar.set_label('Series', rotation=270, labelpad=10, fontsize=8)
    cbar.ax.tick_params(labelsize=7)

plt.subplots_adjust(wspace=0.02, hspace=0.15,
                    left=0.05, right=0.92, top=0.95, bottom=0.05)

# ============================================================
# Save
# ============================================================
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f'Saved: {out_path}')
