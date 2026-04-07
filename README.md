# velocity_effective_stress_relation

## Project Introduction

This project aims to study the relationship between P-wave and S-wave velocities in rocks and stress, develop new models, and explore their applications. The project title is "Stress dependence of P- and S-Wave velocities in rocks: New models and applications".

## Directory Structure

```
velocity_effective_stress_relation/
├── src/                  # Source code directory
│   ├── data/             # Data directory
│   │   ├── temp/         # Temporary data (not under version control)
│   │   └── *.xlsx        # Data files
│   ├── *.py              # Python scripts
├── images/               # Images directory
├── manuscript/           # Manuscript directory
├── myenv/                # Virtual environment (not under version control)
├── README.md             # Project documentation
├── VERSION_CONTROL.md    # Version control instructions
└── .gitignore            # Git ignore file configuration
```

## Main Features

- Analyze the relationship between P-wave and S-wave velocities in rocks and stress
- Develop new velocity-stress relationship models
- Apply models for case studies
- Sensitivity analysis
- Data visualization

## Installation Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/PNMZR/velocity_effective_stress_relation.git
   cd velocity_effective_stress_relation
   ```

2. Create a virtual environment (optional):
   ```bash
   python -m venv myenv
   # Windows
   myenv\Scripts\activate
   # Linux/Mac
   source myenv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install numpy matplotlib pandas
   ```

## Usage

1. Prepare data: Place data files in the `src/data/` directory

2. Run scripts:
   ```bash
   # Run case study
   python src/case_study.py
   
   # Run sensitivity analysis
   python src/sensitivity_analysis.py
   
   # Run velocity fitting
   python src/birch_rock_velocity_fit.py
   ```

3. View results: Results will be output to the console and may generate charts

## Data Description

- `src/data/GOODWYN-6.xlsx`: Goodwyn-6 well data
- `src/data/WILCOX-1.xlsx`: Wilcox-1 well data
- `src/data/WILCOX-2.xlsx`: Wilcox-2 well data
- `src/data/birch1960_Simmons1964.xlsx`: Experimental data from Birch (1960) and Simmons (1964)

## Version Control

This project uses Git for version control. For detailed version control instructions, please refer to the `VERSION_CONTROL.md` file.

## Contribution

Contributions and suggestions are welcome. If you have any questions, please submit them through GitHub Issues.

## License

This project is licensed under the MIT License.

## Contact Information

- Author: Rong Zhao
- Email: zhaorong171@mails.ucas.edu.cn
- Project URL: https://github.com/PNMZR/velocity_effective_stress_relation