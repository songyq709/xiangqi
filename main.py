# -*- coding: utf-8 -*-
"""安卓启动入口 —— python-for-android 从这个文件进。

真正的棋局逻辑全部在同目录的 xiangqi.py 里（桌面版主程序原样复用）。
本文件只做两件事：
  1) 记一份启动日志（应用私有目录 + 外部可见的 Android/data 目录），
     闪退时能把停在哪个阶段、什么报错留下来；
  2) 真出事时开红底窗口把调用栈显示出来，不至于只看到黑屏一闪。
"""
import os
import sys
import time
import traceback

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PKG = "org.songyq.xiangqi"

_EXT = os.environ.get("EXTERNAL_STORAGE")

_LOG_DIRS = [
    "/storage/emulated/0/Android/data/%s/files" % PKG,
    (os.path.join(_EXT, "Android/data", PKG, "files") if _EXT else None),
    os.environ.get("ANDROID_PRIVATE"),
    APP_DIR,
]


def _log(text):
    for d in _LOG_DIRS:
        if not d:
            continue
        try:
            if not os.path.isdir(d):
                os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "启动日志.txt"), "a", encoding="utf-8") as fp:
                fp.write(text.rstrip() + "\n")
            return True
        except Exception:
            continue
    return False


def _env_summary():
    lines = ["平台 %s / Python %s" % (sys.platform, sys.version.split()[0])]
    for key in ("ANDROID_ARGUMENT", "ANDROID_PRIVATE", "ANDROID_APP_PATH",
                "P4A_BOOTSTRAP", "ANDROID_APP", "EXTERNAL_STORAGE"):
        val = os.environ.get(key)
        if val:
            lines.append("%s = %s" % (key, val))
    try:
        lines.append("程序目录 = %s" % APP_DIR)
        lines.append("目录内容 = %s" % ", ".join(sorted(os.listdir(APP_DIR))[:24]))
    except Exception as exc:
        lines.append("列目录失败：%s" % exc)
    return "\n".join(lines)


def _paint(screen, rgb, title, body):
    """在给定窗口上画整屏文字（用 pygame 自带字体，不依赖系统中文字体）"""
    import pygame
    w, h = screen.get_size()
    screen.fill(rgb)
    size = max(14, min(30, w // 40))
    try:
        font = pygame.font.Font(None, size)
    except Exception:
        font = None
    lines = []
    for raw in (title + "\n" + body).splitlines():
        if font is None:
            lines.append(raw)
            continue
        cur = ""
        for ch in raw:
            if font.size(cur + ch)[0] > w - 24:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
    y = 10
    for line in lines:
        if y > h - size:
            break
        if font is not None:
            screen.blit(font.render(line, True, (255, 255, 255)), (12, y))
        y += size + 5
    pygame.display.flip()


def _wait(seconds, stop_on_touch=False):
    import pygame
    end = time.time() + seconds
    while time.time() < end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if stop_on_touch and event.type in (pygame.MOUSEBUTTONDOWN,
                                                pygame.KEYDOWN, pygame.FINGERDOWN):
                return
        time.sleep(0.1)


def main():
    _log("=" * 46)
    _log(_env_summary())

    stage = "import pygame"
    try:
        import pygame
        _log("pygame %s / SDL %s" % (pygame.version.ver, pygame.version.SDL))

        # 屏幕探针：先量一次真实分辨率与 DPI，决定是否启用「手机放大界面」。
        # 逻辑画布固定 572 宽，手机 1080 宽时整体放大，但顶栏/底栏按钮仍偏小，
        # 所以短边 ≥720 物理像素就切到 xs 版大按钮布局（见 xiangqi.set_ui_mode）。
        stage = "屏幕探针"
        try:
            pygame.display.init()
            try:
                w, h = pygame.display.get_desktop_sizes()[0]
            except Exception:
                info = pygame.display.Info()
                w, h = info.current_w, info.current_h
            dpi = None
            try:
                dpi = pygame.display.get_dpi()
            except Exception:
                pass
            big = (min(w, h) >= 720) or ("ANDROID_ARGUMENT" in os.environ)
            os.environ["XQ_BIG_UI"] = "1" if big else "0"
            _log("屏幕探针：%dx%d，DPI %s → %s（XQ_BIG_UI=%s）"
                 % (w, h, dpi, "手机放大界面" if big else "桌面界面",
                    os.environ["XQ_BIG_UI"]))
        except Exception as exc:
            _log("屏幕探针失败：%s（交由主程序按环境判断）" % exc)

        stage = "import xiangqi"
        import xiangqi
        _log("载入 xiangqi v%s" % getattr(xiangqi, "VERSION", "?"))

        stage = "xiangqi.main()"
        xiangqi.main()
        _log("正常退出")
    except SystemExit:
        _log("SystemExit（第 %s 阶段）" % stage)
        raise
    except BaseException:
        tb = traceback.format_exc()
        _log("崩溃（第 %s 阶段）：\n%s" % (stage, tb))
        try:
            import pygame
            pygame.init()
            try:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            except pygame.error:
                screen = pygame.display.set_mode((0, 0))
            _paint(screen, (120, 0, 0), "启动失败：%s" % stage,
                   "点一下屏幕返回。\n" + tb)
            _wait(20, stop_on_touch=True)
        except Exception:
            _log("错误屏也没能显示：\n" + traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
