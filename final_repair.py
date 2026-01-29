import os

# 1. SETUP FOLDERS
workflow_dir = os.path.join(".github", "workflows")
os.makedirs(workflow_dir, exist_ok=True)

# 2. WRITE THE WORKING BUILD.YML
# Key Fix: explicitly adding 'universe' repo and installing libncurses5/libtinfo5
build_yml = """name: Build Android APK
on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # 1. Set up Java 17 (Required)
      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      # 2. Set up Python 3.10
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      # 3. FIX: Install missing 'libtinfo5' manually
      - name: Install System Dependencies
        run: |
          sudo add-apt-repository universe
          sudo apt-get update
          sudo apt-get install -y libncurses5 libtinfo5
          sudo apt-get install -y build-essential git zip unzip autoconf libtool pkg-config zlib1g-dev cmake libffi-dev libssl-dev

      # 4. Install Buildozer
      - name: Install Buildozer
        run: |
          pip install --upgrade pip
          pip install buildozer cython==0.29.33

      # 5. Build (Pre-accept licenses via 'yes' pipe)
      - name: Build with Buildozer
        run: |
          yes | buildozer android debug

      # 6. Upload APK
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: bin/*.apk
"""

with open(os.path.join(workflow_dir, "build.yml"), "w") as f:
    f.write(build_yml)
    print("✅ Created build.yml with 'libtinfo5' fix.")

# 3. ENSURE BUILDOZER.SPEC IS CORRECT
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

# CRITICAL SETTINGS
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
"""

with open("buildozer.spec", "w") as f:
    f.write(spec_content)
    print("✅ Verified buildozer.spec.")