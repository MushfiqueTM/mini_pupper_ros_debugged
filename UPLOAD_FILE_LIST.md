# Files to Upload to GitHub - Complete List

> **Total: 35+ files modified, 5 new files created**

---

## 📁 New Documentation Files (5 files)

These are NEW files created during migration:

| File | Purpose | Size |
|------|---------|------|
| `MIGRATION_JAZZY.md` | Complete migration guide | ~13 KB |
| `MIGRATION_SUMMARY.md` | Summary of all changes | ~8 KB |
| `MIGRATION_TODO.md` | User's personal TODO list | ~9 KB |
| `REFERENCE_REPOSITORIES.md` | Reference repo analysis | ~5 KB |
| `GITHUB_UPLOAD_GUIDE.md` | This upload guide | ~11 KB |

**Action:** Add all to git

---

## 🔧 Root Configuration Files (12 files)

### Updated Files:

| File | Changes |
|------|---------|
| `README.md` | Updated badges, ROS 2 Jazzy notice |
| `CONTRIBUTING.md` | Updated for Jazzy development |
| `pupper_install.sh` | Ubuntu 24.04, ROS Jazzy, new deps |
| `pc_install.sh` | Ubuntu 24.04, ROS Jazzy, new deps |
| `Dockerfile.tracking` | `ros:jazzy-ros-base` |
| `.minipupper.repos` | New lidar driver |
| `.github/workflows/industrial_ci.yml` | `ROS_DISTRO: jazzy` |
| `.github/workflows/lint.yml` | Python 3.12 |
| `docs/detailed-setup-guide.md` | Updated instructions |

### Unchanged Files (but included):

| File | Status |
|------|--------|
| `.gitignore` | Already comprehensive ✓ |
| `LICENSE` | No change needed |
| `NOTICES.md` | No change needed |
| `CODE_OF_CONDUCT.md` | No change needed |

**Action:** Add all to git

---

## 📦 Package Files (All 13 Packages Updated)

### 1. mini_pupper_bringup
- `package.xml` (v0.2.0)
- `CMakeLists.txt` (CMake 3.8)

### 2. mini_pupper_interfaces
- `package.xml` (v1.0.0)
- `CMakeLists.txt` (builtin_interfaces)
- `msg/*.msg` (unchanged)
- `srv/*.srv` (unchanged)

### 3. mini_pupper_driver
- `package.xml` (v1.0.0)
- `setup.py` (v1.0.0)
- `launch/lidar_ld06.launch.py` (NEW dual driver support)

### 4. mini_pupper_description
- `package.xml` (v1.0.0)
- `CMakeLists.txt` (CMake 3.8)
- `urdf/mini_pupper_2/mini_pupper_description.urdf.xacro` (Gazebo Harmonic plugins)
- `urdf/mini_pupper/mini_pupper_description.urdf.xacro` (Gazebo Harmonic plugins)
- `urdf/mini_pupper/d435.urdf.xacro` (camera plugin notes)

### 5. stanford_controller
- `package.xml` (v2.0.0)
- `setup.py` (v2.0.0)

### 6. mini_pupper_tracking
- `package.xml` (v1.0.0)
- `setup.py` (v1.0.0)

### 7. mini_pupper_navigation
- `package.xml` (v1.0.0)
- `CMakeLists.txt` (CMake 3.8)

### 8. mini_pupper_slam
- `package.xml` (v1.1.0)
- `CMakeLists.txt` (unchanged)

### 9. mini_pupper_simulation ⭐ CRITICAL
- `package.xml` (v2.0.0) - Gazebo Harmonic deps
- `CMakeLists.txt` - gz deps
- `launch/gazebo.launch.py` - ros_gz_sim
- `launch/main.launch.py` - ros_gz_sim create
- `launch/ros2_controllers.launch.py` - timeout params
- `config/gazebo_params.yaml` - Harmonic params

### 10. mini_pupper_dance
- `package.xml` (v1.0.0)
- `setup.py` (v1.0.0)

### 11. mini_pupper_music
- `package.xml` (v1.1.0)
- `setup.py` (v1.1.0)

### 12. mini_pupper_recognition
- `package.xml` (v1.0.0)
- `setup.py` (v1.0.0)

### 13. mini_pupper_fleet
- `package.xml` (v1.0.0)
- `CMakeLists.txt` (unchanged)

**Action:** Add all to git

---

## 📝 Key File Categories Summary

### By Change Type:

| Category | Count | Files |
|----------|-------|-------|
| **New Files** | 5 | Migration docs, guides |
| **Updated package.xml** | 13 | All packages |
| **Updated CMakeLists.txt** | 5 | Build configs |
| **Updated setup.py** | 6 | Python packages |
| **Updated Launch Files** | 3 | Gazebo migration |
| **Updated URDF** | 3 | Plugin names |
| **Updated Scripts** | 2 | Install scripts |
| **Updated CI/CD** | 2 | GitHub Actions |

### By Criticality:

| Level | Files |
|-------|-------|
| 🔴 **CRITICAL** | `mini_pupper_simulation/`, `pupper_install.sh`, `pc_install.sh`, `.minipupper.repos` |
| 🟡 **IMPORTANT** | URDF files, lidar launch, package.xml files |
| 🟢 **DOCUMENTATION** | Migration docs, README updates |

---

## ✅ Git Add Commands

### Add Everything at Once:
```bash
git add .
```

### Or Add Selectively:
```bash
# Documentation
git add MIGRATION_*.md REFERENCE_*.md GITHUB_*.md UPLOAD_*.md

# Root config
git add README.md CONTRIBUTING.md pupper_install.sh pc_install.sh Dockerfile.tracking .minipupper.repos

# CI/CD
git add .github/workflows/

# All packages
git add mini_pupper_*/

# Docs
git add docs/
```

---

## 🔍 Verify Before Commit

### Check What's Staged:
```bash
git status
```

Expected output should show:
- `M` (Modified) for updated files
- `A` (Added) for new files
- No `?` (untracked) for files you want to include

### Check File Count:
```bash
git status --short | wc -l
```

Should be around **50-100 files** (depending on how many were already tracked).

---

## 📊 Repository Size Check

### Before Push:
```bash
# Check repository size
du -sh .

# Check what's taking space
find . -type f -size +1M -not -path "./.git/*" | head -20
```

**Expected:** Should be < 100 MB (mostly URDF meshes)

**If too large:** Check for accidentally included:
- Build artifacts (`build/`, `install/`, `log/`)
- Large mesh files
- Bag files
- Python cache

### Ensure .gitignore is Working:
```bash
# These should NOT appear in git status
git status | grep -E "(build/|install/|log/|__pycache__|\.pyc)"
```

If they appear, .gitignore needs updating.

---

## 🎯 Final Verification Commands

```bash
# 1. Check all modified files are staged
git status

# 2. Review commit message
git commit -m "feat: Migrate from ROS 2 Humble to ROS 2 Jazzy

Major changes:
- Ubuntu 22.04 → 24.04 (Noble Numbat)
- ROS 2 Humble → Jazzy Jalisco
- Gazebo Classic → Gazebo Harmonic (gz)
- Python 3.10 → 3.12
- Updated 13 packages with Jazzy dependencies
- Migrated Gazebo launch files to ros_gz_sim
- Updated URDF with Gazebo Harmonic plugins
- Added new lifecycle-based lidar driver
- Added comprehensive migration documentation

BREAKING CHANGE: Requires Ubuntu 24.04 and ROS 2 Jazzy"

# 3. Create branch
git checkout -b ros2-jazzy

# 4. Push
git push -u origin ros2-jazzy

# 5. Verify
git ls-remote --heads origin
```

---

## 🌐 After Upload - GitHub Settings

### 1. Set Branch Protection (Optional but Recommended):
```
GitHub → Repository → Settings → Branches → Add rule
- Branch name pattern: ros2-jazzy
- Require pull request reviews before merging
- Require status checks to pass
```

### 2. Make Branch Default (Optional):
```
GitHub → Repository → Settings → Branches
- Default branch: ros2-jazzy
```

### 3. Create Release:
```
GitHub → Repository → Releases → Draft new release
- Tag: v2.0.0-jazzy
- Target: ros2-jazzy
- Title: ROS 2 Jazzy Release
- Body: Copy from GITHUB_UPLOAD_GUIDE.md
```

---

## 📞 Troubleshooting Upload

### Problem: "fatal: not a git repository"
**Solution:**
```bash
git init
git add .
```

### Problem: "Permission denied"
**Solution:**
```bash
# Use HTTPS with token
git remote set-url origin https://TOKEN@github.com/mangdangroboticsclub/mini_pupper_ros.git
```

### Problem: "Updates were rejected"
**Solution:**
```bash
# Force push (only if you're sure!)
git push -f origin ros2-jazzy

# Or merge first
git pull origin ros2-jazzy --rebase
git push origin ros2-jazzy
```

### Problem: "Large file" error
**Solution:**
```bash
# Find large files
find . -type f -size +10M

# Remove from staging
git reset HEAD <large-file>

# Add to .gitignore
echo "<large-file>" >> .gitignore
```

---

**Ready to upload! Follow GITHUB_UPLOAD_GUIDE.md for detailed steps.** 🚀
