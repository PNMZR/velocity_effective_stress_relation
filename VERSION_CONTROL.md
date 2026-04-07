# Version Control Documentation

## Project Information
- Project Name: Stress dependence of P- and S-Wave velocities in rocks: New models and applications
- Local Directory: `e:\library\velocity_effective_stress_relation`
- Remote Repository: `https://github.com/PNMZR/velocity_effective_stress_relation`

## Version Control Scope

### Files to be managed:
- All `.py` files under the `src` directory
- All `.xlsx` files under the `src/data` directory

### Files not to be managed:
- The `src/data/temp` directory and all its contents
- Other non-`.py` and non-`.xlsx` files

## Initialization and Configuration

### 1. Initialize Git Repository

Execute the following command in the project root directory:

```bash
git init
```

### 2. Create .gitignore File

Create a `.gitignore` file in the project root directory with the following content:

```gitignore
# Exclude all files
*

# Include only .py files under the src directory
!src/
!src/**/*.py

# Include only .xlsx files under the data directory
!src/data/
!src/data/**/*.xlsx

# Exclude the temp subdirectory under data
src/data/temp/

# Exclude temporary files and system files
*.tmp
*.temp
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Exclude virtual environment
myenv/

# Exclude editor configurations
.vscode/
.idea/
.spyproject/
```

### 3. Verify .gitignore Configuration

Execute the following command to check the current status and confirm that .gitignore is configured correctly:

```bash
git status
```

## Connect to Remote Repository

### 1. Add Remote Repository

```bash
git remote add origin https://github.com/PNMZR/velocity_effective_stress_relation.git
```

### 2. Verify Remote Repository Configuration

```bash
git remote -v
```

## Commit and Push

### 1. Initial Commit

```bash
# Add all eligible files
git add .

# Commit changes
git commit -m "Initialize repository: Add paper-related code and data"

# Push to the main branch of the remote repository
git push -u origin main
```

### 2. Subsequent Commits

After each modification to code or data, execute the following commands:

```bash
# Add changed files
git add .

# Commit changes
git commit -m "Describe your changes"

# Push to remote repository
git push
```

## Branch Management

### Create New Branch

```bash
git checkout -b feature-branch
```

### Switch Branch

```bash
git checkout main
```

### Merge Branch

```bash
git checkout main
git merge feature-branch
```

## Common Operations

### View Commit History

```bash
git log
```

### View File Changes

```bash
git diff
```

### Undo Changes

```bash
# Undo changes in working directory
git checkout -- <file>

# Undo changes in staging area
git reset HEAD <file>
```

## Notes

1. **Permission Verification**: When pushing, Git will verify your permissions for the remote repository. Ensure you are the repository owner or a collaborator.
2. **Regular Commits**: Develop the habit of committing changes regularly to maintain a clear version history.
3. **Meaningful Commit Messages**: Commit messages should clearly describe the content and purpose of the changes.
4. **Backup Important Data**: Although Git manages versions, it is still recommended to make additional backups of important data.
5. **Avoid Committing Large Files**: Git is not suitable for managing large binary files, such as large datasets or model files.

## Troubleshooting

### Push Failure

If push fails, it may be due to the following reasons:

1. **Permission Issues**: Ensure you have write permissions for the remote repository
2. **Network Issues**: Check if your network connection is normal
3. **Branch Protection**: If the remote repository has branch protection rules, you may need to make changes through Pull Request

### Version Conflict

If you encounter version conflicts, follow these steps:

1. View conflict files: `git status`
2. Manually resolve conflicts (edit conflict files)
3. Mark conflicts as resolved: `git add <conflicted-file>`
4. Complete the commit: `git commit`

## Contact Information

If you encounter version control-related issues, please refer to the Git official documentation or contact the project manager.