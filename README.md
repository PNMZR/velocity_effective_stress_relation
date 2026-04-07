# velocity_effective_stress_relation

## Repository Introduction

This repository contains the source code and data for the paper **"Stress dependence of P- and S-Wave velocities in rocks: New models and applications"**.

The repository provides the implementation of new models for analyzing the relationship between P-wave and S-wave velocities in rocks and stress, along with the data used in the study.

## Directory Structure

```
velocity_effective_stress_relation/
├── src/                  # Source code directory
│   ├── data/             # Data directory
│   │   ├── temp/         # Temporary data (not under version control)
│   │   └── *.xlsx        # Data files used in the paper
│   ├── *.py              # Python scripts implementing the models
├── images/               # Images and figures
├── manuscript/           # Paper manuscript files
├── README.md             # Repository documentation
├── VERSION_CONTROL.md    # Version control instructions
└── .gitignore            # Git ignore file configuration
```

## Key Files

### Source Code
- `src/birch_rock_velocity_fit.py`: Implementation of velocity-stress relationship models
- `src/case_study.py`: Case studies using the models
- `src/sensitivity_analysis.py`: Sensitivity analysis of model parameters
- `src/nu_heatmap.py`: Poisson's ratio analysis
- `src/plot_cl_cs_vs_nu.py`: Velocity vs. Poisson's ratio plotting

### Data Files
- `src/data/GOODWYN-6.xlsx`: Goodwyn-6 well data
- `src/data/WILCOX-1.xlsx`: Wilcox-1 well data
- `src/data/WILCOX-2.xlsx`: Wilcox-2 well data
- `src/data/birch1960_Simmons1964.xlsx`: Experimental data from Birch (1960) and Simmons (1964)

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/PNMZR/velocity_effective_stress_relation.git
   cd velocity_effective_stress_relation
   ```

2. Install dependencies:
   ```bash
   pip install numpy matplotlib pandas
   ```

3. Run the scripts to reproduce the results from the paper:
   ```bash
   python src/case_study.py
   python src/sensitivity_analysis.py
   python src/birch_rock_velocity_fit.py
   ```

## License

This project is licensed under the MIT License.

## Contact Information

- Author: Rong Zhao
- Email: zhaorong171@mails.ucas.edu.cn
- Project URL: https://github.com/PNMZR/velocity_effective_stress_relation