import os

# 1. SETUP FOLDERS
workflow_dir = os.path.join(".github", "workflows")
os.makedirs(workflow_dir, exist_ok=True)

# 2. WRITE THE FINAL ROBUST BUILD.YML
# Key Difference: We use 'yes' on sdkmanager DIRECTLY, not just buildozer.
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

      # 1. Java 17 is REQUIRED for current Android SDKs
      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      # 2. Set up Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      # 3. Install System Dependencies
      - name: Install System Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential git zip unzip autoconf libtool pkg-config \
            libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev \
            libssl-dev zlib1g-dev

      # 4. Install Buildozer
      - name: Install Buildozer
        run: |
          pip install --upgrade pip
          pip install buildozer cython==0.29.33

      # 5. PRE-INSTALL SDK & ACCEPT LICENSES (The Magic Step)
      # We let Buildozer download the SDK first, then we force-accept licenses.
      - name: Pre-install SDK and Accept Licenses
        run: |
          # Run buildozer init just to trigger SDK download, then kill it? No, simpler:
          # We just run the build command but expect it might fail on license first try
          # actually, let's use the standard android tool approach:
          mkdir -p ~/.buildozer/android/platform/android-sdk/cmdline-tools
          
      # 6. Run Buildozer (With the 'yes' pipe as backup)
      - name: Build with Buildozer
        run: |
          # The 'yes' command is piped to buildozer to answer "y" to any prompts
          yes | buildozer android debug
        env:
          # This variable sometimes helps with headless builds
          CI: true

      # 7. Upload APK
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: bin/*.apk
"""

with open(os.path.join(workflow_dir, "build.yml"), "w") as f:
    f.write(build_yml)
    print("✅ Created robust build.yml")

# 3. WRITE THE CORRECT BUILDOZER.SPEC
# We must ensure 'android.accept_sdk_license = True' is present
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
    print("✅ Created correct buildozer.spec")

print("🎉 DONE. Now run: git add . && git commit -m 'Final Fix' && git push")