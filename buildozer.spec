[app]

# Uygulama adı (telefonda görünen)
title = Roboto'yu Kurtar

# Paket adı ve alan adı → birleşince benzersiz uygulama kimliği (com.aslan.robotoyukurtar)
package.name = robotoyukurtar
package.domain = com.aslan

# Kaynak klasörü ve dahil edilecek dosya türleri
source.dir = .
source.include_exts = py,png,json
# APK'yı şişiren klasörleri hariç tut (PyInstaller çıktıları, önbellek vb.)
source.exclude_dirs = build,dist,__pycache__,.git,.buildozer
source.exclude_patterns = RobotoOyun.spec,*.exe,_*.py

# Sürüm
version = 1.0

# Gereksinimler — Python + Pygame (SDL2). En kritik/kırılgan satır burası.
requirements = python3,pygame

# Yatay kilit + tam ekran (oyun yatay tasarlandı)
orientation = landscape
fullscreen = 1

# Uygulama ikonu
icon.filename = %(source.dir)s/icon.png

# Açılış (presplash) arka plan rengi — oyunun koyu teması
android.presplash_color = #0f1428

# Android API seviyeleri (Play Store 2024+ için hedef 34; min 21 = Android 5.0)
android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

# İnternet gerektirmeyen, çevrimdışı oyun → ekstra izin yok
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 1
