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

# Gereksinimler — Python + Pygame (SDL2).
# Python 3.10.12'ye sabit: 3.11+ ile Pygame "longintrepr.h" hatası veriyor.
# host ve hedef python aynı sürüm olmalı → hostpython3 de sabitlendi.
requirements = hostpython3==3.10.12,python3==3.10.12,pygame

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
# NDK'yı Pygame/SDL2 reçeteleriyle uyumlu sürüme sabitle (r28 çok yeni, derlemeyi bozuyor)
android.ndk = 25b
# Tek mimari: tüm modern telefonlar arm64; derleme daha hızlı ve sağlam
android.archs = arm64-v8a

# İnternet gerektirmeyen, çevrimdışı oyun → ekstra izin yok
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 1
