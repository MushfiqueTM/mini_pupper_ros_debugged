# Quick Reference: Upload to GitHub

## 🚀 One-Command Upload (Copy & Paste)

```bash
# Navigate to your repository
cd "c:\Users\mushf\OneDrive - The Hong Kong Polytechnic University\MangDang"

# Initialize git (if not already)
git init

# Configure git (if not already)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add remote
git remote add origin https://github.com/mangdangroboticsclub/mini_pupper_ros.git

# Stage all files
git add .

# Commit
git commit -m "feat: Complete ROS 2 Humble to Jazzy migration

- Ubuntu 22.04 → 24.04
- ROS 2 Humble → Jazzy
- Gazebo Classic → Harmonic
- Updated all packages for Jazzy compatibility
- Added comprehensive migration documentation"

# Create and push to ros2-jazzy branch
git checkout -b ros2-jazzy
git push -u origin ros2-jazzy

# Done! ✅
```

---

## 📋 Verify Upload

```bash
# Check branch exists on GitHub
git ls-remote --heads origin

# Check what was pushed
git log --oneline origin/ros2-jazzy -5
```

---

## 🔄 Make Scripts Executable (Important!)

```bash
# Make install scripts executable
chmod +x pupper_install.sh
chmod +x pc_install.sh
chmod +x run.sh
chmod +x entrypoint.sh

# Commit this change
git add -p
git commit -m "fix: Make shell scripts executable"
git push origin ros2-jazzy
```

---

## 🧪 Test Clone

```bash
# Test cloning works
cd /tmp
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy test_clone
ls test_clone

# Cleanup
rm -rf test_clone
```

---

## 🌿 Switch Default Branch (After Upload)

On GitHub website:
1. Go to repository → Settings → Branches
2. Change default branch to `ros2-jazzy`
3. Or keep `ros2` and merge `ros2-jazzy` into it

---

**That's it! Your code is ready to be cloned by users.** 🎉
