# Code for "Phosphatidylserine synthesis tunes IP3R-mediated ER Ca2+ release via phospholipid homeostasis"

This repository contains the Python scripts used to generate selected figures in the manuscript.

## Contents

| File                  | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `Figure1J_PCA.py`     | PCA analysis of total lipidomics data with 95% confidence ellipses (Figure 1J). |
| `FigureS4K_3Dline.py` | 3D surface plot for TG-SC8-Dmut time-series data (Figure S4K). |

## Requirements

- Python >= 3.8
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Figure 1J

```bash
python Figure1J_PCA.py
```

Or with custom input/output paths:

```bash
python Figure1J_PCA.py path/to/data.txt path/to/output.png
```

- **Input:** tab-separated lipid abundance table (`Total lipids.txt`). First column: `Species`; remaining columns: sample abundances.
- **Output:** `Figure1J_PCA.png`

### Figure S4K

```bash
python FigureS4K_3Dline.py
```

Or with custom input/output paths:

```bash
python FigureS4K_3Dline.py path/to/data.xlsx path/to/output.png
```

- **Input:** Excel file (`TG-SC8-DMUT.xlsx`) with four sheets: `SC8`, `Dmut`, `TG-SC8`, `TG-Dmut`.
- **Output:** `FigureS4K_3Dline.png`

## Data availability

The raw lipidomics and proteomics datasets are available via the repositories listed in the manuscript's **Resource Availability** section.

## License

This code is released under the MIT License.
