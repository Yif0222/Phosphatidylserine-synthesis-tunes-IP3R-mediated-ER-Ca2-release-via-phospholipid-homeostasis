import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import os

# ============================================================
# Config
# ============================================================
DATA_PATH = 'C:/Users/zhouy/Downloads/Total lipids.txt'
OUTPUT_PATH = 'C:/Users/zhouy/WorkBuddy/2026-07-14-08-20-47/Figure1J_Total_Lipids_PCA.png'

# 分组与配色
GROUPS = {
    'ppl': ['ppl①', 'ppl②', 'ppl③', 'ppl④', 'ppl⑤'],
    'pss': ['pss①', 'pss②', 'pss③', 'pss④', 'pss⑤'],
    'bbc': ['bbc①', 'bbc②', 'bbc③', 'bbc④', 'bbc⑤'],
    'sre': ['sre①', 'sre②', 'sre③', 'sre④', 'sre⑤']
}

GROUP_COLORS = {
    'ppl': '#E63946',
    'pss': '#2A9D8F',
    'bbc': '#F4A261',
    'sre': '#264653'
}

GROUP_NAMES = {
    'ppl': 'PPL',
    'pss': 'PSS',
    'bbc': 'BBC',
    'sre': 'SRE'
}

# ============================================================
# 读取数据
# ============================================================
df = pd.read_csv(DATA_PATH, sep='\t', index_col=0)

# ============================================================
# 异常值检测（IQR）
# ============================================================
def detect_outliers_iqr(data_df, multiplier=1.5, min_keep=10):
    outlier_indices = set()
    for idx in data_df.index:
        values = data_df.loc[idx].values
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        lower = Q1 - multiplier * IQR
        upper = Q3 + multiplier * IQR
        if np.any((values < lower) | (values > upper)):
            outlier_indices.add(idx)
    if (data_df.shape[0] - len(outlier_indices)) < min_keep:
        outlier_indices = set()
        for idx in data_df.index:
            values = data_df.loc[idx].values
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            if np.any((values < Q1 - 2 * IQR) | (values > Q3 + 2 * IQR)):
                outlier_indices.add(idx)
        if (data_df.shape[0] - len(outlier_indices)) < min_keep:
            return []
    return list(outlier_indices)

outliers = detect_outliers_iqr(df, multiplier=1.5, min_keep=10)
cleaned_df = df.drop(outliers) if len(outliers) > 0 else df
print(f"Total lipids: {df.shape[0]} -> {cleaned_df.shape[0]} (removed {len(outliers)})")

# ============================================================
# PCA
# ============================================================
X = cleaned_df.T.values
X_scaled = StandardScaler().fit_transform(X)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
explained = pca.explained_variance_ratio_ * 100
print(f"PCA: PC1={explained[0]:.1f}%, PC2={explained[1]:.1f}%")

# ============================================================
# 95% 置信椭圆
# ============================================================
def confidence_ellipse(x, y, ax, n_std=2.0, facecolor='none', edgecolor='red',
                       alpha=0.22, linewidth=2.5):
    if len(x) < 2:
        return
    cov = np.cov(x, y)
    if cov[0, 0] == 0 or cov[1, 1] == 0:
        return
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1]) if np.sqrt(cov[0, 0] * cov[1, 1]) > 0 else 0
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, edgecolor=edgecolor, alpha=alpha, linewidth=linewidth)
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)
    transf = transforms.Affine2D().rotate_deg(45).scale(scale_x, scale_y).translate(mean_x, mean_y)
    ellipse.set_transform(transf + ax.transData)
    ax.add_patch(ellipse)

# ============================================================
# 绘图
# ============================================================
fig, ax = plt.subplots(figsize=(9, 8))

columns = cleaned_df.columns
for group_name, samples in GROUPS.items():
    indices = [columns.get_loc(s) for s in samples if s in columns]
    if len(indices) == 0:
        continue
    gx = X_pca[indices, 0]
    gy = X_pca[indices, 1]
    color = GROUP_COLORS[group_name]

    ax.scatter(gx, gy, c=color, s=250, alpha=0.9,
               edgecolors='white', linewidth=2.5,
               label=GROUP_NAMES[group_name], zorder=5)

    for i, (x, y) in enumerate(zip(gx, gy)):
        sample_idx = samples[i].replace(group_name, '')
        ax.annotate(f'{group_name.upper()}{sample_idx}',
                    (x, y), xytext=(7, 7), textcoords='offset points',
                    fontsize=11, fontweight='bold', alpha=0.85)

    if len(gx) >= 2:
        confidence_ellipse(gx, gy, ax, n_std=2.0,
                           facecolor=color, edgecolor=color, alpha=0.22, linewidth=2.5)

ax.set_xlabel(f'PC1 ({explained[0]:.1f}%)', fontsize=15, fontweight='bold')
ax.set_ylabel(f'PC2 ({explained[1]:.1f}%)', fontsize=15, fontweight='bold')
ax.set_title('PCA Analysis - Total Lipids\n(with 95% Confidence Ellipses)',
             fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
ax.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
ax.legend(loc='upper left', fontsize=12, framealpha=0.9, edgecolor='gray')

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"Saved: {OUTPUT_PATH}")
