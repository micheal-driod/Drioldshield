import os

# 1. SETUP FOLDERS
workflow_dir = os.path.join(".github", "workflows")
os.makedirs(workflow_dir, exist_ok=True)

# 2. WRITE A "BARE METAL" BUILD.YML (No Docker, No Permission Errors)
# This installs all the tools directly on the server.
build_yml = """name: Build Android APK
on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Install Java 17 (Required for modern Android builds)
      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      # Install Python 3.10
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      # Install the heavy system libraries Android needs
      - name: Install System Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential git zip unzip autoconf libtool pkg-config \
            libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev \
            libssl-dev zlib1g-dev

      # Install Buildozer
      - name: Install Buildozer
        run: |
          pip install --upgrade pip
          pip install buildozer cython==0.29.33

      # Build! (Force accept all licenses)
      - name: Build with Buildozer
        run: |
          yes | buildozer android debug

      # Upload the result
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: bin/*.apk
"""

with open(os.path.join(workflow_dir, "build.yml"), "w") as f:
    f.write(build_yml)
    print("✅ Fixed .github/workflows/build.yml")

# 3. WRITE A SAFE BUILDOZER.SPEC
# This version explicitly accepts the SDK license to prevent hanging.
spec_content = """[app]
title = DroidShield
package.name = droidshield
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,android,pyjnius,requests

# PERMISSIONS
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# ANDROID CONFIG
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# CRITICAL FOR GITHUB ACTIONS
# If this is False, the build fails waiting for you to type 'y'
android.accept_sdk_license = True

# VERSIONS (These work best with Java 17)
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
"""

with open("buildozer.spec", "w") as f:
    f.write(spec_content)
    print("✅ Fixed buildozer.spec (License acceptance set to True)")

print("🎉 Files repaired. Ready to push.")