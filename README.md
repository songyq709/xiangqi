# 中国象棋 · 智算单机版（安卓版）

桌面版（Windows exe）的安卓移植版。棋局规则、AI、残局库、界面全部复用同一份代码
（`xiangqi.py` 就是桌面版主程序 v2.3），只加了一层平台适配：

- 逻辑画布固定 572×838，按短边等比缩放到手机屏幕，**居中留黑边，不拉伸变形**
- 中文字体自动找安卓系统自带的 Noto Sans CJK / DroidSansFallback
- 设置、残局库、棋谱写到应用私有目录（不用存储权限，卸载即清）
- 手指点选即可走子；物理返回键 = 关窗口（浮层先关 → 对局回主页 → 主页才退出）
- 不需要任何 Android 权限：不联网、不读短信、不碰相册

## 目录

| 文件 | 作用 |
| --- | --- |
| `main.py` | 安卓启动入口，负责记启动日志（`启动日志.txt` 在应用私有目录） |
| `xiangqi.py` | 主程序 v2.3（与桌面版同一份，未改逻辑） |
| `buildozer.spec` | 打包配置：包名 `org.songyq.xiangqi`、竖屏全屏、arm64 |
| `icon.png` | 512×512 应用图标 |
| `曲/` | 背景音乐（回家 / 来日方长 / 钢琴曲 梁祝），进 APK 随包发布 |
| `.github/workflows/build-apk.yml` | GitHub Actions 云构建脚本 |

## 云构建（不需要在本机装任何东西）

1. 把这个目录的内容推到一个 GitHub 仓库（`main` 分支）。
2. 打开仓库的 **Actions** 页 → 左侧「打包安卓 APK」→ 右侧 **Run workflow**。
3. 首次构建约 40–70 分钟（要下载 Android SDK / NDK 并编译 CPython），之后有缓存会快很多。
4. 构建完成后，在本次运行页面底部 **Artifacts** 下载 `中国象棋-apk.zip`，里面就是
   `bin/中国象棋-2.3-arm64-v8a-debug.apk`。
5. 传到手机上安装（首次需在系统里允许「安装未知来源应用」）。

打 tag 时（`git tag v2.3 && git push --tags`）会把 APK 附到 Release，
手机浏览器点链接就能直接下载安装。

## 本机构建（Linux / macOS / WSL 均可，Windows 原生不行）

```bash
pip install buildozer cython==0.29.36 virtualenv
sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool \
    pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev
buildozer -v android debug
```

## 已知限制

- debug 包的签名是调试密钥，装到手机要允许「未知来源」；上架应用商店需另配 release 签名。
- 名字输入（残局改名 / 粘贴棋谱）依赖软键盘，安卓上 pygame 不弹输入法，这部分功能在手机上用不了；
  走子、残局、设置、音乐都正常。
- `曲/` 里的 mp3 能否播放取决于打包时的 SDL_mixer 是否编译了 mp3 支持；不支持时自动回落到内置合成古曲。
