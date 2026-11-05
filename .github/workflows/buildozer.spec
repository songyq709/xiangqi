[app]

# 应用名（手机桌面显示）
title = 中国象棋

# 包名：org.songyq.xiangqi
package.name = xiangqi
package.domain = org.songyq

# 源码目录：本文件所在目录（main.py + xiangqi.py + 素材）
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,ttf,otf,wav,ogg,mp3
source.exclude_patterns = icon_src.png,启动日志.txt,*.pyc
source.exclude_dirs = bin,__pycache__,.github

version = 2.8

# pygame 走 python-for-android 的 sdl2 引导层
# 必须钉版本：p4a 的 pygame recipe 默认拉 pygame 2.1.0，它 include 的
# longintrepr.h 在 Python 3.11 之后已移入 Include/cpython/，在 3.14 里更是没了。
# 不钉 python 版本，构建环境会用最新 3.14，pygame 的 C 扩展必然编译失败。
requirements = python3==3.11.5,pygame==2.5.2,cython==3.0.11
p4a.bootstrap = sdl2
# p4a 固定走 master 分支（该分支已修复 3.12+ 的 python3 recipe）
p4a.branch = 2024.01.21

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png

# 竖屏、吃满全屏（游戏内部逻辑画布 572×838，会等比缩放居中留黑边）
orientation = portrait
fullscreen = 1

# 不需要任何权限：不联网、不读短信、不碰相册（保持默认空权限）
# android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.ndk_api = 21
# 钉 NDK 版本：不写这一行，buildozer 会挑最新 NDK，与 p4a 的 recipe 不匹配
android.ndk = 25b
android.archs = arm64-v8a
android.numeric_version = 20800
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1
