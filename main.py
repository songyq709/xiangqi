# -*- coding: utf-8 -*-
"""安卓启动入口 —— python-for-android 从这个文件进。

真正的棋局逻辑全部在同目录的 xiangqi.py 里（就是桌面版主程序，一字未改地复用），
这里只负责：把启动过程和异常记进日志，免得手机上黑屏时无从下手。
"""
import os
import sys
import traceback

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def _log(text):
    """写到应用私有目录的 启动日志.txt（卸载 App 时一起清掉）"""
    try:
        d = os.environ.get("ANDROID_PRIVATE") or APP_DIR
        with open(os.path.join(d, "启动日志.txt"), "a", encoding="utf-8") as fp:
            fp.write(text.rstrip() + "\n")
    except Exception:
        pass


def _env_summary():
    lines = ["平台 %s / Python %s" % (sys.platform, sys.version.split()[0])]
    for key in ("ANDROID_ARGUMENT", "ANDROID_PRIVATE", "ANDROID_APP_PATH",
                "P4A_BOOTSTRAP", "ANDROID_APP"):
        val = os.environ.get(key)
        if val:
            lines.append("%s = %s" % (key, val))
    return "\n".join(lines)


if __name__ == "__main__":
    _log("=" * 40)
    _log("启动 " + _env_summary())
    try:
        import pygame
        _log("pygame %s / SDL %s" % (pygame.version.ver, pygame.version.SDL))
    except Exception:
        _log("pygame 没装上：\n" + traceback.format_exc())
    try:
        import xiangqi
        _log("载入 xiangqi v%s" % getattr(xiangqi, "VERSION", "?"))
        xiangqi.main()
        _log("正常退出")
    except SystemExit:
        _log("SystemExit")
        raise
    except BaseException:
        _log("崩溃：\n" + traceback.format_exc())
        raise
