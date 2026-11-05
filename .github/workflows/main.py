# -*- coding: utf-8 -*-
"""安卓启动入口 —— python-for-android 从这个文件进。

真正的棋局逻辑全部在同目录的 xiangqi.py 里（桌面版主程序原样复用）。

这个入口额外做两件事，专门应付"图标一闪就退出、屏幕上什么都没有"的情况：
  1) 把启动过程分阶段记进日志，崩溃时写清楚停在哪一步；
  2) 崩溃时**直接在屏幕上显示错误文字**，不用连电脑抓 logcat。
"""
import os
import sys
import traceback

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 日志落盘位置：先试应用私有目录，再试几个外部可见目录（能写哪个算哪个）
_LOG_DIRS = [
    os.environ.get("ANDROID_PRIVATE"),
    APP_DIR,
    "/storage/emulated/0/Download",
    "/sdcard/Download",
    "/storage/emulated/0",
]


def _log(text):
    for d in _LOG_DIRS:
        if not d:
            continue
        try:
            with open(os.path.join(d, "启动日志.txt"), "a", encoding="utf-8") as fp:
                fp.write(text.rstrip() + "\n")
            return True
        except Exception:
            continue
    return False


def _env_summary():
    lines = ["平台 %s / Python %s" % (sys.platform, sys.version.split()[0])]
    for key in ("ANDROID_ARGUMENT", "ANDROID_PRIVATE", "ANDROID_APP_PATH",
                "P4A_BOOTSTRAP", "ANDROID_APP", "SDL_VIDEODRIVER"):
        val = os.environ.get(key)
        if val:
            lines.append("%s = %s" % (key, val))
    try:
        lines.append("程序目录 = %s" % APP_DIR)
        lines.append("目录内容 = %s" % ", ".join(sorted(os.listdir(APP_DIR))[:20]))
    except Exception as exc:
        lines.append("列目录失败：%s" % exc)
    return "\n".join(lines)


def _show_error(title, body):
    """把错误直接画在屏幕上，点一下屏幕或等 90 秒再退出"""
    try:
        import time
        import pygame
        if not pygame.display.get_init():
            pygame.display.init()
        if not pygame.font.get_init():
            pygame.font.init()
        try:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except pygame.error:
            screen = pygame.display.set_mode((0, 0))
        w, h = screen.get_size()
        if w < 200 or h < 200:
            w, h = 1080, 1920
            screen = pygame.display.set_mode((w, h))
        size = max(12, min(26, w // 44))
        try:
            font = pygame.font.Font(None, size)   # pygame 自带字体，不依赖系统中文字体
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

        screen.fill((16, 16, 18))
        y = 8
        for line in lines:
            if y > h - size - 4:
                break
            if font is not None:
                screen.blit(font.render(line, True, (240, 240, 240)), (10, y))
            y += size + 4
        pygame.display.flip()

        deadline = time.time() + 90
        while time.time() < deadline:
            for event in pygame.event.get():
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN,
                                  pygame.FINGERDOWN, pygame.QUIT):
                    return
            time.sleep(0.1)
    except Exception:
        pass


if __name__ == "__main__":
    _log("=" * 46)
    _log(_env_summary())

    stage = "import pygame"
    try:
        import pygame
        _log("pygame %s / SDL %s" % (pygame.version.ver, pygame.version.SDL))

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
        _show_error("启动失败：%s" % stage, tb)
        raise
