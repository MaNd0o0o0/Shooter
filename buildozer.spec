[app]
title = Mando Game
package.name = mando
package.domain = org.mando
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,mp3,wav
version = 1.0.0
requirements = python3,kivy==2.3.0
orientation = landscape
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1