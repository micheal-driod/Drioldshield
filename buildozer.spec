[app]
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
