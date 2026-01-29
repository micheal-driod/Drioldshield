%%writefile buildozer.spec
[app]
title = DroidShield Pro
package.name = droidshieldpro
package.domain = org.cyber
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 8.0
requirements = python3,kivy==2.2.1,android,pyjnius,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# --- STABLE COMPATIBILITY CONFIG ---
# These versions are known to work with the default tools
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
# -----------------------------------

[buildozer]
log_level = 2
warn_on_root = 1