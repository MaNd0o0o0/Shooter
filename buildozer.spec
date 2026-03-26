[app]
# اسم التطبيق اللي هيظهر للمستخدم
title = Space Shooter

# اسم الباكدج (Package Name)
package.name = spaceshooter

# الدومين الخاص بك (بيخلي الـ package فريد)
package.domain = org.mando

# مجلد الكود الأساسي
source.dir = .

# الامتدادات اللي هيتم تضمينها في البناء
source.include_exts = py,png,jpg,kv,atlas,json,ttf,mp3,wav

# رقم الإصدار
version = 1.0.0

# المكتبات المطلوبة
requirements = python3,kivy

# اتجاه الشاشة
orientation = landscape

# وضع ملء الشاشة (0 = لأ، 1 = نعم)
fullscreen = 0

# الصلاحيات المطلوبة
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# إعدادات أندرويد
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# اسم المطور
author = mando

[buildozer]
# مستوى اللوج
log_level = 2

# تحذير لو شغال كـ root
warn_on_root = 1