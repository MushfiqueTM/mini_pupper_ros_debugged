# GitHub Upload Guide for ROS 2 Jazzy Migration

> **This guide helps you upload all migration files to GitHub for cloning.**

---

## 📋 Pre-Upload Checklist

Before uploading, verify these files are ready:

### ✅ Root Level Files (All Updated)
- [x] `README.md` - Updated for Jazzy
- [x] `CONTRIBUTING.md` - Updated for Jazzy
- [x] `pupper_install.sh` - Updated for Ubuntu 24.04 + Jazzy
- [x] `pc_install.sh` - Updated for Ubuntu 24.04 + Jazzy
- [x] `Dockerfile.tracking` - Updated to `ros:jazzy-ros-base`
- [x] `.minipupper.repos` - Updated with new lidar driver
- [x] `.gitignore` - Already comprehensive
- [x] `.github/workflows/industrial_ci.yml` - Updated to `jazzy`
- [x] `.github/workflows/lint.yml` - Updated to Python 3.12

### ✅ Documentation (New Files)
- [x] `MIGRATION_JAZZY.md` - Complete migration guide
- [x] `MIGRATION_SUMMARY.md` - Summary of changes
- [x] `MIGRATION_TODO.md` - User TODO list
- [x] `REFERENCE_REPOSITORIES.md` - Reference repo analysis
- [x] `docs/detailed-setup-guide.md` - Updated

### ✅ Package Files (All Updated)
- [x] All 13 `package.xml` files - Updated versions + deps
- [x] All `CMakeLists.txt` files - Updated CMake min version
- [x] All `setup.py` files - Updated versions
- [x] `mini_pupper_simulation/launch/*.py` - Gazebo Harmonic
- [x] `mini_pupper_driver/launch/lidar_ld06.launch.py` - New lidar support
- [x] URDF files - Gazebo plugin updates

---

## 🚀 Step-by-Step Upload Instructions

### Step 1: Initialize Git Repository (if not already)

```bash
cd c:\Users\mushf\OneDrive - The Hong Kong Polytechnic University\MangDang

# Check if already a git repo
ls -la .git

# If NOT a git repo, initialize it
git init

# If it IS a git repo, check status
git status
```

### Step 2: Configure Git (if not already configured)

```bash
# Set your name and email
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Verify
git config --list
```

### Step 3: Add Remote Repository

You have TWO options:

#### Option A: Create NEW Repository on GitHub

1. Go to https://github.com/mangdangroboticsclub
2. Click "New Repository"
3. Name: `mini_pupper_ros`
4. Make it Public
5. **DO NOT** initialize with README (we have one already)
6. Create repository
7. Copy the remote URL

#### Option B: Use EXISTING Repository

If the repository already exists:

```bash
# Check current remotes
git remote -v

# Add/Update origin
git remote add origin https://github.com/mangdangroboticsclub/mini_pupper_ros.git

# Or update existing
git remote set-url origin https://github.com/mangdangroboticsclub/mini_pupper_ros.git
```

### Step 4: Stage All Files

```bash
# Check what files will be added
git status

# Stage all files
git add .

# Verify staging
git status
```

### Step 5: Commit Changes

```bash
# Create a meaningful commit message
git commit -m "feat: Migrate from ROS 2 Humble to ROS 2 Jazzy

Major changes:
- Ubuntu 22.04 → 24.04 (Noble Numbat)
- ROS 2 Humble → Jazzy Jalisco
- Gazebo Classic → Gazebo Harmonic (gz)
- Python 3.10 → 3.12
- Updated all package.xml files with Jazzy dependencies
- Updated CMakeLists.txt minimum version to 3.8
- Migrated launch files from gazebo_ros to ros_gz_sim
- Updated URDF with Gazebo Harmonic plugin names
- Added new lidar driver (ldrobot-lidar-ros2) with lifecycle support
- Updated install scripts (pupper_install.sh, pc_install.sh)
- Added comprehensive migration documentation
- Updated CI/CD workflows for Jazzy

BREAKING CHANGE: This release requires Ubuntu 24.04 and ROS 2 Jazzy.
Previous ROS 2 Humble releases are no longer compatible."
```

### Step 6: Create and Push to Branch

```bash
# Create and checkout new branch for Jazzy migration
git checkout -b ros2-jazzy

# Push to GitHub
git push -u origin ros2-jazzy

# If you want to make it the default branch later:
# Go to GitHub repository → Settings → Branches → Set as default
```

### Step 7: Verify Upload

1. Go to https://github.com/mangdangroboticsclub/mini_pupper_ros
2. Check that `ros2-jazzy` branch exists
3. Verify all files are present
4. Check file contents are correct

---

## 🌿 Branch Strategy Recommendation

### Recommended Branch Setup:

```
main (or master)         ← Stable releases
├── ros2-humble          ← ROS 2 Humble (Ubuntu 22.04) - Legacy
└── ros2-jazzy           ← ROS 2 Jazzy (Ubuntu 24.04) - NEW ✨
    └── feature/xyz      ← Feature branches
```

### Branch Descriptions:

| Branch | Purpose | Target Users |
|--------|---------|--------------|
| `main` | Stable releases | End users |
| `ros2` | Development (was Humble, now becomes Jazzy) | Developers |
| `ros2-humble` | Legacy Humble support | Users on Ubuntu 22.04 |
| `ros2-jazzy` | New Jazzy development | Users on Ubuntu 24.04 |

### If You Want to Replace `ros2` Branch:

```bash
# Option 1: Merge Jazzy into existing ros2 branch
git checkout ros2
git merge ros2-jazzy
git push origin ros2

# Option 2: Force push (DANGEROUS - overwrites history)
git checkout ros2-jazzy
git push -f origin ros2-jazzy:ros2
```

---

## 📦 Files to Verify Before Pushing

### Must-Have Files for Cloning:

```
mini_pupper_ros/
├── .gitignore                          ✓
├── .github/
│   └── workflows/
│       ├── industrial_ci.yml           ✓ (jazzy)
│       └── lint.yml                    ✓ (python 3.12)
├── docs/
│   └── detailed-setup-guide.md         ✓ (updated)
├── mini_pupper_bringup/
│   ├── CMakeLists.txt                  ✓
│   ├── package.xml                     ✓ (v0.2.0)
│   ├── config/
│   └── launch/
├── mini_pupper_description/
│   ├── CMakeLists.txt                  ✓
│   ├── package.xml                     ✓ (v1.0.0)
│   └── urdf/                           ✓ (updated plugins)
├── mini_pupper_driver/
│   ├── package.xml                     ✓ (v1.0.0)
│   ├── setup.py                        ✓ (v1.0.0)
│   └── launch/
│       └── lidar_ld06.launch.py        ✓ (new driver support)
├── mini_pupper_simulation/
│   ├── CMakeLists.txt                  ✓ (gz deps)
│   ├── package.xml                     ✓ (v2.0.0)
│   └── launch/
│       ├── gazebo.launch.py            ✓ (gz)
│       ├── main.launch.py              ✓ (gz)
│       └── ros2_controllers.launch.py  ✓ (updated)
├── [other packages...]                 ✓ (all updated)
├── pupper_install.sh                   ✓ (jazzy)
├── pc_install.sh                       ✓ (jazzy)
├── Dockerfile.tracking                 ✓ (jazzy)
├── README.md                           ✓ (jazzy)
├── CONTRIBUTING.md                     ✓ (jazzy)
├── MIGRATION_JAZZY.md                  ✓ (new)
├── MIGRATION_SUMMARY.md                ✓ (new)
├── MIGRATION_TODO.md                   ✓ (new)
├── REFERENCE_REPOSITORIES.md           ✓ (new)
└── .minipupper.repos                   ✓ (new lidar)
```

---

## 🧪 Test Clone Instructions

After pushing, test that cloning works:

```bash
# Test 1: Fresh clone on Mini Pupper (Ubuntu 24.04)
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy mini_pupper_ros
cd mini_pupper_ros
./pupper_install.sh

# Test 2: Fresh clone on PC (Ubuntu 24.04)
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy mini_pupper_ros
cd mini_pupper_ros
./pc_install.sh

# Test 3: Verify branch checkout works
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git
cd mini_pupper_ros
git checkout ros2-jazzy
```

---

## 📝 Release Notes Template

Create a GitHub Release with this template:

```markdown
## ROS 2 Jazzy Migration Release

### ⚠️ Breaking Changes
- **Ubuntu**: 22.04 → 24.04 (Noble Numbat)
- **ROS 2**: Humble → Jazzy Jalisco
- **Gazebo**: Classic → Harmonic (gz)
- **Python**: 3.10 → 3.12

### ✨ New Features
- Gazebo Harmonic simulation support
- New lifecycle-based lidar driver
- Updated CHAMP controller for Jazzy
- Comprehensive migration documentation

### 📦 Installation

**Mini Pupper:**
\`\`\`bash
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy mini_pupper_ros
cd mini_pupper_ros
./pupper_install.sh
\`\`\`

**PC/Simulation:**
\`\`\`bash
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy mini_pupper_ros
cd mini_pupper_ros
./pc_install.sh
\`\`\`

### 📖 Documentation
- [Migration Guide](MIGRATION_JAZZY.md)
- [Migration Summary](MIGRATION_SUMMARY.md)
- [Setup Guide](docs/detailed-setup-guide.md)

### 🔧 Known Issues
- champ_gazebo contact sensor may not work with Gazebo Harmonic
- See [MIGRATION_TODO.md](MIGRATION_TODO.md) for full list

---

**Full Changelog**: Compare with previous release
```

---

## 🔗 Useful Git Commands

```bash
# Check status
git status

# See what changed
git diff

# See commit history
git log --oneline -20

# Check which files are tracked
git ls-files

# Check file size (avoid large binaries)
find . -type f -size +10M -not -path "./.git/*"

# Check repository size
du -sh .git

# Clean untracked files (BE CAREFUL)
git clean -n  # Preview
git clean -f  # Actually delete

# Undo last commit (if needed)
git reset --soft HEAD~1

# Rename branch
git branch -m old-name new-name
git push origin :old-name new-name
```

---

## ⚠️ Common Issues

### Issue 1: Large Files

**Problem:** Repository too big due to binary files

**Solution:**
```bash
# Check large files
find . -type f -size +10M

# Remove from git but keep locally
git rm --cached <file>

# Add to .gitignore
echo "*.bag" >> .gitignore
echo "*.pyc" >> .gitignore
```

### Issue 2: Authentication Failed

**Problem:** Can't push to GitHub

**Solution:**
```bash
# Use HTTPS with token
git remote set-url origin https://TOKEN@github.com/mangdangroboticsclub/mini_pupper_ros.git

# Or use SSH
git remote set-url origin git@github.com:mangdangroboticsclub/mini_pupper_ros.git
```

### Issue 3: Wrong Branch Name

**Problem:** Accidentally committed to wrong branch

**Solution:**
```bash
# Move commits to new branch
git checkout -b correct-branch
git push origin correct-branch

# Delete wrong branch (if needed)
git push origin --delete wrong-branch
```

---

## ✅ Final Checklist Before Upload

- [ ] All files are saved
- [ ] No sensitive data (passwords, keys) in files
- [ ] No large binary files (>10MB)
- [ ] All file permissions are correct
- [ ] Git configured with correct user info
- [ ] Remote URL is correct
- [ ] Commit message is descriptive
- [ ] Branch name follows convention (`ros2-jazzy`)
- [ ] README.md is up to date
- [ ] Install scripts are executable (`chmod +x *.sh`)

---

## 📞 Need Help?

If you encounter issues uploading:

1. Check git status: `git status`
2. Check git log: `git log --oneline`
3. Check remote: `git remote -v`
4. Check errors carefully

---

**Ready to upload!** 🚀
