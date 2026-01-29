import os

# 1. SETUP FOLDERS
workflow_dir = os.path.join(".github", "workflows")
os.makedirs(workflow_dir, exist_ok=True)

# 2. WRITE A "DOCKERIZED" BUILD.YML
# This uses the official 'kivy/buildozer' image. It CANNOT miss libraries because they are baked in.
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

      # We run the build INSIDE the official container
      # This bypasses all 'missing library' errors on the host
      - name: Build with Buildozer Docker
        uses: docker://kivy/buildozer:latest
        with:
          args: buildozer android debug
        env:
          # This fixes permission issues by telling Docker to run as the current user
          USER_ID: 1001
          GROUP_ID: 1001

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: bin/*.apk
"""

with open(os.path.join(workflow_dir, "build.yml"), "w") as f:
    f.write(build_yml)
    print("✅ Created Docker-based build.yml")

# 3. ENSURE BUILDOZER.SPEC IS COMPATIBLE
# We need to make sure the spec file doesn't have weird paths
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
# Docker image handles these versions automatically
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
"""

with open("buildozer.spec", "w") as f:
    f.write(spec_content)
    print("✅ Reset buildozer.spec to standard config.")

print("🎉 DONE. Now run: git add . && git commit -m 'Switch to Docker' && git push")