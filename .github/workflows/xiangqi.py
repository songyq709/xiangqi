# -*- coding: utf-8 -*-
# pyright: reportMissingImports=false
"""中国象棋 · 智算单机版（Pygame 版）

v2.5 手机专版改动：
  1) 界面按屏幕自动分两套：启动探针量一次真实分辨率，短边 ≥720 物理像素就走
     「手机放大版」——顶栏按钮 32 高、底栏 36 高、主页按钮加高加大，字号提一档；
     桌面窗口仍是原来的尺寸。判断结果也可以通过 XQ_BIG_UI=0/1 强制指定。
  2) 底栏重排：音乐开关挪到顶栏、紧挨音效；底栏九格改为
     悔棋 / 复盘 / 提示 / 存局 / 认输 / 提和 / 棋谱 / 重开 / 返回。
     「返回」等同 Esc，摆棋与残局库本来就有自己的返回口，不再重复放。
  3) 主页新增「退出」：手机上直接结束 Activity 回桌面，不必再用上滑手势；
     桌面版点它等同关窗口。
  4) 「提示」改为后台线程算：深度由 3 层提到最多 8 层、时间 2 秒，
     算的时候界面照常 60 帧，不再假死；残局里给出的着法明显更靠谱。
  5) 上滑切后台再回来偶发黑屏：加了 Surface 尺寸复核（每半秒一次 + 前台事件触发重建），
     并关掉 SDL 的「失焦最小化」；同时把主线程里所有长任务都移出，避免 ANR 黑屏。
  6) 残局库新增 100 局（经典 70 + 江湖 30），全部经过规则校验与「两步杀」强制验证；
     升级安装时按名字自动并入老库，不用清数据。

v2.4 改动：
  1) 对局中按 Esc 不再悄悄存「半局」，直接回主页，并提示「这局没存，想保下来
     请在局中点存局」。整个「暂存半局」功能撤掉，旧设置里攒下的暂存条目一并清空。
  2) 导入浮层只留「粘贴文本 / 选文件导入」两块，面板固定高度居中；
     以前那半块看不见的暂存列表不再占地方。
  3) 说明浮层每页记住行数，页面没写满且后面还有页时，底部加一行绿字提示
     「↓ 后面还有 N 页」，不会再误以为已经看完了。
  4) 翻页按钮跟着状态变：还能翻的是绿底白字，到头的是灰底灰字。

v2.2 改动：
  1) 主页背景换成象棋：原来是《重屏会棋图》（画的其实是围棋），现在改为程序自绘的
     斜放象棋盘 + 几枚红子 + 「楚河·汉界」，墨线按主题取色，深浅两套皮肤都合身；
     想换成自己的画，把图片命名成 主页背景.jpg 放程序目录即可（会盖掉自绘版）。
  2) 说明浮层鼠标可操作：滚轮上下翻页，点「« 上一页 / 下一页 »」，点正文左半往回、
     右半往前，鼠标停在按钮上会亮起来；键盘 ← → / PgUp / PgDn 照旧。
  3) 电脑战力提升（同一时间预算下明显更硬）：
     · 子力价值改为象棋惯例（士象由 20 提到 200，不再为救一个兵送士象），
       位置分改用整张位置分表：兵过河、马炮居中、车占要道、士象守家各有分值；
     · 着法排序加入「置换表着法 → 吃子按 MVV-LVA → 杀手着法 → 历史启发」，
       同样深度下节点数少了一个数量级（实测 4 层：11.9 秒 → 2.0 秒）；
     · 将军延伸：临近叶子被将军多看一层，不再「将完才发现自己亏子」；
     · 杀棋分值随层数衰减，优先走快杀、被将死时尽量拖；
     · 置换表在同一步内不再清空、跨层复用；「困难 / 大师」的时间预算真正用满
       （大师最多 8 层，实际层数由 5.5 秒决定）。
  4) 残局库补齐：11-01 备份里少的 7 条（第094局 负笈追师 + 6 条自定残局）已并回，共 115 条。

v2.1 改动（安卓版 v2.1，桌面端行为不变）：
  1) 新增安卓（python-for-android / buildozer）适配层，桌面 exe 仍按原样运行：
     可写目录改用应用私有目录（ANDROID_PRIVATE），只读资源仍从 __file__ 旁边取。
  2) 显示改为「等比缩放 + 居中留边」：以前按窗口宽高直接拉伸，手机竖屏（1080×1920）
     与逻辑画布（572×838）比例不同会被压扁；现在按短边等比缩放、四周留黑边，坐标反算同步改。
  3) 中文字体自动找安卓系统字体（Noto Sans CJK / DroidSansFallback 等），不再只认
     Windows 字体目录；找不到再退回 SysFont。
  4) 安卓物理返回键等同窗口关闭：浮层先关、对局先回主页、主页才退出。
  5) 触屏：显式打开 SDL 的触摸转鼠标模拟，手指点选即可走子。

v2.0 改动（修一个真 bug）：
  1) 长将判定改为「按整个重复循环看谁在将军」：以前只看「这一着是否将军」，于是对手连将、
     你被迫来回走帅时，若你的某一步恰好也形成将军（抽将），长将会记到你头上；反过来
     对手一直将军却因为不构成「你这一着将军」而判不出来。现在记录每着的局面与将军状态
     （pos_log），同一局面第 3 次出现时，回看这一轮循环：谁每着都在将军谁判负，
     被迫躲闪的一方不受罚。
  2) 三次重复但双方都不在将军（确实无别的着法可走）→ 判和，不再让双方在原地反复打转；
     原来只在走子前拦一下，被迫重复时既不判和也不判负，会一直循环。
  3) 说明文字同步更新。

v1.9 改动：
  1) 单步计时圆表放大：半径按面板内框算（黑方 22、红方 26），比边框小一圈，
     纵向在面板里居中；横向仍与将帅那条竖线对齐，所以表就压在帅/将的正上、正下方。
  2) 剩 10 秒内不再只是变红，改为**红黑交替闪烁**（约 0.8 秒一闪），
     秒数、表圈、剩余弧一起闪，远看也看得见「要超时了」。

v1.8 改动：
  1) 「该谁走」不再用面板上的箭头带，改为**单步计时圆表**：圆表挂在轮走一方的将/帅旁边
     （与将帅同一竖线、贴在棋盘下沿 / 上沿），12 个刻度像座钟，指针一圈走完这一手的限时，
     圈心写这一手还剩几秒；不走的一方不画表。圆表旁一句话写「该你走」/「思考中…」。
  2) 新增「单步限时」：设置面板可选 不限 / 15 / 30 / 60 秒，对战顶部设置栏另有一个
     「单步」按钮，对局中直接点即可在四档之间轮换，不必回主页；超时判负（不限时则纯计时）。
  3) 说明浮层改为**多页显示**：上一页 / 下一页按钮 + 页码，← → 键翻页，面板居中；
     文字量再涨也不会挤成一团或被底边裁掉。
  4) 主页落款「制作人」向左提一格（26px），不再贴着右侧边框。

v1.7 改动：
  1) 长将判负真正生效：同一局面第 3 次出现，且这几着一直在将军 —— 直接判长将方负；
     以前「将军」这一类重复会被「不得重复走子」挡回去，长将永远判不出来，现在放行并判负；
     电脑自己则会避开这类着法，不主动长将；
  2) 设置面板里，曲 目录里的真实音频与内置合成曲在样式上分开了：
     有文件的按钮描绿边、右上角实心点，合成的画灰色空心点，旁边一行图例说明。

v1.6 改动：
  1) 背景曲库改为「自动扫描 曲 目录」：往里放 mp3 / ogg / wav，设置面板立刻多一个曲目，
     放进去即生效、删掉即消失，不必再改代码；内置四首合成古曲仍在，作为没有文件时的兜底；
  2) 曲目按钮改为每行 5 个、最多 10 个，面板底部提示当前 曲 目录里有几首、哪些是内置合成；
  3) 曲名过长自动截断，不再顶出按钮。

v1.5 改动：
  1) 程序更名为「中国象棋-智算单机版-版本号」；exe 名称自动跟随主程序名；
  2) 缺少 pygame 时不再直接抛一堆红字：弹出中文提示，告诉你去装包或用 exe；
     同时在文件首行关掉编辑器（Pylance / Pyright）的「无法解析导入 pygame」告警；
  3) 残局库的操作提示（已改名 / 已收藏 / 已删除…）只在当前库视图里显示，
     切分类、改搜索词、翻页、关掉浮层都会自动清掉，不再带到别的菜单；
  4) 对战新增「轮走指示」：上下两块面板各有一条计时箭头带，轮到哪方哪条就亮，
     箭头左右巡游，面板里同步写「该你走」/「思考中…」；
  5) 深色「墨玉」主题下，残局库 / 设置 / 说明 / 导入 / 命名浮层一并换成深色配色；
  6) AI 思考改到后台线程：算棋时窗口不再卡死，箭头与计时照常动；
  7) 音效与背景曲支持外置替换：往 音效 / 曲 目录放同名 wav / ogg / mp3 即生效；
  8) 打包带程序图标；说明文字与对局提示换行时不再把标点挤到行首。

v1.4 改动：
  1) 残局库条目可重命名：每行行尾新增「改」按钮，改名时可同时改「先行方」；
  2) 库行新增两列：出处（适情雅趣 / 经典排局 …）与存盘日期，子数/通关/黑先状态另列显示；
  3) 「已通关」按实际胜方判定并记录：条目自带先行方（红先 / 黑先），
     载入黑先排局时人类执黑、电脑执红，赢棋照样记通关，行内绿灯不变；
  4) 暂存半局只在走过 2 手以上才记，空局面与一手就退的不再堆进暂存列表（旧垃圾会清掉）。

v1.3 改动：
  1) 重复走子改温和版：同一局面第 3 次出现才拦（前两次照常走），提示里写明次数；
  2) 导入支持整份棋谱：粘贴本程序导出的棋谱全文，自动解析起始局面并逐手回放，
     可直接续下、可复盘全谱；普通式与叠子式记谱（炮八平五 / 前炮进1）都能认；
  3) 导入浮层新增「选文件」：从 棋谱 目录或任意位置选 .txt / .json / .fen；
     输入框容量 200 → 4000 字符，长棋谱不再被截断；
  4) 导入浮层最多列 4 条暂存（其余提示「另有 N 条」），面板高度随内容收放；
  5) AI 搜索时定期处理窗口消息，大师难度思考数秒也不会被系统判成「未响应」。

v1.2 改动：
  1) 三次重复局面不再判和：重复走子会被拦下并提示换着法，电脑也避开重复路线；
  2) 残局库一屏 20 行、尾部同样 20 行，↑↓ 一行一行滚动，PgUp/PgDn 整屏；
  3) 残局库每行有行号，行尾 ★ 收藏（更醒目），已通关显示绿色「已通关」；
  4) 对战 / 残局底部新增「存局」，把当前局面存进残局库（分类：自定残局）；
  5) 存盘一律写入分类，解决「全部里有、分项里找不到」的问题；
  6) 对局中可随手开关背景音乐（底部「音乐」按钮或 M 键），换曲不再强制打开音乐；
  7) 暂存半局列表加了行号，快捷键补 L（残局库）/ M（音乐）。

v1.1 改动：
  1) 窗口自适应：按屏幕可用高度等比缩放（1376×768 之类的小屏也能完整显示）；
  2) 走子提示：选中棋子后把可落点画成绿点、可吃子画成红圈；
  3) 将军 / 胜负提示：被将军的将帅描红并闪“将军”，终局在棋盘中央弹结果牌；
  4) 规则补全：长将判负（连续将军 6 步）、三次重复局面判和、60 回合无吃子判和；
  5) 认输 / 提和按钮（提和由电脑按形势决定）、悔棋次数限制（设置里可选）；
  6) AI 增强：置换表 + 静态搜索（吃子延伸）+ 迭代加深，同等时间算得更深；
  7) 残局库：搜索框、收藏筛选、通关标记、导出 / 导入整库、写库自动留 .bak；
  8) 对局“提示”按钮：电脑给出推荐一手并标在棋盘上；
  9) 设置新增：音效音量、音乐音量滑块，悔棋限制，棋盘配色（原木 / 墨玉）；
 10) 打包支持：资源与数据路径兼容 PyInstaller 单文件 exe。

快捷键：
  R      重开当前局面
  1      切换残局示例
  2      切换标准开局
  E      进入 / 退出摆棋模式
  S      音效开 / 关
  H      提示一手
  G      导出棋谱
  U      悔棋
  P      复盘（方向键 / 空格步进与自动播放，ESC 退出）
  ESC    对战中返回主页（不自动暂存，保局请在局中点「存局」）；主页关闭浮层或退出程序
"""

import json
import math
import os
import random
import re
import shutil
import sys
import threading
import time
from array import array

try:
    import pygame
except ImportError:                    # 没装 pygame / 编辑器解释器选错时的兜底说明
    _TIP = (
        "没有找到 pygame，游戏无法启动。\n\n"
        "① 最省事：直接双击 dist 目录里的「中国象棋-智算单机版-….exe」，它已内置 pygame。\n"
        "② 跑源码：用装了 pygame 的 Python 启动，例如\n"
        "      %LocalAppData%\\Programs\\Python\\Python313\\python.exe 中国象棋-智算单机版-v1.5.py\n"
        "③ 手动装包：命令行执行  python -m pip install pygame\n\n"
        "提示：编辑器里那句「无法解析导入 pygame」只是静态检查的提醒——\n"
        "它用的解释器里没有这个包，并不影响程序运行；本文件首行已关掉这条告警。"
    )
    print(_TIP)
    try:
        import tkinter as _tk
        from tkinter import messagebox as _mb
        _root = _tk.Tk()
        _root.withdraw()
        _mb.showerror("中国象棋 · 缺少 pygame", _TIP)
        _root.destroy()
    except Exception:
        pass
    raise SystemExit(1)

# ---------------------------- 路径（兼容 exe 打包 / 安卓） ----------------------------
def is_android():
    """是不是跑在安卓上（python-for-android 会注入 ANDROID_ARGUMENT / ANDROID_PRIVATE）"""
    for key in ("ANDROID_ARGUMENT", "ANDROID_PRIVATE", "P4A_BOOTSTRAP"):
        if key in os.environ:
            return True
    return os.path.exists("/system/build.prop") and sys.platform.startswith("linux")


IS_ANDROID = is_android()


def _android_writable_dir():
    """安卓上唯一可写的地方：应用私有目录（卸载即清）"""
    for key in ("ANDROID_PRIVATE", "ANDROID_APP_PATH"):
        d = os.environ.get(key)
        if d:
            try:
                os.makedirs(d, exist_ok=True)
            except OSError:
                pass
            return d
    try:
        from android.storage import app_storage_path    # type: ignore
        return app_storage_path()
    except Exception:
        return os.path.expanduser("~")


def _base_dir():
    """数据目录（设置 / 残局库 / 棋谱，必须可写）
    Windows 脚本：脚本所在目录；exe：exe 所在目录；安卓：应用私有目录"""
    if IS_ANDROID:
        return _android_writable_dir()
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _res_dir():
    """资源目录（图标 / 音效 / 曲 / 内置残局，只读）
    exe：解包临时目录；安卓：.py 与资源一起打进 site-packages，取 __file__ 旁边"""
    if IS_ANDROID:
        return os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", _base_dir())
    return _base_dir()


def _asset(name):
    """资源文件：先找打包解包目录，再找程序目录"""
    p = os.path.join(_res_dir(), name)
    if os.path.exists(p):
        return p
    return os.path.join(_base_dir(), name)


_BASE_DIR = _base_dir()


# ---------------------------- 常量 ----------------------------
BOARD_COLS = 9
BOARD_ROWS = 10
CELL = 60
MARGIN = 46

CONTROL_H = 40          # 顶部设置栏（难度 / 摆棋 / 残局库 / 音效）
PANEL_TOP = 56          # 黑方计时面板
PANEL_BOTTOM = 140      # 红方计时面板 + 提示文字 / 摆棋面板 + 底部按钮栏

BOARD_PX_W = MARGIN * 2 + CELL * (BOARD_COLS - 1)      # 572
BOARD_PX_H = MARGIN * 2 + CELL * (BOARD_ROWS - 1)      # 632
SCREEN_W = BOARD_PX_W
BOARD_ORIGIN_Y = CONTROL_H + PANEL_TOP                 # 棋盘区域起始 y
SCREEN_H = CONTROL_H + PANEL_TOP + BOARD_PX_H + PANEL_BOTTOM   # 838

# 摆棋面板（替代底部计时面板显示）
EDIT_TOP = BOARD_ORIGIN_Y + BOARD_PX_H + 2
EDIT_BAR1_Y = EDIT_TOP + 4        # 红方全盘棋子行（黑方在其下 32px）
EDIT_BAR2_Y = EDIT_TOP + 68       # 操作按钮
EDIT_MSG_Y = EDIT_BAR2_Y + 34     # 编辑提示文字

# 计时设置（分钟，可用环境变量 CHESS_TIME_MIN 覆盖）
try:
    TIME_LIMIT = max(1, int(os.environ.get("CHESS_TIME_MIN", "10"))) * 60
except ValueError:
    TIME_LIMIT = 10 * 60

# 配色（默认原木；可在设置里切换「墨玉」深色主题）
RED = "r"
BLACK = "b"

THEMES = {
    "原木": {
        "bg": (241, 219, 182), "line": (92, 62, 32), "river": (150, 105, 60),
        "piece_face": (252, 240, 212), "piece_edge": (120, 92, 60),
        "piece_shadow": (196, 166, 126), "board_border": (120, 86, 52),
        "panel_bg": (233, 225, 210), "panel_line": (202, 192, 176),
        "panel_fill": (255, 252, 242), "panel_idle": (233, 227, 214),
        "text": (70, 60, 48), "label": (96, 76, 56), "btn_text": (92, 82, 68),
        "muted": (140, 128, 112), "accent_red": (178, 44, 44),
        "accent_black": (38, 38, 44),
    },
    "墨玉": {
        "bg": (54, 60, 62), "line": (176, 186, 182), "river": (152, 180, 176),
        "piece_face": (230, 228, 216), "piece_edge": (86, 100, 96),
        "piece_shadow": (28, 34, 36), "board_border": (146, 156, 152),
        "panel_bg": (70, 78, 80), "panel_line": (44, 50, 52),
        "panel_fill": (96, 106, 108), "panel_idle": (66, 74, 76),
        "text": (236, 230, 216), "label": (206, 212, 206), "btn_text": (228, 224, 210),
        "muted": (196, 192, 180), "accent_red": (240, 128, 114),
        "accent_black": (206, 214, 222),
    },
}
THEME_NAMES = ["原木", "墨玉"]
TH = dict(THEMES["原木"])
BG_COLOR = TH["bg"]
def fit_layout(win_w, win_h):
    """逻辑画布（572×838）在窗口里的等比放置方案：(draw_w, draw_h, off_x, off_y)。
    按短边贴合，长边居中留黑 —— 手机竖屏 1080×1920 时得到 1080×1583、上下各留 168 黑边，
    画面绝不拉伸变形；桌面窗口本来就是 1:1，返回 (572, 838, 0, 0)。"""
    win_w = max(1, int(win_w))
    win_h = max(1, int(win_h))
    fit = min(win_w / float(SCREEN_W), win_h / float(SCREEN_H))
    draw_w = max(1, int(round(SCREEN_W * fit)))
    draw_h = max(1, int(round(SCREEN_H * fit)))
    return draw_w, draw_h, (win_w - draw_w) // 2, (win_h - draw_h) // 2


def window_to_logical(pos, win_w, win_h):
    """窗口坐标 → 逻辑画布坐标：扣掉黑边偏移，并夹在画布范围内（点黑边不越界）"""
    if (win_w, win_h) == (SCREEN_W, SCREEN_H):
        return pos
    draw_w, draw_h, off_x, off_y = fit_layout(win_w, win_h)
    x = (pos[0] - off_x) * SCREEN_W / float(draw_w)
    y = (pos[1] - off_y) * SCREEN_H / float(draw_h)
    return (max(0.0, min(SCREEN_W - 1.0, x)),
            max(0.0, min(SCREEN_H - 1.0, y)))


BOARD_LINE = TH["line"]
RIVER_COLOR = TH["river"]
THEME_CURRENT = "原木"


def apply_theme(name):
    """切换棋盘配色：直接改模块级颜色变量，绘制函数即时生效。
    棋盘层与棋子是预渲染缓存的，换主题时一并作废，下次重画。"""
    global TH, BG_COLOR, BOARD_LINE, RIVER_COLOR, THEME_CURRENT
    THEME_CURRENT = name if name in THEMES else "原木"
    TH = dict(THEMES[THEME_CURRENT])
    BG_COLOR = TH["bg"]
    BOARD_LINE = TH["line"]
    RIVER_COLOR = TH["river"]
    for _name in ("_BOARD_LAYER", "_PIECE_CACHE", "_SHADOW_CACHE"):
        _cache = globals().get(_name)
        if _cache is not None:
            _cache.clear()


# 浮层（残局库 / 设置 / 说明 / 导入 / 命名）原本是浅色纸质风。
# 这里给出一张「浅色 → 墨玉」对照表，浮层代码里的颜色统一走 C(...)：
# 原木主题原样返回，墨玉主题自动换深色，一套代码两套皮肤。
_DARK_MAP = {
    (252, 249, 242): (44, 50, 52),      # 面板底
    (255, 255, 255): (60, 68, 70),      # 输入框 / 列表行
    (250, 246, 238): (68, 76, 78),      # 普通按钮
    (244, 240, 232): (64, 72, 74),      # 收藏按钮（未收藏）
    (240, 244, 236): (66, 78, 72),      # 「改」按钮
    (238, 248, 240): (52, 74, 62),      # 已通关行
    (238, 246, 240): (54, 76, 66),      # 先行=红 按钮
    (236, 236, 240): (58, 62, 70),      # 先行=黑 按钮
    (236, 232, 224): (56, 62, 64),      # 禁用按钮
    (232, 214, 208): (92, 62, 58),      # 关闭按钮
    (250, 238, 206): (92, 80, 48),      # 已收藏
    (214, 206, 194): (72, 80, 82),      # 滚动轨
    (214, 206, 192): (72, 80, 82),      # 音量轨
    (206, 196, 180): (86, 96, 94),      # 边框
    (204, 196, 182): (86, 96, 94),
    (196, 186, 170): (96, 106, 104),
    (192, 204, 186): (90, 110, 98),
    (176, 166, 150): (104, 114, 112),
    (176, 52, 48): (168, 58, 52),       # 危险按钮底色
    (168, 60, 54): (236, 150, 142),     # 关闭叉
    (176, 106, 24): (232, 168, 90),     # 「黑先」标记
    (96, 82, 66): (206, 200, 188),      # 设置里的小标签
    (198, 188, 172): (116, 126, 124),    # 面板未轮到时的描边
    (232, 244, 236): (52, 78, 66),      # 「音乐开」按钮
    (238, 234, 228): (60, 64, 62),      # 「音乐关」按钮
    (170, 164, 154): (120, 130, 128),   # 禁用按钮描边
    (150, 144, 132): (168, 176, 170),   # 禁用按钮文字
    (112, 98, 80): (200, 194, 182),     # 控制栏小标签
    (120, 176, 132): (86, 150, 110),    # 通关行描边
    (110, 176, 132): (86, 150, 110),
    (214, 168, 66): (206, 168, 86),     # ★ 已收藏描边
    (198, 142, 26): (226, 178, 70),     # ★ 已收藏
    (170, 162, 148): (150, 142, 128),   # ☆ 未收藏
    (140, 128, 112): (168, 176, 170),
    (146, 134, 118): (160, 168, 162),
    (132, 122, 106): (150, 158, 152),
    (128, 116, 100): (156, 164, 158),
    (150, 138, 122): (160, 168, 162),
    (150, 140, 126): (160, 168, 162),
    (120, 132, 122): (156, 166, 160),
    (120, 108, 92): (158, 166, 160),
    (168, 158, 142): (150, 158, 152),
    (176, 168, 154): (140, 148, 144),
    (170, 160, 146): (152, 160, 154),
    (92, 82, 68): (226, 220, 206),      # 按钮文字
    (86, 74, 60): (228, 222, 208),
    (78, 64, 50): (230, 224, 210),
    (70, 58, 46): (232, 226, 212),
    (60, 52, 42): (234, 228, 214),
    (60, 50, 40): (236, 230, 216),
    (58, 50, 40): (236, 230, 216),
    (60, 48, 36): (236, 230, 216),
    (48, 42, 34): (240, 234, 220),
    (70, 112, 82): (150, 210, 176),
    (30, 112, 66): (140, 210, 170),
    (64, 66, 78): (190, 196, 214),
    (24, 132, 76): (110, 205, 150),
    (34, 130, 84): (110, 205, 150),
    (46, 120, 78): (110, 200, 146),
    (34, 150, 96): (86, 190, 140),      # 主色：边框 / 选中态
    (255, 245, 235): (250, 240, 230),
}


def _auto_dark(color):
    """对照表里没有的颜色：亮底压暗、深字提亮，保证不会出现白底白字 / 深底深字"""
    r, g, b = color
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    if lum > 0.72:                     # 亮色底 → 深色面
        return tuple(int(v * 0.24) for v in color)
    if lum < 0.58:                     # 文字 / 深块 → 浅色字
        return tuple(min(255, int(152 + v * 0.46)) for v in color)
    return tuple(int(v * 0.90) for v in color)


def K(color):
    """原样返回：彩色按钮上的白字、滑块圆点这类不该跟着主题变色的颜色用它"""
    return color


def C(color):
    """浮层配色：原木主题原样返回；墨玉主题换成对应深色"""
    if THEME_CURRENT != "墨玉":
        return color
    hit = _DARK_MAP.get(tuple(color))
    return hit if hit is not None else _auto_dark(color)

KING = "k"
ADVISOR = "a"
ELEPHANT = "e"
HORSE = "h"
ROOK = "r"
CANNON = "c"
PAWN = "p"

CHINESE_PIECES = {
    (RED, KING): "帅",
    (RED, ADVISOR): "仕",
    (RED, ELEPHANT): "相",
    (RED, HORSE): "马",
    (RED, ROOK): "车",
    (RED, CANNON): "炮",
    (RED, PAWN): "兵",
    (BLACK, KING): "将",
    (BLACK, ADVISOR): "士",
    (BLACK, ELEPHANT): "象",
    (BLACK, HORSE): "马",
    (BLACK, ROOK): "车",
    (BLACK, CANNON): "炮",
    (BLACK, PAWN): "卒",
}

# 各兵种单方标准数量上限（用于摆棋实时核验：如炮最多 2 个）
PIECE_MAX = {
    KING: 1, ADVISOR: 2, ELEPHANT: 2, HORSE: 2,
    ROOK: 2, CANNON: 2, PAWN: 5,
}

# 字体路径兜底配置：安卓先找系统自带的中文字体，桌面再落到 Windows 字体
ANDROID_FONT_PATHS = [
    "/system/fonts/NotoSansCJK-Regular.ttc",      # 主流安卓自带（思源黑体全集）
    "/system/fonts/NotoSansCJKsc-Regular.otf",
    "/system/fonts/NotoSansSC-Regular.otf",
    "/system/fonts/SourceHanSansCN-Regular.otf",
    "/system/fonts/DroidSansFallback.ttf",        # 老机型兜底
    "/system/fonts/DroidSansChinese.ttf",
]
FONT_PATHS = ANDROID_FONT_PATHS + [
    r"C:\Windows\Fonts\simhei.ttf",   # 优先系统黑体
    r"C:\Windows\Fonts\msyh.ttc",     # 其次微软雅黑
    os.path.join(_res_dir(), "中文字体.ttf"),   # 想换字体就把 ttf 放这儿并改名
    os.path.join(_res_dir(), "中文字体.otf"),
    os.path.join(_res_dir(), "simhei.ttf"),
]
_FONT_CACHE = {}


def load_font(size):
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    font = None
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                break
            except (OSError, pygame.error):
                continue
    if font is None:
        font = pygame.font.SysFont("simhei,simsun,arial", size)
    _FONT_CACHE[size] = font
    return font


# ---------------------------- 版本 / 创作者 / 设置项 ----------------------------
VERSION = "2.10"
APP_NAME = "中国象棋-智算单机版"
CREATOR = "songyq"     # 主页右下角标注；
TIME_OPTIONS = [5, 10, 20, 30, 60]    # 对战时间（分钟）
MOVE_TIME_OPTIONS = [0, 15, 30, 60]   # 单步限时（秒），0 = 不限时（只在圆表上正计时）
HOME_CREDIT_DX = 26                   # 主页落款「制作人」向左提一格的距离（px）
# 内置合成古曲（曲 目录里没有同名音频时用这些合成旋律兜底）
BGM_CORE = ["高山流水", "平沙落雁", "渔舟唱晚", "广陵散"]
BGM_NAMES = BGM_CORE          # 兼容旧引用；实际可用曲目请用 bgm_names()
BGM_MAX = 8                   # 设置面板最多列 8 个曲目（2 行 × 4）
MUSIC_MAX_FILES = 4           # 曲 目录里最多收 4 首自己导入的曲子
LIB_CATEGORIES = ["全部", "经典残局", "江湖排局", "自定残局", "收藏"]
CUSTOM_CATEGORY = "自定残局"      # 对战 / 摆棋里存下来的局面默认归到这里
UNDO_LIMITS = [("不限", 0), ("三次", 3), ("五次", 5)]
UNDO_LIMIT_VALUES = dict(UNDO_LIMITS)
DEFAULT_SOUND_VOL = 0.8
DEFAULT_MUSIC_VOL = 0.7


# ---------------------------- 背景古曲（程序内实时合成） ----------------------------
# 五声音阶（宫商角徵羽），不依赖外部音频文件
_PENTA = [130.81, 146.83, 164.81, 196.00, 220.00]   # C3 D3 E3 G3 A3


def _penta(i):
    """五声音阶第 i 级频率，支持跨八度"""
    if i < 0:
        return _penta(i + 5) / 2.0
    return _PENTA[i % 5] * (2 ** (i // 5))


def _make_track(seq, beat=0.46):
    """seq 为 [(音阶索引, 拍数), ...] → [(频率, 时长秒), ...]"""
    return [(round(_penta(i), 2), round(beat * b, 2)) for i, b in seq]


BGM_TRACKS = {
    # 高山流水：琶音如溪流层层递进，收于长音
    "高山流水": _make_track([
        (4, 1), (5, 0.5), (7, 0.5), (9, 1), (7, 0.5), (5, 0.5),
        (4, 1.5), (2, 0.5), (4, 2), (0, 0.5),
        (2, 1), (4, 0.5), (5, 0.5), (7, 1), (5, 0.5), (4, 0.5),
        (2, 1.5), (0, 0.5), (2, 2), (0, 0.5),
        (7, 1), (9, 0.5), (11, 0.5), (12, 2), (11, 0.5), (9, 0.5),
        (7, 1.5), (5, 0.5), (7, 2), (4, 0.5),
        (5, 1), (4, 0.5), (2, 0.5), (4, 1), (5, 1),
        (4, 0.5), (2, 0.5), (0, 3),
    ]),
    # 广陵散：低音区起手，庄重顿挫
    "广陵散": _make_track([
        (0, 1.5), (2, 0.5), (0, 1), (4, 1), (2, 1.5), (0, 0.5),
        (0, 2), (0, 0.5),
        (5, 1), (4, 0.5), (2, 0.5), (4, 1), (2, 1.5), (0, 0.5),
        (2, 2), (0, 0.5),
        (7, 1), (7, 0.5), (9, 1), (7, 0.5), (5, 0.5), (4, 1.5), (2, 0.5),
        (4, 2), (0, 0.5),
        (0, 1), (4, 1), (5, 1), (7, 1), (5, 1.5), (4, 0.5),
        (2, 1), (0, 3),
    ]),
    # 平沙落雁：长音铺陈，开阔疏朗
    "平沙落雁": _make_track([
        (7, 2.5), (9, 1), (11, 1), (9, 2.5), (7, 0.5), (5, 0.5),
        (7, 2), (0, 0.5),
        (5, 2), (4, 1), (5, 1), (7, 2.5), (9, 1), (7, 0.5), (5, 0.5),
        (4, 2), (0, 0.5),
        (2, 2), (4, 1), (5, 1), (7, 1.5), (9, 0.5), (7, 1),
        (5, 1.5), (4, 0.5), (2, 1), (0, 0.5),
        (4, 2), (2, 1), (0, 1), (2, 2.5), (0, 3),
    ]),
    # 渔舟唱晚：附点摇曳，归舟晚唱
    "渔舟唱晚": _make_track([
        (9, 1), (7, 0.5), (5, 0.5), (7, 1.5), (5, 0.5), (4, 1),
        (2, 1.5), (4, 0.5), (5, 2), (0, 0.5),
        (7, 1), (9, 0.5), (7, 0.5), (5, 1), (4, 1.5), (5, 0.5),
        (7, 2), (5, 0.5), (4, 0.5), (2, 2), (0, 0.5),
        (4, 1), (5, 0.5), (7, 0.5), (9, 1), (11, 0.5), (9, 0.5),
        (7, 1.5), (5, 0.5), (7, 2), (4, 0.5),
        (5, 1), (4, 0.5), (2, 0.5), (4, 1.5), (2, 0.5),
        (0, 1), (2, 0.5), (0, 3),
    ]),
}
BGM_CHANNEL = 1


def play_note(freq, dur, vol=0.16, channel=None):
    """合成并播放一个单音（背景古曲用）；指定 channel 则占用独立声道"""
    if freq <= 0 or dur <= 0:
        return
    try:
        buf = _build_wave([(freq, dur, 4.5)], vol, 0.0)
        snd = pygame.mixer.Sound(buffer=buf)
    except (pygame.error, OSError):
        return
    if channel is None:
        snd.play()
    else:
        try:
            pygame.mixer.Channel(channel).play(snd)
        except (AttributeError, pygame.error):
            snd.play()


# ---------------------------- 宋体（古典标题 / 落款） ----------------------------
def load_font_song(size):
    """优先使用宋体（simsun.ttc），落款与标题更有古典味；缓存于 _FONT_CACHE"""
    key = ("song", size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    for path in ANDROID_FONT_PATHS + [r"C:\Windows\Fonts\simsun.ttc",
                                      r"C:\Windows\Fonts\simsun.ttf",
                                      r"C:\Windows\Fonts\simhei.ttf",
                                      os.path.join(_res_dir(), "中文字体.ttf")]:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                _FONT_CACHE[key] = font
                return font
            except (OSError, pygame.error):
                continue
    font = pygame.font.SysFont("simsun,simhei,arial", size)
    _FONT_CACHE[key] = font
    return font


# 默认残局示例
DEFAULT_ENDGAME = {
    (0, 3): (BLACK, KING),
    (9, 3): (RED, KING),
    (9, 5): (RED, ROOK),
    (9, 6): (RED, ROOK),
    (8, 4): (RED, CANNON),
    (9, 4): (RED, CANNON),
    (1, 4): (BLACK, ADVISOR),
    (7, 3): (BLACK, PAWN),
}

# 标准开局
FULL_OPENING = {
    (0, 0): (BLACK, ROOK), (0, 1): (BLACK, HORSE), (0, 2): (BLACK, ELEPHANT),
    (0, 3): (BLACK, ADVISOR), (0, 4): (BLACK, KING), (0, 5): (BLACK, ADVISOR),
    (0, 6): (BLACK, ELEPHANT), (0, 7): (BLACK, HORSE), (0, 8): (BLACK, ROOK),
    (2, 1): (BLACK, CANNON), (2, 7): (BLACK, CANNON),
    (3, 0): (BLACK, PAWN), (3, 2): (BLACK, PAWN), (3, 4): (BLACK, PAWN),
    (3, 6): (BLACK, PAWN), (3, 8): (BLACK, PAWN),
    (9, 0): (RED, ROOK), (9, 1): (RED, HORSE), (9, 2): (RED, ELEPHANT),
    (9, 3): (RED, ADVISOR), (9, 4): (RED, KING), (9, 5): (RED, ADVISOR),
    (9, 6): (RED, ELEPHANT), (9, 7): (RED, HORSE), (9, 8): (RED, ROOK),
    (7, 1): (RED, CANNON), (7, 7): (RED, CANNON),
    (6, 0): (RED, PAWN), (6, 2): (RED, PAWN), (6, 4): (RED, PAWN),
    (6, 6): (RED, PAWN), (6, 8): (RED, PAWN),
}

POSITIONS = {"残局示例": DEFAULT_ENDGAME, "标准开局": FULL_OPENING}


# ---------------------------- 棋盘工具 ----------------------------
def in_board(r, c):
    return 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS


def in_palace(color, r, c):
    if color == RED:
        return r in (7, 8, 9) and c in (3, 4, 5)
    return r in (0, 1, 2) and c in (3, 4, 5)


def own_side(color, r):
    if color == RED:
        return r >= 5
    return r <= 4


# 落点规则：士走九宫斜点、象守本方七象位、兵卒只进不退
ADVISOR_POINTS = {
    RED: {(9, 3), (9, 5), (8, 4), (7, 3), (7, 5)},
    BLACK: {(0, 3), (0, 5), (1, 4), (2, 3), (2, 5)},
}
ELEPHANT_POINTS = {
    RED: {(9, 2), (9, 6), (7, 0), (7, 4), (7, 8), (5, 2), (5, 6)},
    BLACK: {(0, 2), (0, 6), (2, 0), (2, 4), (2, 8), (4, 2), (4, 6)},
}
PAWN_ROW_RANGE = {RED: (0, 6), BLACK: (3, 9)}     # 兵/卒可以出现的行区间


def square_rule(piece, r, c):
    """落点规则：把一枚棋子摆在 (r,c) 是否合规。返回 (是否合规, 提示语)"""
    if not in_board(r, c):
        return False, "落点超出棋盘范围。"
    pc, pt = piece
    pname = CHINESE_PIECES[(pc, pt)]
    if pt == KING:
        if not in_palace(pc, r, c):
            return False, "%s「%s」只能落在九宫内。" % (name_of(pc), pname)
    elif pt == ADVISOR:
        if (r, c) not in ADVISOR_POINTS[pc]:
            return False, "%s「%s」斜行，只能落在九宫的五个斜点上。" % (name_of(pc), pname)
    elif pt == ELEPHANT:
        if (r, c) not in ELEPHANT_POINTS[pc]:
            return False, ("%s「%s」只能守本方的七个象位，不能过河，"
                           "也不能落在象位以外。" % (name_of(pc), pname))
    elif pt == PAWN:
        lo, hi = PAWN_ROW_RANGE[pc]
        if not lo <= r <= hi:
            return False, ("%s「%s」只进不退，只能落在兵行线及对方一侧。"
                           % (name_of(pc), pname))
    return True, ""


def position_rule_message(board):
    """整盘落点核验：返回第一条不合规说明，全盘合规返回 None"""
    for (r, c), piece in sorted(board.items()):
        ok, why = square_rule(piece, r, c)
        if not ok:
            return why
    return None


def opponent(color):
    return BLACK if color == RED else RED


def name_of(color):
    return "红方" if color == RED else "黑方"


def piece_at(board, r, c):
    return board.get((r, c))


_KING_HINT = {}          # 上一回找到的将/帅位置：搜索里将帅极少动，命中率极高


def find_king(board, color):
    """找将/帅。先用上次的位置试一下（命中率极高），不中再遍历棋盘。
    命中时仍然用 board 校验一遍，所以缓存绝不会给出错的答案。"""
    hint = _KING_HINT.get(color)
    if hint is not None and board.get(hint) == (color, KING):
        return hint
    for (r, c), (pc, pt) in board.items():
        if pc == color and pt == KING:
            _KING_HINT[color] = (r, c)
            return r, c
    return None


def kings_face(board):
    rk = find_king(board, RED)
    bk = find_king(board, BLACK)
    if not rk or not bk:
        return False
    if rk[1] != bk[1]:
        return False
    for r in range(min(rk[0], bk[0]) + 1, max(rk[0], bk[0])):
        if (r, rk[1]) in board:
            return False
    return True


# ---------------------------- 走子生成 ----------------------------
HORSE_DELTAS = [
    (2, 1, 1, 0), (2, -1, 1, 0), (-2, 1, -1, 0), (-2, -1, -1, 0),
    (1, 2, 0, 1), (-1, 2, 0, 1), (1, -2, 0, -1), (-1, -2, 0, -1),
]


def raw_moves(board, r, c):
    piece = piece_at(board, r, c)
    if not piece:
        return []
    pc, pt = piece
    moves = []

    def add(nr, nc):
        if not in_board(nr, nc):
            return
        target = piece_at(board, nr, nc)
        if target and target[0] == pc:
            return
        moves.append((nr, nc))

    if pt == KING:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if in_palace(pc, nr, nc):
                add(nr, nc)

    elif pt == ADVISOR:
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nr, nc = r + dr, c + dc
            if in_palace(pc, nr, nc):
                add(nr, nc)

    elif pt == ELEPHANT:
        for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            nr, nc = r + dr, c + dc
            mr, mc = r + dr // 2, c + dc // 2
            if in_board(nr, nc) and own_side(pc, nr) and not piece_at(board, mr, mc):
                add(nr, nc)

    elif pt == HORSE:
        for dr, dc, mr, mc in HORSE_DELTAS:
            nr, nc = r + dr, c + dc
            if in_board(nr, nc) and not piece_at(board, r + mr, c + mc):
                add(nr, nc)

    elif pt == ROOK:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            while in_board(nr, nc):
                target = piece_at(board, nr, nc)
                if target:
                    if target[0] != pc:
                        moves.append((nr, nc))
                    break
                moves.append((nr, nc))
                nr += dr
                nc += dc

    elif pt == CANNON:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            jumped = False
            while in_board(nr, nc):
                target = piece_at(board, nr, nc)
                if not jumped:
                    if target:
                        jumped = True
                    else:
                        moves.append((nr, nc))
                else:
                    if target:
                        if target[0] != pc:
                            moves.append((nr, nc))
                        break
                nr += dr
                nc += dc

    elif pt == PAWN:
        if pc == RED:
            if r > 0:
                add(r - 1, c)
            if r <= 4:
                add(r, c - 1)
                add(r, c + 1)
        else:
            if r < 9:
                add(r + 1, c)
            if r >= 5:
                add(r, c - 1)
                add(r, c + 1)

    return moves


# ---------------------------- 合法性与将军 ----------------------------
def apply_move(board, fr, fc, tr, tc):
    new_board = dict(board)
    new_board[(tr, tc)] = new_board.pop((fr, fc))
    return new_board


def _attacked_by_pawn(board, kr, kc, enemy):
    if enemy == BLACK:
        cands = [(kr - 1, kc)]
        if kr >= 5:
            cands += [(kr, kc - 1), (kr, kc + 1)]
    else:
        cands = [(kr + 1, kc)]
        if kr <= 4:
            cands += [(kr, kc - 1), (kr, kc + 1)]
    for r, c in cands:
        p = board.get((r, c))
        if p and p[0] == enemy and p[1] == PAWN:
            return True
    return False


def _attacked_by_horse(board, kr, kc, enemy):
    for dr, dc in ((2, 1), (2, -1), (-2, 1), (-2, -1),
                   (1, 2), (1, -2), (-1, 2), (-1, -2)):
        hr, hc = kr + dr, kc + dc
        p = board.get((hr, hc))
        if not p or p[0] != enemy or p[1] != HORSE:
            continue
        # 马从 (hr,hc) 跳到 (kr,kc)，蹩马腿在长边方向的第一格
        lr = hr + (1 if -dr == 2 else (-1 if -dr == -2 else 0))
        lc = hc + (1 if -dc == 2 else (-1 if -dc == -2 else 0))
        if not in_board(lr, lc) or (lr, lc) not in board:
            return True
    return False


def _attacked_by_slider(board, kr, kc, enemy):
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r, c = kr + dr, kc + dc
        blockers = 0
        while in_board(r, c):
            p = board.get((r, c))
            if p:
                pc, pt = p
                if pc == enemy:
                    if blockers == 0:
                        if pt == ROOK:
                            return True
                        if pt == KING and (abs(r - kr) + abs(c - kc)) == 1:
                            return True
                    elif blockers == 1 and pt == CANNON:
                        return True
                blockers += 1
                if blockers >= 2:
                    break
            r += dr
            c += dc
    return False


def in_check(board, color):
    """判断 color 一方是否被攻击（含被将军）。

    三种攻击检测写在一个函数里、把 board.get 绑成局部变量：搜索时每秒要调用
    几十万次，省下的函数调用与全局名查找，换成的是实打实的一层深度。
    逻辑与 _attacked_by_* 完全一致（那几个函数留着给外部调用与自检用）。"""
    king = find_king(board, color)
    if king is None:
        return True
    kr, kc = king
    enemy = BLACK if color == RED else RED
    get = board.get

    # 车 / 炮 / 将帅：同行同列
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r = kr + dr
        c = kc + dc
        blockers = 0
        while 0 <= r < 10 and 0 <= c < 9:
            p = get((r, c))
            if p is not None:
                if p[0] == enemy:
                    pt = p[1]
                    if blockers == 0:
                        if pt == ROOK:
                            return True
                        if pt == KING and abs(r - kr) + abs(c - kc) == 1:
                            return True
                    elif blockers == 1 and pt == CANNON:
                        return True
                blockers += 1
                if blockers >= 2:
                    break
            r += dr
            c += dc

    # 马：八个马位，顺手把马腿（靠近马那一侧的直格）算出来
    for dr, dc in ((2, 1), (2, -1), (-2, 1), (-2, -1),
                   (1, 2), (1, -2), (-1, 2), (-1, -2)):
        hr = kr + dr
        hc = kc + dc
        p = get((hr, hc))
        if p is None or p[0] != enemy or p[1] != HORSE:
            continue
        if dr == 2 or dr == -2:
            lr, lc = hr - dr // 2, hc
        else:
            lr, lc = hr, hc - dc // 2
        if (lr, lc) not in board:
            return True

    # 兵 / 卒：本方半场里只能迎面顶，过了河才能横吃
    if enemy == BLACK:
        p = get((kr - 1, kc))
        if p is not None and p[0] == enemy and p[1] == PAWN:
            return True
        if kr >= 5:
            p = get((kr, kc - 1))
            if p is not None and p[0] == enemy and p[1] == PAWN:
                return True
            p = get((kr, kc + 1))
            if p is not None and p[0] == enemy and p[1] == PAWN:
                return True
    else:
        p = get((kr + 1, kc))
        if p is not None and p[0] == enemy and p[1] == PAWN:
            return True
        if kr <= 4:
            p = get((kr, kc - 1))
            if p is not None and p[0] == enemy and p[1] == PAWN:
                return True
            p = get((kr, kc + 1))
            if p is not None and p[0] == enemy and p[1] == PAWN:
                return True
    return False


def legal_moves(board, color):
    """全部合法着法。

    提速关键（v2.3）：会走出「自己被将」的着法只有三种来源 ——
      · 走开的是与己方将帅同行 / 同列的棋子（拔掉了挡子，或让炮找到了炮架）；
      · 走的是将帅本人；
      · 本来就正被将军（所以每一步都得验）。
    其余着法一律直接放行，不必跑攻击检测。实测着法生成快三倍以上。"""
    king = find_king(board, color)
    if king is None:
        return []
    kr, kc = king
    danger = in_check(board, color)
    moves = []
    keys = [k for k, v in board.items() if v[0] == color]
    for key in keys:
        piece = board[key]
        r, c = key
        quick = not danger and r != kr and c != kc
        for tr, tc in raw_moves(board, r, c):
            if quick and tr != kr and tc != kc:
                moves.append((r, c, tr, tc))
                continue
            victim = board.get((tr, tc))
            board[(tr, tc)] = piece
            del board[key]
            try:
                ok = not kings_face(board) and not in_check(board, color)
            finally:
                board[key] = board.pop((tr, tc))
                if victim is not None:
                    board[(tr, tc)] = victim
            if ok:
                moves.append((r, c, tr, tc))
    return moves


def is_checkmate(board, color):
    return in_check(board, color) and len(legal_moves(board, color)) == 0


def insufficient_material(board):
    """子力不足判和：双方都再也不可能把对方将死。

    判定口径（跟着象棋惯例走，宁可放过、不可错杀）：
      · 一方只要有车、炮、兵（卒），就还有进攻手段 —— 不算和；
      · 马算半个：一匹马还能「马后炮」式的巧胜，两匹马才算真有攻势；
      · 双方都只剩将帅 + 士象（或至多各一匹马）时，任何走法都分不出胜负。
    典型的「光将对光将」「单马对光将」「单马对单马」「只剩将士象互磨」
    都落在这里 —— 以前这些局面要磨到六十回合无吃子才判和，用户看着就是
    「明明和定了却还在下」。"""
    for color in (RED, BLACK):
        horses = 0
        for (pc, pt) in board.values():
            if pc != color:
                continue
            if pt in (ROOK, CANNON, PAWN):
                return False
            if pt == HORSE:
                horses += 1
        if horses >= 2:
            return False
    return True


def move_reason(board, fr, fc, tr, tc):
    """落点合法性说明：这步可走返回 None，不可走返回具体原因（用于对局提示）"""
    piece = piece_at(board, fr, fc)
    if not piece:
        return None
    pc, pt = piece
    if (fr, fc, tr, tc) in legal_moves(board, pc):
        return None
    pname = CHINESE_PIECES[(pc, pt)]
    target = piece_at(board, tr, tc)
    if target and target[0] == pc:
        return "「%s」不能吃自己的子。" % pname
    if (tr, tc) not in raw_moves(board, fr, fc):
        if pt == KING:
            return "「%s」只能在九宫内直走一步。" % pname
        if pt == ADVISOR:
            return "「%s」只能在九宫内斜走一步。" % pname
        if pt == ELEPHANT:
            if abs(tr - fr) != 2 or abs(tc - fc) != 2:
                return "「%s」走田字，须斜走两格。" % pname
            if not own_side(pc, tr):
                return "「%s」不能过河。" % pname
            if piece_at(board, (fr + tr) // 2, (fc + tc) // 2):
                return "象眼被塞，「%s」走不过去。" % pname
            return "「%s」不这样走。" % pname
        if pt == HORSE:
            return "马腿被别住，「%s」走不过去。" % pname
        if pt == ROOK:
            return "「%s」只能沿直线行走。" % pname
        if pt == CANNON:
            return "「%s」走直线，吃子须隔一个棋子。" % pname
        if pt == PAWN:
            if (pc == RED and tr > fr) or (pc == BLACK and tr < fr):
                return "「%s」不能后退。" % pname
            return "「%s」未过河不能横走。" % pname
        return "「%s」不能这样走。" % pname
    if kings_face(apply_move(board, fr, fc, tr, tc)):
        return "将帅不能照面。"
    return "这步走完自己的将/帅会被将军。"


# ---------------------------- 残局 AI（置换表 + 静态搜索 + 迭代加深） ----------------------------
# 子力价值按象棋惯例（车 9 / 炮 4.5 / 马 4.2 / 兵 1，士象各 2）：
# 旧版把士象压到 20 分，电脑会为救一个兵把士象送掉，防守立刻漏风。
PIECE_VALUES = {KING: 10000, ROOK: 900, CANNON: 450, HORSE: 420,
                PAWN: 100, ADVISOR: 200, ELEPHANT: 200}
MATE_SCORE = 100000


def _pst(text):
    """把 90 个空格分隔的数字读成位置分表"""
    vals = [int(v) for v in text.split()]
    if len(vals) != 90:
        raise ValueError("位置分表应有 90 个数字，实得 %d" % len(vals))
    return vals


def _sparse_pst(cells):
    vals = [0] * 90
    for (r, c), v in cells.items():
        vals[r * 9 + c] = v
    return vals


# 位置分表统一按「红方视角」写：第 0 行是黑方底线，第 9 行是红方底线。
# 黑方查表时行、列都镜像（9-r, 8-c），一张表两方通用。
_PST = {
    PAWN: _pst("""
        20 24 30 40 46 40 30 24 20
        30 40 55 62 68 62 55 40 30
        10 18 30 42 48 42 30 18 10
         6 12 20 30 36 30 20 12  6
         4 10 16 22 26 22 16 10  4
         2  6 10 14 18 14 10  6  2
         0  0  0  0  0  0  0  0  0
         0  0  0  0  0  0  0  0  0
         0  0  0  0  0  0  0  0  0
         0  0  0  0  0  0  0  0  0
    """),
    ROOK: _pst("""
        10 12 14 16 16 16 14 12 10
        12 16 18 20 22 20 18 16 12
        12 18 20 24 26 24 20 18 12
        10 16 18 22 24 22 18 16 10
        10 14 16 20 22 20 16 14 10
         8 12 14 16 18 16 14 12  8
         6 10 12 14 16 14 12 10  6
         6  8 10 12 14 12 10  8  6
         4  6  8 10 12 10  8  6  4
         2  4  6  8 10  8  6  4  2
    """),
    HORSE: _pst("""
         2  4  6  6  6  6  6  4  2
         4  8 12 12 14 12 12  8  4
         6 12 16 18 20 18 16 12  6
         6 14 18 20 22 20 18 14  6
         6 14 18 20 22 20 18 14  6
         4 12 16 18 20 18 16 12  4
         2 10 12 14 16 14 12 10  2
         0  6  8 10 12 10  8  6  0
         0  2  4  6  6  6  4  2  0
         0  0  2  2  4  2  2  0  0
    """),
    CANNON: _pst("""
         4  4  6  6  8  6  6  4  4
         6  8 10 12 14 12 10  8  6
         6 10 14 16 20 16 14 10  6
         4  8 12 14 18 14 12  8  4
         4  8 12 14 18 14 12  8  4
         2  6 10 12 16 12 10  6  2
         2  6 10 12 14 12 10  6  2
         2  6 10 12 14 12 10  6  2
         2  4  8 10 12 10  8  4  2
         0  2  4  6  8  6  4  2  0
    """),
    # 士象留在原位有分，乱飞要扣分：将门两侧的士、中路象最有用
    ADVISOR: _sparse_pst({(9, 3): 8, (9, 5): 8, (8, 4): 5, (7, 3): 3, (7, 5): 3}),
    ELEPHANT: _sparse_pst({(9, 2): 6, (9, 6): 6, (7, 4): 8, (7, 0): 4, (7, 8): 4}),
}


def _pos_bonus(pc, pt, r, c):
    """位置分：兵过河、马炮居中、车占要道，查表 O(1)"""
    tbl = _PST.get(pt)
    if tbl is None:
        return 0
    if pc == RED:
        return tbl[r * 9 + c]
    return tbl[(9 - r) * 9 + (8 - c)]


def _edge_bonus(r, c):
    """离棋盘边线越近分越高（残局逼将用）：中线 0 分，边线 4 分"""
    return (4 - min(r, 9 - r)) + (4 - min(c, 8 - c))


def _mop_up(strong_king, weak_king):
    """残局收尾技巧：把对方将帅往边上赶 + 自己帅靠过去。
    车兵残局里这两项不会自己出现在子力分里，但正是「会不会赢下来」的关键。"""
    if strong_king is None or weak_king is None:
        return 0
    dist = max(abs(strong_king[0] - weak_king[0]),
               abs(strong_king[1] - weak_king[1]))
    return 12 * _edge_bonus(*weak_king) - 8 * dist


def evaluate(board):
    """局面分（正数红方好）。

    v2.3 加入「阶段判断」：残局和中局的打分口径本来就该不一样 ——
      · 兵：中局只算位置，残局多一个兵往往就是胜负，按残局程度额外加权；
      · 士象：中局守住家门不便宜，残局防守价值下降；缺一个士或象则要重罚
        （车马难破士象全，反过来缺士的一方常常直接崩）；
      · 收尾技巧：一方白多一个车、对方又没有车马炮时，逼将上边、帅往上靠
        （`_mop_up`），把「赢了但不会杀」的局收下来。
    仍然只遍历一遍棋盘，顺带把子数统出来，不给搜索加负担。"""
    score = 0
    rp = bp = 0                      # 兵 / 卒
    ra = ba = re = be = 0            # 士、象
    heavy = 0                        # 车马炮总数，用来判断残局程度
    mat_r = mat_b = 0                # 不含将帅的子力分（判残局收尾用）
    hv_r = hv_b = 0                  # 各方车马炮数量
    rk = bk = None                   # 双方将帅位置
    for (r, c), (pc, pt) in board.items():
        if pt == KING:
            if pc == RED:
                rk = (r, c)
            else:
                bk = (r, c)
            v = PIECE_VALUES.get(pt, 0)
            score += v if pc == RED else -v
            continue
        base = PIECE_VALUES.get(pt, 0)
        v = base + _pos_bonus(pc, pt, r, c)
        if pc == RED:
            score += v
            mat_r += base
            if pt == PAWN:
                rp += 1
            elif pt == ADVISOR:
                ra += 1
            elif pt == ELEPHANT:
                re += 1
            else:
                heavy += 1
                hv_r += 1
        else:
            score -= v
            mat_b += base
            if pt == PAWN:
                bp += 1
            elif pt == ADVISOR:
                ba += 1
            elif pt == ELEPHANT:
                be += 1
            else:
                heavy += 1
                hv_b += 1

    phase = 1.0 - min(heavy, 6) / 6.0     # 0 = 满子开局，1 = 纯残局
    if phase > 0.0:
        score += int((rp - bp) * 55 * phase)
        lack_r = (2 - ra) * 26 + (2 - re) * 26
        lack_b = (2 - ba) * 26 + (2 - be) * 26
        score += int((lack_b - lack_r) * (0.5 + 0.8 * phase))

    # 残局收尾：一方多出一个车以上、对方又没有车马炮，才启用逼将 / 靠帅
    if phase > 0.30:
        if mat_r - mat_b >= 400 and hv_b == 0:
            score += _mop_up(rk, bk)
        elif mat_b - mat_r >= 400 and hv_r == 0:
            score -= _mop_up(bk, rk)

    # 将帅被将军的一方要先把这口气解掉，给一点「轮走压力」分
    if in_check(board, BLACK):
        score += 40
    if in_check(board, RED):
        score -= 40
    return score



# Zobrist 散列：给「棋盘 + 走子方」一个 64 位指纹，用于置换表
_ZOBRIST = {}
_rnd_z = random.Random(20261101)
for _sq in range(90):
    for _pc in (RED, BLACK):
        for _pt in (KING, ADVISOR, ELEPHANT, HORSE, ROOK, CANNON, PAWN):
            _ZOBRIST[(_sq, _pc, _pt)] = _rnd_z.getrandbits(64)
_ZOBRIST_TURN = _rnd_z.getrandbits(64)


def board_hash(board, turn):
    h = 0
    for (r, c), (pc, pt) in board.items():
        h ^= _ZOBRIST[(r * 9 + c, pc, pt)]
    return h ^ (_ZOBRIST_TURN if turn == BLACK else 0)


class _SearchTimeout(Exception):
    """迭代加深超出时间预算时用于中止搜索"""


_deadline = None
_node_count = 0
_TT = {}            # hash -> (深度, 标志, 分值, 着法)，标志 0 精确 / 1 下界 / 2 上界
_TT_LIMIT = 160000  # 置换表条目上限，超过就整体清空（约十几 MB，不会一直涨）
_ROOT_BANNED = frozenset()   # 根层禁走的着法（用于禁止重复走子）
QUIESCE_PLIES = 3   # 静态搜索最多再延伸几层吃子
EXT_BUDGET = 3      # 每一轮迭代加深允许的「将军延伸」总层数
_HISTORY = {}       # 安静着法历史启发：着法 -> 抢到 beta 的次数权重
_KILLERS = {}       # ply -> [第一杀手着法, 第二杀手着法]
_ext_left = EXT_BUDGET
NULL_MOVE_R = 2     # 空着裁剪：假装自己不走，让对方白走一步，直接砍掉几层
_null_lock = False  # 空着裁剪不能连着用，否则连续空着会把局面算歪
ASP_WIN = 70        # 渴望窗口半宽：窄窗命中就省一大批节点，命不中再全窗口重搜
# 剪枝开关：正常全开。留着是为了能一项一项关掉做强度对比（见 _tools\剪枝对照.py）
_OPT = {"pvs": True, "lmr": True, "null": True, "ext": True}
_CHECK_HASH = False   # 调试用：每个节点重算一遍指纹，验证增量更新没错
_last_depth = 0     # 上一手真正算完的层数（界面上会写出来，方便知道电脑算得多深）
# 搜索路径上的局面指纹计数（含走子方）。棋规里同一局面第 3 次出现要么和棋、要么
# 长将方判负，搜索必须知道这件事，否则会在优势局面里被「来回倒」白送和棋：
# 以前引擎不会算这个，残局里经常「多一个车还在绕圈」。
_REP_STACK = {}


def _pop_rep(key, prev):
    """从重复局面栈里退出一个节点（prev 为 0 时整条删掉，别留空壳）"""
    if prev:
        _REP_STACK[key] = prev
    else:
        _REP_STACK.pop(key, None)



_last_pump = 0.0
_AI_STATE = {"cancel": False, "busy": False}   # 后台搜索的取消位 / 占用位
_PUMP_IN_SEARCH = True      # 主线程搜索时才由搜索循环泵消息；线程里禁止碰 SDL


def _tick_time():
    """每 128 个节点检查一次：是否超时、是否被要求取消，并顺手泵一下窗口消息。
    搜索在主线程跑时（如「提示」按钮），若一直不处理系统消息，
    Windows 会把窗口标成「未响应」；pump 只收消息、不清空事件队列。
    搜索在后台线程跑时不泵消息——SDL 只允许主线程碰它。"""
    global _node_count, _last_pump
    _node_count += 1
    if _node_count & 127:
        return
    if _AI_STATE["cancel"]:
        raise _SearchTimeout
    now = time.perf_counter()
    if _deadline is not None and now > _deadline:
        raise _SearchTimeout
    if _PUMP_IN_SEARCH and now - _last_pump > 0.12:
        _last_pump = now
        try:
            pygame.event.pump()
        except pygame.error:
            pass


def quiesce(board, alpha, beta, maximizing, plies):
    """静态搜索：只展开吃子，避免“吃完就结束”的地平线误差。
    走子同样是「就地改、算完撤」，不复制棋盘。"""
    _tick_time()
    stand = evaluate(board)
    if maximizing:
        if stand >= beta:
            return beta
        if stand > alpha:
            alpha = stand
    else:
        if stand <= alpha:
            return alpha
        if stand < beta:
            beta = stand
    if plies <= 0:
        return stand

    color = RED if maximizing else BLACK
    caps = capture_moves(board, color)
    if not caps:
        return stand

    def q_key(mv):
        """吃子排序：净收益大的先试（被吃子价值 − 出手子价值），
        能让 alpha 更早抬起来，后面的吃子大多被 delta 剪掉。"""
        return -(PIECE_VALUES.get(mv[4], 0) * 8
                 - PIECE_VALUES.get(board[(mv[0], mv[1])][1], 0))

    caps.sort(key=q_key)

    for fr, fc, tr, tc, _v in caps:
        # delta 剪枝：吃下这个子也追不上 alpha（或已经高过 beta），这层白算
        gain = PIECE_VALUES.get(_v, 0)
        if maximizing:
            if stand + gain + 100 <= alpha:
                continue
        else:
            if stand - gain - 100 >= beta:
                continue
        piece = board[(fr, fc)]
        victim = board[(tr, tc)]
        board[(tr, tc)] = piece
        del board[(fr, fc)]
        try:
            score = quiesce(board, alpha, beta, not maximizing, plies - 1)
        finally:
            board.pop((tr, tc))
            board[(fr, fc)] = piece
            board[(tr, tc)] = victim
        if maximizing:
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        else:
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
    return alpha if maximizing else beta


def capture_moves(board, color):
    """只生成吃子着法（静态搜索专用）：比全量合法着法快一个数量级。
    同样用就地走子 / 撤销，省掉整盘复制。"""
    out = []
    keys = [k for k, v in board.items() if v[0] == color]
    for key in keys:
        piece = board[key]
        r, c = key
        for tr, tc in raw_moves(board, r, c):
            victim = board.get((tr, tc))
            if victim is None:
                continue
            board[(tr, tc)] = piece
            del board[key]
            try:
                ok = not kings_face(board) and not in_check(board, color)
            finally:
                board[key] = board.pop((tr, tc))
                board[(tr, tc)] = victim
            if ok:
                out.append((r, c, tr, tc, victim[1]))
    return out


def minimax(board, depth, alpha, beta, maximizing, ply=0, hkey=None):
    """主搜索（v2.3 重写）：
      · 就地走子 / 撤销，配合增量指纹，不再每个节点复制整盘；
      · PVS 主变例搜索：第一个着法全窗口，其余先零窗口试探，失败再全窗口重搜；
      · LMR 后期着法削减：排序靠后的安静着法先少算一两层，确认有戏再补；
      · 空着裁剪：子力还多的局面里，假设自己不走对方也占不到便宜，直接剪掉。
    配合渴望窗口与置换表深度优先替换，同样的时间能多看两三层。"""
    global _ext_left, _null_lock
    _tick_time()
    turn = RED if maximizing else BLACK
    if hkey is None:
        hkey = board_hash(board, turn)
    elif _CHECK_HASH and hkey != board_hash(board, turn):
        raise AssertionError("增量指纹与实算不一致")

    ent = _TT.get(hkey)
    tt_move = None
    if ent is not None:
        e_depth, e_flag, e_val, e_move = ent
        tt_move = e_move
        # 根层不做置换表截断：根层每轮都要交出一个着法，而且它带着「禁走」过滤
        if ply > 0 and e_depth >= depth:
            if e_flag == 0:
                return e_val, e_move
            if e_flag == 1 and e_val >= beta:
                return e_val, e_move
            if e_flag == 2 and e_val <= alpha:
                return e_val, e_move

    if depth <= 0:
        return quiesce(board, alpha, beta, maximizing, QUIESCE_PLIES), None

    in_danger = in_check(board, turn)
    moves = legal_moves(board, turn)
    if not moves:                     # 将死 / 困毙：越早死分越差，逼它优先走快杀
        return (-MATE_SCORE + ply) if maximizing else (MATE_SCORE - ply), None

    if ply == 0 and _ROOT_BANNED:
        filtered = [mv for mv in moves if mv not in _ROOT_BANNED]
        if filtered:
            moves = filtered

    # 空着裁剪：不在将军、子力还不少、也没连着空着过。
    # 层数越深让得越多（R = 2 + depth//4）：深处本来就是粗算，敢多砍一点。
    opt = _OPT
    if (opt["null"] and depth >= 3 and ply > 0 and not in_danger and not _null_lock
            and len(board) >= 13):
        _null_lock = True
        try:
            val, _ = minimax(board, depth - 1 - (NULL_MOVE_R + depth // 4), alpha,
                             beta, not maximizing, ply + 1, hkey ^ _ZOBRIST_TURN)
        finally:
            _null_lock = False
        if maximizing and val >= beta:
            return val, None
        if (not maximizing) and val <= alpha:
            return val, None

    killers = _KILLERS.get(ply) or ()

    def order_key(mv):
        """排序：置换表着法 → 吃子（先吃大子、少用大子换）→ 杀手着法 → 历史分。
        好的排序能让剪枝多砍掉一大半分支，同等时间就能多算一层。"""
        if tt_move is not None and mv == tt_move:
            return -10 ** 9
        victim = board.get((mv[2], mv[3]))
        if victim is not None:
            mover = board[(mv[0], mv[1])][1]
            return -(10 ** 6 + PIECE_VALUES.get(victim[1], 0) * 16
                     - PIECE_VALUES.get(mover, 0) // 8)
        if mv in killers:
            return -10 ** 5 + (0 if mv == killers[0] else 1)
        return -_HISTORY.get(mv, 0)

    moves.sort(key=order_key)

    alpha0, beta0 = alpha, beta
    best_move = moves[0]
    value = -math.inf if maximizing else math.inf
    first = True

    for idx, (fr, fc, tr, tc) in enumerate(moves):
        piece = board[(fr, fc)]
        victim = board.get((tr, tc))
        child_key = (hkey
                     ^ _ZOBRIST[(fr * 9 + fc, piece[0], piece[1])]
                     ^ _ZOBRIST[(tr * 9 + tc, piece[0], piece[1])]
                     ^ _ZOBRIST_TURN)
        if victim is not None:
            child_key ^= _ZOBRIST[(tr * 9 + tc, victim[0], victim[1])]

        board[(tr, tc)] = piece
        del board[(fr, fc)]
        rep_prev = _REP_STACK.get(child_key, 0)
        try:
            gives = in_check(board, opponent(turn))     # 走完是否将军（延伸 / 削减都要用）
            child_depth = depth - 1
            # 将军延伸：临近叶子时对手被将军就多看一层，免得「将完才发现自己亏子」。
            # 延伸总数受 _ext_left 限制，不会把搜索炸开。
            if opt["ext"] and _ext_left > 0 and depth <= 2 and gives:
                child_depth = depth
                _ext_left -= 1

            if rep_prev >= 2:
                # 走完是同一局面第 3 次出现：棋规上不是和棋就是长将判负，都别再往下算了。
                if gives:                       # 还在将军 → 走子方长将，直接算它输
                    child = (-MATE_SCORE + ply) if turn == RED else (MATE_SCORE - ply)
                else:                           # 双方都没将军 → 三次重复，判和
                    child = 0
                first = False
            elif first or not opt["pvs"]:
                _REP_STACK[child_key] = rep_prev + 1
                try:
                    child, _ = minimax(board, child_depth, alpha, beta,
                                       not maximizing, ply + 1, child_key)
                finally:
                    _pop_rep(child_key, rep_prev)
                first = False
            else:
                _REP_STACK[child_key] = rep_prev + 1
                try:
                    reduce = 0
                    # 根层不削减：根层着法就是最终要交出去的那一步，削浅了容易漏好棋
                    if (opt["lmr"] and ply > 0 and child_depth >= 3 and idx >= 4
                            and victim is None and not gives and not in_danger):
                        reduce = 1 if idx < 14 else 2
                    if maximizing:
                        lo, hi = alpha, min(alpha + 1, beta)
                    else:
                        lo, hi = max(beta - 1, alpha), beta
                    child, _ = minimax(board, child_depth - reduce, lo, hi,
                                       not maximizing, ply + 1, child_key)
                    miss = (child > alpha) if maximizing else (child < beta)
                    if miss:
                        child, _ = minimax(board, child_depth, alpha, beta,
                                           not maximizing, ply + 1, child_key)
                finally:
                    _pop_rep(child_key, rep_prev)
        finally:
            board.pop((tr, tc))
            board[(fr, fc)] = piece
            if victim is not None:
                board[(tr, tc)] = victim

        if maximizing:
            if child > value:
                value, best_move = child, (fr, fc, tr, tc)
            if value > alpha:
                alpha = value
        else:
            if child < value:
                value, best_move = child, (fr, fc, tr, tc)
            if value < beta:
                beta = value
        if beta <= alpha:
            if victim is None:          # 安静着法剪出的好棋：记进杀手 / 历史表
                mv = (fr, fc, tr, tc)
                _HISTORY[mv] = _HISTORY.get(mv, 0) + depth * depth
                ks = _KILLERS.setdefault(ply, [None, None])
                if ks[0] != mv:
                    ks[1] = ks[0]
                    ks[0] = mv
            break

    if value <= alpha0:
        flag = 2
    elif value >= beta0:
        flag = 1
    else:
        flag = 0
    # 置换表替换策略：表满时用「更深的留下」，同深度覆盖旧的
    # （只留浅层条目会让好不容易搜深的分支被挤掉，反复重算）
    old = _TT.get(hkey)
    if old is None or len(_TT) < _TT_LIMIT or depth >= old[0]:
        _TT[hkey] = (depth, flag, value, best_move)
    return value, best_move


# 各难度：搜索层数上限（迭代加深的封顶）、时间预算（秒）、随机失误概率
# 「大师」把封顶提到 8 层，真正跑到几层由 5.5 秒预算决定：多余的时间不再浪费。
DIFFICULTY_LEVELS = [("简单", 1), ("普通", 2), ("困难", 4), ("大师", 8)]
DIFFICULTY_DEPTH = dict(DIFFICULTY_LEVELS)
DIFFICULTY_BUDGET = {1: 0.15, 2: 0.70, 3: 1.80, 4: 1.80, 5: 5.50, 8: 5.50}
BLUNDER_RATE = {1: 0.30, 2: 0.10, 3: 0.0, 4: 0.0, 5: 0.0, 8: 0.0}


# ---------------------------- 开局库 ----------------------------
# 常见开局的成有着法（坐标序列，红先）。开局前几手直接照谱走：
# 既省下思考时间，也避免一上来就走出「炮打底马」这种亏子棋。
# 每条线路都是一串 (起行, 起列, 至行, 至列)，红黑交替。
# 走完线路就交回搜索，所以不会一直照着谱走。
OPENING_LINES = [
    # 中炮对屏风马（最正统的一路）
    [(7, 7, 7, 4), (0, 7, 2, 6), (9, 7, 7, 6), (0, 8, 0, 7),
     (9, 8, 9, 7), (0, 1, 2, 2), (6, 6, 5, 6), (3, 2, 4, 2)],
    # 中炮对顺手炮（对攻，火力旺）
    [(7, 7, 7, 4), (2, 1, 2, 4), (9, 7, 7, 6), (0, 7, 2, 6),
     (9, 8, 9, 7), (0, 8, 1, 8), (6, 6, 5, 6), (1, 8, 1, 7)],
    # 仙人指路对卒底（先探虚实）
    [(6, 2, 5, 2), (3, 6, 4, 6), (9, 1, 7, 2), (0, 7, 2, 6),
     (9, 6, 7, 4), (0, 8, 0, 7), (9, 7, 7, 6), (0, 1, 2, 2)],
    # 飞相局（稳守反击）
    [(9, 6, 7, 4), (2, 1, 2, 4), (9, 1, 7, 2), (0, 7, 2, 6),
     (9, 3, 8, 4), (0, 8, 0, 7), (9, 7, 7, 6), (0, 1, 2, 2)],
    # 起马局（以逸待劳）
    [(9, 1, 7, 2), (3, 6, 4, 6), (6, 2, 5, 2), (0, 7, 2, 6),
     (9, 6, 7, 4), (0, 1, 2, 2), (9, 7, 7, 6), (0, 8, 0, 7)],
    # 中炮对单提马（黑方走边马，变化少而扎实）
    [(7, 7, 7, 4), (0, 1, 2, 0), (9, 7, 7, 6), (0, 7, 2, 6),
     (9, 8, 9, 7), (0, 8, 0, 7), (6, 6, 5, 6), (3, 2, 4, 2)],
]

_OPENING_BOOK = None


def opening_book():
    """把 OPENING_LINES 展开成「局面指纹 → 可走着法表」。第一次用到时建一次。"""
    global _OPENING_BOOK
    if _OPENING_BOOK is not None:
        return _OPENING_BOOK
    book = {}
    for line in OPENING_LINES:
        board = dict(FULL_OPENING)
        turn = RED
        for mv in line:
            piece = board.get((mv[0], mv[1]))
            if piece is None or piece[0] != turn:
                break
            if mv not in legal_moves(board, turn):
                break
            key = board_hash(board, turn)
            slot = book.setdefault(key, [])
            if mv not in slot:
                slot.append(mv)
            board = apply_move(board, *mv)
            turn = opponent(turn)
    _OPENING_BOOK = book
    return book


def book_move(board, color, banned=()):
    """查开局库：命中就返回一个着法，没命中返回 None。
    同一局面有多路谱着时随机挑一个，每局开法不重样。"""
    slot = opening_book().get(board_hash(board, color))
    if not slot:
        return None
    usable = [mv for mv in slot if mv not in banned]
    if not usable:
        return None
    if len(usable) == 1:
        return usable[0]
    return usable[0] if random.random() < 0.6 else random.choice(usable[1:])


def _reset_ext_budget():
    """每一层迭代加深重新发放「将军延伸」额度，免得同一局限死三层"""
    global _ext_left
    _ext_left = EXT_BUDGET


def _reset_search_tables():
    """每步开局前整理搜索表：置换表别无限涨，历史分衰减，杀手表清空"""
    if len(_TT) > _TT_LIMIT:
        _TT.clear()
    if len(_HISTORY) > 30000:
        _HISTORY.clear()
    else:
        # 历史分半衰：上一步的例子仅供参考，新近抢到 beta 的着法更有说服力
        for mv in _HISTORY:
            _HISTORY[mv] //= 2
    _KILLERS.clear()
    _REP_STACK.clear()          # 重复局面栈只活在一次搜索里
    _reset_ext_budget()


def _pick_safest(board, color, moves):
    """候选里挑一手最不亏的：走完按评估分取对我方最好的那步。
    只在搜索没能交出着法时兜底用——总比按着法生成顺序随手抓一个强。"""
    best, best_v = None, None
    sign = 1 if color == RED else -1
    for mv in moves:
        try:
            child = apply_move(board, mv[0], mv[1], mv[2], mv[3])
        except (KeyError, IndexError):
            continue
        v = evaluate(child) * sign
        if best_v is None or v > best_v:
            best, best_v = mv, v
    return best if best is not None else (moves[0] if moves else None)


def long_check_move(board, turn, rep_counts, pos_log, move):
    """走这一着会不会让自己被判「长将判负」——判定口径与裁判完全一致：
    同一局面第 3 次出现，且这一轮循环里自己每一着都在将军。"""
    child = apply_move(board, move[0], move[1], move[2], move[3])
    enemy = opponent(turn)
    key = position_key(child, enemy)
    cnt = rep_counts.get(key, 0) + 1
    if cnt < REPEAT_BLOCK:
        return False
    log = list(pos_log)
    log.append({"key": key, "mover": turn, "check": in_check(child, enemy)})
    verdict = repeat_cycle_verdict(log, key, turn, enemy, cnt)
    return bool(verdict and verdict[0] == "long_check" and verdict[2] == enemy)


def avoid_self_long_check(board, turn, rep_counts, pos_log, move, moves=None):
    """电脑落子前的最后一道保险：这一手若会把自己走成「长将判负」，换成别的着法。
    搜索侧已经禁过长将，这里是双保险 —— 万一禁走逻辑因为「无着可变」退了让，
    也不会真的把一盘好棋白送出去。只有确实还有别的着法时才换。"""
    if move is None or not long_check_move(board, turn, rep_counts, pos_log, move):
        return move
    pool = [mv for mv in (legal_moves(board, turn) if moves is None else moves)
            if (mv[0], mv[1], mv[2], mv[3]) != (move[0], move[1], move[2], move[3])
            and not long_check_move(board, turn, rep_counts, pos_log, mv)]
    if not pool:
        return move                       # 真无着可变，只能这样走
    return _pick_safest(board, turn, pool)


def ai_best_move(board, color, level=2, budget=None, banned=None):
    """迭代加深：在时间预算内尽量深搜，超时则沿用上一层结果。
    banned 为根层禁走的着法（例如会造成重复局面的着法），会被排除在候选之外；
    若禁走后无子可走，则自动放弃禁用，保证总能走出一步。"""
    global _deadline, _node_count, _ROOT_BANNED, _last_depth
    candidates = legal_moves(board, color)
    if not candidates:
        return None
    banned = frozenset(banned or ())
    if banned:
        free = [mv for mv in candidates if mv not in banned]
        if free:
            candidates = free
        else:
            banned = frozenset()

    if random.random() < BLUNDER_RATE.get(level, 0.0):
        return random.choice(candidates)

    # 看得见的杀就先杀：残局里搜索未必能在预算内算到将死，这一手是白拿的。
    # 简单难度不给（新手要留破绽），其余档位都走这一条。
    if level >= 2:
        kill = find_mate_in_one(board, color)
        if kill is not None and kill not in banned:
            _last_depth = max(_last_depth, 1)
            return kill

    # 开局照着谱走：省时间、不跑偏。「简单」难度故意不查库，留点破绽给新手。
    if level >= 2:
        bm = book_move(board, color, banned)
        if bm is not None:
            return bm

    if budget is None:
        budget = DIFFICULTY_BUDGET.get(level, 1.0)

    best = None
    _reset_search_tables()
    _REP_STACK[board_hash(board, color)] = 1      # 根局面进栈，往下才有「重复」可比
    _node_count = 0
    _ROOT_BANNED = banned
    _deadline = time.perf_counter() + budget
    prev_val = None
    try:
        for depth in range(1, level + 1):
            _reset_ext_budget()
            # 渴望窗口：先用「上一层分值 ±ASP_WIN」的窄窗搜，命不中再全窗口重搜。
            # 局面平稳时窄窗能省掉大量节点，把这些时间换成更深的层数。
            lo, hi = -math.inf, math.inf
            narrow = (ASP_WIN is not None and prev_val is not None and depth >= 3)
            if narrow:
                lo, hi = prev_val - ASP_WIN, prev_val + ASP_WIN
            val, move = minimax(board, depth, lo, hi, color == RED)
            if narrow and (val <= lo or val >= hi):
                val, move = minimax(board, depth, -math.inf, math.inf, color == RED)
            if move is not None:
                best = move
                _last_depth = depth
                prev_val = val
    except _SearchTimeout:
        pass
    finally:
        _deadline = None
        _ROOT_BANNED = frozenset()
        _REP_STACK.clear()

    if best in banned:
        best = None
    if best is None:
        # 兜底：不按着法生成顺序随手抓一个，而是比一比谁最不亏
        best = _pick_safest(board, color, candidates)
    return best

_AI_LOCK = threading.Lock()


class AiJob:
    """把一次 AI 搜索放到后台线程：主循环照常以 60 帧绘制，
    轮走箭头、倒计时都不会卡；算完把着法交回主线程执行，避免跨线程改棋盘。"""

    def __init__(self, board, color, level, banned=None, budget=None):
        self.result = None
        self.error = None
        self.done = False
        self.started = time.perf_counter()
        self.finished = None
        self._board = dict(board)
        self._color = color
        self._level = level
        self._banned = banned
        self._budget = budget
        self.thread = threading.Thread(target=self._run, daemon=True,
                                       name="xiangqi-ai")

    def start(self):
        _AI_STATE["cancel"] = False
        self.thread.start()
        return self

    def _run(self):
        global _PUMP_IN_SEARCH
        with _AI_LOCK:
            _AI_STATE["busy"] = True
            _PUMP_IN_SEARCH = False       # 后台线程里不能碰 SDL
            try:
                self.result = ai_best_move(self._board, self._color, self._level,
                                           budget=self._budget, banned=self._banned)
            except Exception as exc:      # 线程里的异常不能静默吞掉
                self.error = exc
            finally:
                self.finished = time.perf_counter()
                _PUMP_IN_SEARCH = True
                _AI_STATE["busy"] = False
                self.done = True

    def cancel(self, timeout=1.2):
        """叫停并等它退出：搜索每 128 个节点查一次取消位，通常几十毫秒就停"""
        _AI_STATE["cancel"] = True
        if self.thread.is_alive():
            self.thread.join(timeout)
        _AI_STATE["cancel"] = False
        return not self.thread.is_alive()

    @property
    def alive(self):
        return self.thread.is_alive()


# ---------------------------- 音效合成 ----------------------------
SAMPLE_RATE = 44100


def _build_wave(segments, volume=0.5, noise=0.0):
    """按 (频率, 时长, 衰减系数) 列表合成 16bit 双声道 PCM 数据。

    noise 为噪声占比，用来做出木质敲击感；频率为 0 时纯噪声。
    """
    buf = array("h")
    for freq, dur, decay in segments:
        n = max(1, int(SAMPLE_RATE * dur))
        for i in range(n):
            t = i / SAMPLE_RATE
            env = math.exp(-decay * t)
            if freq:
                sample = math.sin(2 * math.pi * freq * t)
                sample += 0.35 * math.sin(4 * math.pi * freq * t)
            else:
                sample = 0.0
            if noise:
                sample = (1 - noise) * sample + noise * (random.random() * 2 - 1)
            value = int(max(-1.0, min(1.0, sample * env * volume)) * 32767)
            buf.append(value)
            buf.append(value)
    return buf.tobytes()


AUDIO_EXTS = (".wav", ".ogg", ".mp3")
SFX_DIR = "音效"           # 放 select.wav / 落子.wav 这类，同名即替换内置音效
MUSIC_DIR = "曲"           # 放 高山流水.ogg 这类，同名即替换内置古曲
SFX_ALIASES = {
    "select": ("选中",), "move": ("落子",), "capture": ("吃子",),
    "check": ("将军",), "win": ("胜利",), "lose": ("失败",),
    "illegal": ("误操作",),
}
_MUSIC_CACHE = {}


def extern_files_dir():
    """安卓的外部可写目录：/sdcard/Android/data/org.songyq.xiangqi/files。
    放曲目、音效、背景图都行——数据线连电脑或者文件管理能直接拷进去，不用申请权限。
    非安卓返回 None。"""
    if not IS_ANDROID:
        return None
    ext = os.environ.get("EXTERNAL_STORAGE") or "/storage/emulated/0"
    d = os.path.join(ext, "Android", "data", "org.songyq.xiangqi", "files")
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d if os.path.isdir(d) else None


def _audio_bases():
    """找 音效 / 曲 目录的位置：手机外部可写目录排在前面（自己拷进去的最优先），
    然后是程序目录、解包目录，以及它们的上一级
    （exe 放在 dist 里时，把 曲 目录摆在 dist 上一层同样能被找到）"""
    bases = []
    cands = [extern_files_dir(), _BASE_DIR, _res_dir(),
             os.path.dirname(_BASE_DIR)]
    for base in cands:
        if base and base not in bases and os.path.isdir(base):
            bases.append(base)
    return bases


def find_audio(folder, names):
    """在 音效 / 曲 目录里按名找音频文件（wav / ogg / mp3），找不到返回 None"""
    for base in _audio_bases():
        d = os.path.join(base, folder)
        if not os.path.isdir(d):
            continue
        for nm in names:
            for ext in AUDIO_EXTS:
                path = os.path.join(d, nm + ext)
                if os.path.exists(path):
                    return path
    return None


def music_library():
    """扫 曲 目录：返回音频名（去扩展名、去重、按名字排序）。
    放进去就出现、删掉就消失，不用改代码。"""
    names = []
    for base in _audio_bases():
        d = os.path.join(base, MUSIC_DIR)
        if not os.path.isdir(d):
            continue
        try:
            files = sorted(os.listdir(d))
        except OSError:
            continue
        for fn in files:
            stem, ext = os.path.splitext(fn)
            stem = stem.strip()
            if ext.lower() in AUDIO_EXTS and stem and stem not in names:
                names.append(stem)
    return names


def has_music_file(name):
    """该曲目是否有真实音频文件（否则用内置合成旋律）"""
    return find_audio(MUSIC_DIR, (name,)) is not None


def bgm_names():
    """可选曲目：曲 目录里的真音频在前（好认），内置合成古曲在后作为兜底"""
    names = music_library()
    for nm in BGM_CORE:
        if nm not in names:
            names.append(nm)
    return names


def load_user_music(name):
    """曲 目录里若有同名音频，就用它循环播放，否则用内置合成古曲"""
    if name in _MUSIC_CACHE:
        return _MUSIC_CACHE[name]
    snd = None
    path = find_audio(MUSIC_DIR, (name,))
    if path:
        try:
            snd = pygame.mixer.Sound(path)
        except (pygame.error, OSError):
            snd = None
    _MUSIC_CACHE[name] = snd
    return snd


def build_sounds():
    sounds = {
        # 选中棋子：轻微高频短音
        "select": pygame.mixer.Sound(buffer=_build_wave([(1100, 0.045, 70)], 0.20)),
        # 落子：木质感敲击。做三个音高，按落点高低挑一个 —— 上三路清脆、下三路低沉，
        # 听着像真在木盘上落子（外置 音效\move.wav 存在时三个变体都用文件里的声音）
        "move": pygame.mixer.Sound(buffer=_build_wave([(520, 0.07, 45)], 0.42, noise=0.55)),
        "move_a": pygame.mixer.Sound(buffer=_build_wave([(566, 0.07, 45)], 0.40, noise=0.55)),
        "move_b": pygame.mixer.Sound(buffer=_build_wave([(520, 0.07, 45)], 0.42, noise=0.55)),
        "move_c": pygame.mixer.Sound(buffer=_build_wave([(472, 0.08, 45)], 0.44, noise=0.52)),
        # 吃子：更低更厚
        "capture": pygame.mixer.Sound(buffer=_build_wave([(260, 0.13, 26)], 0.58, noise=0.72)),
        # 将军：三声提示
        "check": pygame.mixer.Sound(
            buffer=_build_wave([(760, 0.08, 18), (1020, 0.09, 14), (760, 0.11, 14)], 0.45)),
        # 胜利：上行音阶
        "win": pygame.mixer.Sound(
            buffer=_build_wave([(523, 0.11, 12), (659, 0.11, 12),
                                (784, 0.11, 12), (1047, 0.22, 8)], 0.45)),
        # 失败 / 超时：下行音阶
        "lose": pygame.mixer.Sound(
            buffer=_build_wave([(392, 0.13, 12), (330, 0.13, 12), (262, 0.26, 8)], 0.45)),
        # 误操作：低沉闷响
        "illegal": pygame.mixer.Sound(buffer=_build_wave([(150, 0.10, 30)], 0.35, noise=0.6)),
    }
    # 外置替换：音效\move.wav（或 音效\落子.wav）存在就用文件里的声音
    for key in list(sounds):
        path = find_audio(SFX_DIR, (key,) + SFX_ALIASES.get(key, ()))
        if not path:
            continue
        try:
            sounds[key] = pygame.mixer.Sound(path)
        except (pygame.error, OSError):
            pass
    # 换了落子声，三个音高变体也一起换，不然只有一部分落子是新声音
    move_snd = sounds.get("move")
    for key in ("move_a", "move_b", "move_c"):
        sounds[key] = move_snd
    return sounds


SOUND_NAMES = ("select", "move", "move_a", "move_b", "move_c",
                "capture", "check", "win", "lose", "illegal")


def play(sounds, name):
    snd = sounds.get(name)
    if snd is not None:
        snd.play()


# ---------------------------- 坐标与界面绘制 ----------------------------
def board_to_pixel(r, c):
    return MARGIN + c * CELL, BOARD_ORIGIN_Y + MARGIN + r * CELL


def pixel_to_board(x, y):
    c = int(round((x - MARGIN) / CELL))
    r = int(round((y - BOARD_ORIGIN_Y - MARGIN) / CELL))
    if not in_board(r, c):
        return None
    px, py = board_to_pixel(r, c)
    if abs(x - px) <= CELL * 0.48 and abs(y - py) <= CELL * 0.48:
        return r, c
    return None


def pixel_to_board_snap(x, y):
    """拖动落子用：范围放宽一点并吸附到最近的交叉点，
    手指 / 鼠标松开时差几像素也算落在这个点上。"""
    c = int(round((x - MARGIN) / CELL))
    r = int(round((y - BOARD_ORIGIN_Y - MARGIN) / CELL))
    if not in_board(r, c):
        return None
    px, py = board_to_pixel(r, c)
    if abs(x - px) <= CELL * 0.62 and abs(y - py) <= CELL * 0.62:
        return r, c
    return None


def draw_rect(screen, color, rect, width=0, radius=10):
    try:
        pygame.draw.rect(screen, color, rect, width, border_radius=radius)
    except TypeError:                       # 老版本 pygame 不支持圆角
        pygame.draw.rect(screen, color, rect, width)


def draw_text_center(screen, text, cx, cy, font, color):
    surf = font.render(text, True, color)
    screen.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))


def draw_spaced_text(screen, text, cx, cy, font, color, gap=10):
    surfs = [font.render(ch, True, color) for ch in text]
    total = sum(s.get_width() for s in surfs) + gap * (len(surfs) - 1)
    x = cx - total / 2
    for s in surfs:
        screen.blit(s, (x, cy - s.get_height() / 2))
        x += s.get_width() + gap


def fit_text(text, font, max_w, color):
    """超宽就截断并补省略号（返回 Surface，长度不会溢出 max_w）"""
    text = str(text or "")
    if font.size(text)[0] <= max_w:
        return font.render(text, True, color)
    cut = text
    while cut and font.size(cut + "…")[0] > max_w:
        cut = cut[:-1]
    return font.render((cut + "…") if cut else "", True, color)


# 兵位、炮位的十字标记
MARKS = [
    (2, 1), (2, 7), (7, 1), (7, 7),
    (3, 0), (3, 2), (3, 4), (3, 6), (3, 8),
    (6, 0), (6, 2), (6, 4), (6, 6), (6, 8),
]

PIECE_R = 26              # 棋子半径（格距 60，两侧各留 4px 空隙）
_BOARD_LAYER = {}         # 主题 -> 画好的整块棋盘（含木纹、线、路数），每帧只 blit
_PIECE_CACHE = {}         # (主题, 颜色, 兵种, 半径) -> 预渲染好的立体棋子
_SHADOW_CACHE = {}        # (主题, 半径) -> 棋子投影


def board_to_layer(r, c):
    """棋盘层内坐标（棋盘层贴在 BOARD_ORIGIN_Y 处，省掉屏幕的纵向偏移）"""
    return MARGIN + c * CELL, MARGIN + r * CELL


def draw_board(screen):
    """棋盘整块缓存：木纹、横竖线、九宫、兵炮位、路数、楚河汉界一次画好，
    之后每帧只 blit 一次 —— 省下的时间用来加立体细节，帧率反而更高。"""
    screen.fill(BG_COLOR)
    screen.blit(board_layer(), (0, BOARD_ORIGIN_Y))


def board_layer():
    key = THEME_CURRENT
    surf = _BOARD_LAYER.get(key)
    if surf is not None:
        return surf
    surf = pygame.Surface((SCREEN_W, BOARD_PX_H))
    dark = key == "墨玉"
    base = TH["bg"]
    ink = _mix(base, (255, 255, 255) if dark else (0, 0, 0), 0.16)

    # 底：上深下浅的柔和渐变，像一块被窗光照着的木板
    for y in range(BOARD_PX_H):
        t = y / float(BOARD_PX_H)
        surf.fill(_mix(_mix(base, ink, 0.10), base, t), pygame.Rect(0, y, SCREEN_W, 1))

    # 木纹：几条起伏极缓的长线，几乎看不见，只让大面积平色活起来
    rnd = random.Random(20261102)
    grain = _mix(base, ink, 0.55)
    for _ in range(22):
        y0 = rnd.randrange(-10, BOARD_PX_H + 10)
        amp = rnd.uniform(2.0, 6.5)
        freq = rnd.uniform(0.010, 0.026)
        phase = rnd.uniform(0, 6.283)
        pts = [(x, y0 + amp * math.sin(freq * x + phase))
               for x in range(0, SCREEN_W + 1, 10)]
        pygame.draw.lines(surf, grain, False, pts, 1)

    left, top = board_to_layer(0, 0)
    right, bottom = board_to_layer(BOARD_ROWS - 1, BOARD_COLS - 1)
    width = right - left
    height = bottom - top
    river_y = top + 4 * CELL

    # 棋盘外的一圈护板：外深内浅，做出「棋盘嵌在木框里」的层次
    frame = pygame.Rect(left - 20, top - 20, width + 40, height + 40)
    pygame.draw.rect(surf, _mix(base, ink, 0.30), frame, 0, 6)
    pygame.draw.rect(surf, _mix(base, ink, 0.16), frame.inflate(-6, -6), 0, 5)
    pygame.draw.rect(surf, _mix(base, (255, 255, 255) if dark else (255, 255, 240), 0.12),
                     frame, 1, 6)

    # 十条横线
    for r in range(BOARD_ROWS):
        y = top + r * CELL
        pygame.draw.line(surf, BOARD_LINE, (left, y), (right, y), 1)

    # 九条竖线：两侧外框贯通，中间七路在河界处断开
    for c in range(BOARD_COLS):
        x = left + c * CELL
        if c in (0, BOARD_COLS - 1):
            pygame.draw.line(surf, BOARD_LINE, (x, top), (x, bottom), 1)
        else:
            pygame.draw.line(surf, BOARD_LINE, (x, top), (x, river_y), 1)
            pygame.draw.line(surf, BOARD_LINE, (x, river_y + CELL), (x, bottom), 1)

    # 九宫斜线
    for r1, c1, r2, c2 in ((0, 3, 2, 5), (0, 5, 2, 3), (7, 3, 9, 5), (7, 5, 9, 3)):
        pygame.draw.line(surf, BOARD_LINE, board_to_layer(r1, c1),
                         board_to_layer(r2, c2), 1)

    # 外框加粗，外面再压一道浅色细线，像木框的倒角
    pygame.draw.rect(surf, BOARD_LINE,
                     pygame.Rect(left - 5, top - 5, width + 10, height + 10), 3)
    pygame.draw.rect(surf, _mix(BOARD_LINE, (255, 255, 255), 0.45),
                     pygame.Rect(left - 8, top - 8, width + 16, height + 16), 1)

    # 兵位、炮位标记
    for r, c in MARKS:
        x, y = board_to_layer(r, c)
        for dx in (-1, 1):
            for dy in (-1, 1):
                if (c == 0 and dx < 0) or (c == BOARD_COLS - 1 and dx > 0):
                    continue
                sx, sy = x + dx * 7, y + dy * 7
                pygame.draw.line(surf, BOARD_LINE, (sx, sy), (sx + dx * 11, sy), 1)
                pygame.draw.line(surf, BOARD_LINE, (sx, sy), (sx, sy + dy * 11), 1)

    # 河界：一条淡色水带 + 中间两句「楚河」「汉界」
    band = pygame.Surface((width, CELL), pygame.SRCALPHA)
    band.fill(_mix(base, (120, 170, 190) if dark else (150, 200, 220), 0.14) + (70,))
    surf.blit(band, (left, river_y + 1))
    river_font = load_font(26)
    draw_spaced_text(surf, "楚河", left + 2 * CELL, river_y + CELL / 2,
                     river_font, RIVER_COLOR, 14)
    draw_spaced_text(surf, "汉界", left + 6 * CELL, river_y + CELL / 2,
                     river_font, RIVER_COLOR, 14)

    # 路数：上为黑方 1-9（自左向右），下为红方 九-一
    num_font = load_font(15)
    red_files = ["九", "八", "七", "六", "五", "四", "三", "二", "一"]
    label_top_cy = max(10, (top - 26) // 2)
    label_bottom_cy = min(BOARD_PX_H - 10, (bottom + 26 + BOARD_PX_H) // 2)
    for c in range(BOARD_COLS):
        x = left + c * CELL
        draw_text_center(surf, str(c + 1), x, label_top_cy, num_font, TH["label"])
        draw_text_center(surf, red_files[c], x, label_bottom_cy, num_font,
                         TH["accent_red"])

    _BOARD_LAYER[key] = surf
    return surf


def piece_surface(color, piece, radius=None):
    """预渲染一枚立体棋子：球面渐变 + 左上高光 + 两道圈 + 字带亮边。
    同一枚棋子每帧只 blit 一次，画多少次都不掉帧。"""
    radius = radius or PIECE_R
    key = (THEME_CURRENT, color, piece, radius)
    surf = _PIECE_CACHE.get(key)
    if surf is not None:
        return surf

    size = radius * 2 + 10
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size / 2.0
    face = TH["piece_face"]
    edge = TH["piece_edge"]
    hi = _mix(face, (255, 255, 255), 0.62)
    lo = _mix(face, edge, 0.52)

    # 球面：一圈圈往里画，越靠中心越亮，整圈再往左上偏一点
    steps = max(10, radius)
    for i in range(steps, 0, -1):
        t = i / float(steps)
        col = _mix(hi, lo, t ** 0.80)
        ox = -(radius * 0.09) * (1.0 - t)
        oy = -(radius * 0.12) * (1.0 - t)
        pygame.draw.circle(surf, col, (int(cx + ox), int(cy + oy)),
                           max(1, int(radius * t)))

    # 左上高光斑
    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 92),
                        pygame.Rect(int(cx - radius * 0.58), int(cy - radius * 0.80),
                                    int(radius * 1.16), int(radius * 0.74)))
    surf.blit(hl, (0, 0))

    # 外描边（下沿更深，模拟厚度）+ 内圈 + 兵种环
    pygame.draw.circle(surf, _mix(edge, (0, 0, 0), 0.18), (int(cx), int(cy) + 1),
                       radius, 2)
    pygame.draw.circle(surf, _mix(edge, (255, 255, 255), 0.30), (int(cx), int(cy)),
                       int(radius * 0.84), 1)
    ring = (176, 44, 44) if color == RED else (46, 46, 54)
    pygame.draw.circle(surf, ring, (int(cx), int(cy)), int(radius * 0.70), 2)

    # 字：先垫一层亮边，再从原位压上主色，暗底上也能看清
    name = CHINESE_PIECES.get((color, piece), "?")
    font = load_font_song(max(11, int(radius * 1.00)))
    glyph = font.render(name, True, ring)
    light = font.render(name, True, (255, 255, 255))
    light.set_alpha(150)
    gx = int(cx - glyph.get_width() / 2)
    gy = int(cy - glyph.get_height() / 2)
    surf.blit(light, (gx + 1, gy + 1))
    surf.blit(glyph, (gx, gy))

    _PIECE_CACHE[key] = surf
    return surf


def piece_shadow(radius=None):
    """棋子投影：几层很淡的同心圆，落点偏右下，看着像搁在棋盘上"""
    radius = radius or PIECE_R
    key = (THEME_CURRENT, radius)
    surf = _SHADOW_CACHE.get(key)
    if surf is not None:
        return surf
    size = radius * 2 + 16
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    dark = TH["piece_shadow"]
    col = (int(dark[0] * 0.45), int(dark[1] * 0.45), int(dark[2] * 0.45))
    for i in range(4, 0, -1):
        pygame.draw.circle(surf, col + (14 + 10 * (4 - i),), (size // 2, size // 2),
                           radius + i)
    _SHADOW_CACHE[key] = surf
    return surf


def draw_pieces(screen, board, selected, checked=(), skip=(), flying=None):
    """画棋子。selected 会轻轻抬起并加绿环；checked 里的将帅闪红环。
    skip：这些格子不画（正在滑行 / 被拖动的棋子由调用方单独画）。
    flying：(棋子, 屏幕 x, 屏幕 y, 缩放) 用于走子动画与拖动。"""
    shadow = piece_shadow()
    half_sh = shadow.get_width() // 2
    base = piece_surface(RED, PAWN)
    half = base.get_width() // 2

    for (r, c), (pc, pt) in board.items():
        if (r, c) in skip:
            continue
        x, y = board_to_pixel(r, c)
        up = 3 if selected == (r, c) else 0          # 选中的子轻轻抬起
        screen.blit(shadow, (x - half_sh + 2, y - half_sh + 5 + up // 2))
        screen.blit(piece_surface(pc, pt), (x - half, y - half - up))
        if selected == (r, c):
            pygame.draw.circle(screen, (24, 150, 96), (x, y - up), PIECE_R + 4, 3)
        if (r, c) in checked:                        # 被将军的将/帅：红环闪动
            phase = (pygame.time.get_ticks() // 220) % 2
            pygame.draw.circle(screen, (226, 62, 48) if phase else (176, 36, 30),
                               (x, y - up), PIECE_R + 5, 3)

    if flying is not None:
        pc, pt = flying[0], flying[1]
        fx, fy = flying[2], flying[3]
        scale = flying[4] if len(flying) > 4 else 1.0
        surf = piece_surface(pc, pt)
        if abs(scale - 1.0) > 0.02:
            nw = max(6, int(surf.get_width() * scale))
            surf = pygame.transform.smoothscale(surf, (nw, nw))
        screen.blit(shadow, (fx - half_sh + 2, fy - half_sh + 5))
        screen.blit(surf, (fx - surf.get_width() // 2, fy - surf.get_height() // 2))


def fmt_time(seconds):
    seconds = max(0, int(math.ceil(seconds - 1e-6)))
    return "%02d:%02d" % (seconds // 60, seconds % 60)


def control_hitboxes():
    """顶栏按钮区域，返回 [(Rect, (类型, 名称))]。
    手机版把四档难度合成一个「难度·xx」按钮（点一下换一档），
    换来的宽度给摆棋 / 残局 / 音效 / 音乐 / 单步，手指点得准。
    音乐开关按用户要求从底栏挪到音效旁边，底栏因此少一格、每格更宽。"""
    boxes = []
    if UI_BIG:
        x, y, h = 8, 4, 32
        for w, kind in ((112, "diff_cycle"), (68, "edit"), (68, "lib"),
                        (74, "sound"), (74, "music"), (90, "move")):
            boxes.append((pygame.Rect(x, y, w, h), (kind, None)))
            x += w + 6
        return boxes
    x = 48
    for label, _depth in DIFFICULTY_LEVELS:
        boxes.append((pygame.Rect(x, 7, 44, 26), ("diff", label)))
        x += 48
    boxes.append((pygame.Rect(242, 7, 58, 26), ("edit", None)))
    boxes.append((pygame.Rect(306, 7, 64, 26), ("lib", None)))
    # 「存局」在底部按钮栏（对战 / 残局 / 摆棋都能存），顶部不再重复放一个
    boxes.append((pygame.Rect(376, 7, 58, 26), ("sound", None)))
    boxes.append((pygame.Rect(440, 7, 58, 26), ("music", None)))
    # 单步限时：对局中直接点就能在 不限 / 15 / 30 / 60 秒 之间轮换
    boxes.append((pygame.Rect(504, 7, 62, 26), ("move", None)))
    return boxes


def draw_control_bar(screen, difficulty, sound_on, editing=False, move_limit=0,
                     music_on=True):
    pygame.draw.rect(screen, TH["panel_bg"], pygame.Rect(0, 0, SCREEN_W, CONTROL_H))
    pygame.draw.line(screen, TH["panel_line"], (0, CONTROL_H - 1),
                     (SCREEN_W, CONTROL_H - 1), 1)

    font = load_font(15 if UI_BIG else 14)
    if not UI_BIG:
        hint = font.render("难度", True, C((112, 98, 80)))
        screen.blit(hint, (10, (CONTROL_H - hint.get_height()) // 2))

    for rect, (kind, label) in control_hitboxes():
        tone = C((34, 150, 96))
        if kind == "diff":
            text, active = label, difficulty == label
        elif kind == "diff_cycle":
            text, active = "难度·" + difficulty, True
        elif kind == "edit":
            text, active = ("摆棋中" if editing else "摆棋"), editing
        elif kind == "lib":
            text, active = "残局", False
        elif kind == "move":
            text = "步限" + ("不限" if int(move_limit) <= 0 else str(int(move_limit)))
            active = int(move_limit) > 0
        elif kind == "music":
            text, active = ("音乐开" if music_on else "音乐关"), music_on
            tone = C((52, 96, 150))
        elif kind == "sound":
            text, active = ("音效开" if sound_on else "音效关"), sound_on
        else:
            text, active = "保存", False
        draw_button_face(screen, rect,
                         tone if active else C((250, 246, 238)),
                         tone if active else C((196, 186, 170)),
                         radius=8, active=active)
        surf = font.render(text, True, C((255, 255, 255)) if active else TH["btn_text"])
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))


def _mix(c1, c2, t):
    """两色按 t(0~1) 混合，用于压暗 / 提亮轨道这类细节"""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


MOVE_LIMIT_LABELS = {0: "不限", 15: "15 秒", 30: "30 秒", 60: "60 秒"}
CLOCK_R = 26              # 圆表半径兜底值（实际按面板高度算，见 clock_radius）
CLOCK_URGENT = 10         # 剩这么多秒就转红并闪烁
CLOCK_BLINK_MS = 400      # 闪烁半周期：一亮一暗共 0.8 秒，够醒目又不晃眼
AI_MIN_THINK = 0.45      # 电脑最少「想」这么久：太快会看不清走子动画


def move_limit_label(sec):
    """单步限时的中文档位名（0 表示不限时）"""
    sec = int(sec or 0)
    return MOVE_LIMIT_LABELS.get(sec, "%d 秒" % sec)


def clock_radius(rect):
    """圆表半径：比面板内框小一圈（左右各留 3px）——黑方面板高 50 取 22，红方高 58 取 26"""
    return max(14, rect.height // 2 - 3)


def move_clock_center(rect, side=RED):
    """圆表横向与中路（将帅所在的第 5 路）对齐、纵向在面板里居中：
    红方面板紧贴棋盘下沿，表就落在帅的正下方；黑方面板紧贴上沿，表落在将的正上方。"""
    return rect.centerx, rect.centery


def clock_blink_on():
    """剩 10 秒内的闪烁节拍，绘制与自检共用一套"""
    return (pygame.time.get_ticks() // CLOCK_BLINK_MS) % 2 == 0


def draw_move_clock(screen, center, radius, elapsed, limit, accent):
    """单步计时圆表：表圈 + 12 道刻度 + 指针，圈心写这一手还剩几秒。
    limit > 0：指针一圈走完这一手的限时，表圈上的弧表示剩余时间，剩 10 秒内转红；
               进入 10 秒后整块表（弧、表圈、刻度、秒数）红暗交替闪烁。
    limit = 0（不限时）：指针 60 秒转一圈，圈心写这一手已经用了多久。"""
    cx, cy = int(center[0]), int(center[1])
    r = int(radius)
    hot = (214, 66, 54)
    left = max(0.0, float(limit) - elapsed) if limit > 0 else 0.0
    urgent = bool(limit > 0 and left <= CLOCK_URGENT)
    on = (not urgent) or clock_blink_on()      # 未进入 10 秒：一直亮着

    if urgent:                                  # 着急了：底色、表圈、刻度一起跟着闪
        face = _mix(TH["panel_fill"], hot, 0.22 if on else 0.00)
        ring = _mix(TH["panel_fill"], hot, 0.85 if on else 0.12)
        col = hot if on else _mix(hot, TH["panel_fill"], 0.72)
    else:
        face = _mix(TH["panel_fill"], accent, 0.10)
        ring = _mix(TH["panel_fill"], accent, 0.70)
        col = accent
    plate = _mix(TH["panel_fill"], (255, 255, 255), 0.75)

    pygame.draw.circle(screen, face, (cx, cy), r)
    pygame.draw.circle(screen, ring, (cx, cy), r, 3 if (urgent and on) else 2)
    for i in range(12):                         # 12 道刻度：整点那四根长一些
        ang = math.pi / 2 - i * math.pi / 6
        ln = 5 if i % 3 == 0 else 3
        pygame.draw.line(screen, ring,
                         (cx + (r - 5 - ln) * math.cos(ang),
                          cy - (r - 5 - ln) * math.sin(ang)),
                         (cx + (r - 5) * math.cos(ang),
                          cy - (r - 5) * math.sin(ang)), 1)

    if limit > 0:
        used = 1.0 - left / float(limit)
        if used > 0.004:                        # 剩余时间弧：指针到 12 点之间那一段
            box = pygame.Rect(cx - r + 1, cy - r + 1, 2 * r - 2, 2 * r - 2)
            pygame.draw.arc(screen, col, box, math.pi / 2 - 2 * math.pi * used,
                            math.pi / 2, 3)
        text = "%d" % int(math.ceil(left - 1e-6))
    else:
        used = (elapsed % 60.0) / 60.0
        text = "%d" % min(99, int(elapsed))

    # 圈心的数字盘：先铺一层浅色圆，秒数才不会被指针压糊
    pr = r - 10
    pygame.draw.circle(screen, plate, (cx, cy), pr)
    pygame.draw.circle(screen, ring, (cx, cy), pr, 1)
    # 圈心是浅色底盘，秒数统一用「压深的强调色」，两套主题都看得清；
    # 闪烁时只让表圈和弧跳，秒数保持常亮，免得一闪就读不到数
    dcol = _mix(hot if urgent else col, (36, 30, 28), 0.45 if urgent else 0.62)
    num = None
    for size in (17, 15, 13, 11):
        num = load_font(size).render(text, True, dcol)
        if num.get_width() <= 2 * pr - 2 and num.get_height() <= 2 * pr - 2:
            break
    screen.blit(num, (cx + 1 - num.get_width() // 2, cy + 1 - num.get_height() // 2))

    ang = math.pi / 2 - 2 * math.pi * used
    pygame.draw.line(screen, col,
                     (cx + (pr + 1) * math.cos(ang), cy - (pr + 1) * math.sin(ang)),
                     (cx + (r - 5) * math.cos(ang), cy - (r - 5) * math.sin(ang)), 3)


def draw_player_panel(screen, rect, label, remain, active, count, side, hint="",
                      move_elapsed=0.0, move_limit=0):
    fill = TH["panel_fill"] if active else TH["panel_idle"]
    edge = C((34, 150, 96)) if active else C((198, 188, 172))
    draw_button_face(screen, rect, fill, edge, radius=10, active=active,
                     border_w=2 if active else 1, highlight=False)

    accent = TH["accent_red"] if side == RED else TH["accent_black"]
    name_font = load_font(19)
    info_font = load_font(15)
    time_font = load_font(26)

    name_y = rect.y + (10 if side == BLACK
                       else max(6, (rect.height - name_font.get_height()) // 2))
    name = name_font.render(label, True, accent if active else TH["muted"])
    screen.blit(name, (rect.x + 14, name_y))
    info = info_font.render("第 %d 手" % count, True, TH["muted"])
    info_x = rect.x + 24 + name.get_width()
    screen.blit(info, (info_x, name_y + 4))

    color = accent if active else TH["muted"]
    if remain <= 30:
        color = C((208, 60, 50))
    txt = time_font.render(fmt_time(remain), True, color)
    time_y = rect.y + (8 if side == BLACK
                       else max(4, (rect.height - txt.get_height()) // 2))
    screen.blit(txt, (rect.right - 16 - txt.get_width(), time_y))

    # 单步计时圆表：只有轮走的一方有表（不走的一方不画），紧挨着他的将/帅
    if not active:
        return
    r = clock_radius(rect)
    cx, cy = move_clock_center(rect, side)
    draw_move_clock(screen, (cx, cy), r, move_elapsed, move_limit, accent)
    if hint:
        tag = info_font.render(hint, True, accent)
        screen.blit(tag, (cx + r + 14, cy - tag.get_height() // 2))


_NO_LINE_START = "。，；、）」』！？·…—：,.;:!?)]}"


def _wrap_tokens(text):
    """折行的切分单位：连续 ASCII 字母数字（含 . _ - /）算一个整体，
    免得 select.wav 被拆成「sel / ect.wav」；其余按单字。"""
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isascii() and (ch.isalnum() or ch in "._-/"):
            j = i
            while j < n and text[j].isascii() and (text[j].isalnum() or text[j] in "._-/"):
                j += 1
            out.append(text[i:j])
            i = j
        else:
            out.append(ch)
            i += 1
    return out


def wrap_text(text, font, max_width):
    """按像素宽度折行；「。，）」这类标点不落在行首，英文单词不拆开"""
    lines, cur = [], ""
    for token in _wrap_tokens(text):
        if font.size(token)[0] > max_width:      # 单个超长英文串：退回逐字拆
            for ch in token:
                if cur and font.size(cur + ch)[0] > max_width:
                    lines.append(cur)
                    cur = ch
                else:
                    cur += ch
            continue
        if not cur or font.size(cur + token)[0] <= max_width:
            cur += token
        elif token in _NO_LINE_START and len(cur) > 1:
            lines.append(cur[:-1])
            cur = cur[-1] + token
        else:
            lines.append(cur)
            cur = token
    if cur:
        lines.append(cur)
    return lines


def draw_scene(screen, board, selected, turn, remain, turn_start, counts,
               message, game_over, difficulty, sound_on, editing=False,
               last_move=None, caption=None, replay_info=None,
               hints=None, result_text=None, music_on=True, move_limit=0,
               anim=None, drag=None, ripple=None):
    draw_board(screen)
    checked = []
    for color in (RED, BLACK):
        king = find_king(board, color)
        if king and in_check(board, color):
            checked.append(king)

    now = time.perf_counter()
    skip = set()
    flying = None
    ease = 1.0
    dx = dy = 0.0

    # 走子滑行：从起点沿一条微抬的弧线滑到落点，吃掉的那枚棋子同时淡出
    if anim is not None:
        dur = anim.get("dur", 0.17)
        t = (now - anim["t0"]) / dur if dur > 0 else 1.0
        if t < 1.0:
            ease = 1.0 - (1.0 - max(0.0, t)) ** 3
            sx, sy = board_to_pixel(anim["fr"], anim["fc"])
            dx, dy = board_to_pixel(anim["tr"], anim["tc"])
            px = sx + (dx - sx) * ease
            py = sy + (dy - sy) * ease - math.sin(ease * math.pi) * 7
            skip.add((anim["tr"], anim["tc"]))
            flying = (anim["piece"][0], anim["piece"][1], px, py,
                      1.0 + 0.05 * math.sin(ease * math.pi))

    # 拖动：把点住的棋子从盘上拿下来，跟着鼠标走
    if drag is not None and drag.get("moved"):
        skip.add((drag["fr"], drag["fc"]))
        flying = (drag["piece"][0], drag["piece"][1],
                  drag["pos"][0], drag["pos"][1], 1.08)

    draw_pieces(screen, board, None if game_over else selected, checked,
                skip=skip, flying=flying)

    if anim is not None and anim.get("victim") and ease < 1.0:
        victim = piece_surface(*anim["victim"])
        victim = victim.copy()
        victim.set_alpha(int(255 * (1.0 - ease)))
        screen.blit(victim, (int(dx - victim.get_width() // 2),
                             int(dy - victim.get_height() // 2)))
    if ripple is not None:
        draw_ripple(screen, ripple[0], ripple[1], ripple[2])

    draw_move_hints(screen, [] if game_over else (hints or []), board)
    draw_move_track(screen, last_move)
    draw_control_bar(screen, difficulty, sound_on, editing, move_limit,
                     music_on=music_on)

    shown = {}
    for color in (RED, BLACK):
        value = remain[color]
        if not game_over and turn == color:
            value = max(0.0, value - (now - turn_start))
        shown[color] = value

    black_rect = player_panel_rect(BLACK)
    red_rect = player_panel_rect(RED)

    def _hint(color):
        if game_over or turn != color:
            return ""
        return "该你走" if color == HUMAN_SIDE else "思考中…"

    elapsed = max(0.0, now - turn_start)
    live = None if game_over else turn          # 终局 / 复盘时谁都不走棋，圆表停笔
    draw_player_panel(screen, black_rect, side_mark(BLACK), shown[BLACK], live == BLACK,
                      counts[BLACK], BLACK, _hint(BLACK), elapsed, move_limit)
    draw_player_panel(screen, red_rect, side_mark(RED), shown[RED], live == RED,
                      counts[RED], RED, _hint(RED), elapsed, move_limit)

    # 提示 / 复盘说明（按钮栏上方）：手机版底部只剩一行的位置，截断显示；
    # 桌面版仍是两行，长的出错说明看得全。
    font = load_font(15)
    text_width = SCREEN_W - 32
    caption_text = caption if caption is not None else message
    if UI_BIG:
        line = fit_text(caption_text, font, text_width, TH["text"])
        screen.blit(line, (16, red_rect.bottom + 3))
    else:
        for i, line in enumerate(wrap_text(caption_text, font, text_width)[:2]):
            surf = font.render(line, True, TH["text"])
            screen.blit(surf, (16, red_rect.bottom + 4 + i * 18))

    if replay_info is not None:
        draw_replay_controls(screen, replay_info[0], replay_info[1], replay_info[2])
    else:
        draw_bottom_buttons(screen, game_over=game_over, music_on=music_on)

    if checked and not game_over:
        draw_check_banner(screen)
    if game_over and result_text:
        draw_result_banner(screen, result_text)


def draw_ripple(screen, r, c, t0):
    """落子涟漪：两圈很快散开的浅绿波纹，给「啪」一下的落子感"""
    t = (time.perf_counter() - t0) / 0.42
    if t >= 1.0 or t < 0:
        return
    x, y = board_to_pixel(r, c)
    for delay in (0.0, 0.20):
        tt = t - delay
        if tt <= 0.0 or tt >= 1.0:
            continue
        rad = int(PIECE_R * (1.05 + 1.15 * tt))
        surf = pygame.Surface((rad * 2 + 6, rad * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, (28, 158, 100, int(110 * (1.0 - tt))),
                           (rad + 3, rad + 3), rad, 2)
        screen.blit(surf, (x - rad - 3, y - rad - 3))


def draw_move_hints(screen, moves, board):
    """可落点提示：空点画绿点，可吃子画红圈"""
    if not moves:
        return
    dot = (46, 160, 104) if THEME_CURRENT == "原木" else (120, 220, 170)
    for fr, fc, tr, tc in moves:
        x, y = board_to_pixel(tr, tc)
        if (tr, tc) in board:
            pygame.draw.circle(screen, (222, 92, 64), (x, y), 29, 3)
        else:
            pygame.draw.circle(screen, dot, (x, y), 9)
            pygame.draw.circle(screen, (24, 120, 76), (x, y), 9, 1)


def draw_check_banner(screen):
    """被将军时在河界处闪一个「将军」字样"""
    phase = (pygame.time.get_ticks() // 320) % 2
    txt = "将 军"
    font = load_font(40)
    surf = font.render(txt, True, (226, 62, 48) if phase else (176, 34, 28))
    surf = surf.convert_alpha()
    surf.set_alpha(230 if phase else 150)
    cx = SCREEN_W // 2 - surf.get_width() // 2
    cy = BOARD_ORIGIN_Y + 4 * CELL + CELL // 2 - surf.get_height() // 2
    screen.blit(surf, (cx, cy))


def draw_result_banner(screen, text):
    """终局结果牌（棋盘中央）"""
    font = load_font(24)
    surf = font.render(text, True, (255, 248, 236))
    w = min(SCREEN_W - 60, surf.get_width() + 44)
    rect = pygame.Rect((SCREEN_W - w) // 2,
                       BOARD_ORIGIN_Y + 236, w, 66)
    shade = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(shade, (150, 42, 34, 232), shade.get_rect(), border_radius=12)
    pygame.draw.rect(shade, (236, 206, 170, 255), shade.get_rect(), 2, border_radius=12)
    screen.blit(shade, rect.topleft)
    screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                       rect.centery - surf.get_height() // 2))


# ---------------------------- 主动议和 / 认输 ----------------------------
# 电脑不再只是「等人类提和」，它自己觉得再下也分不出胜负时会主动开口。
# 人类不同意就接着下，间隔一次比一次长（12 / 24 / 36 个半回合），
# 问过 DRAW_OFFER_MAX 回就不再打扰 —— 用户反馈「议和后还多次议和」太磨人。
DRAW_OFFER_GAP = 12          # 第一次被拒后再等 6 个回合（12 个半回合）才重提
DRAW_OFFER_MIN_MOVES = 16    # 开局 8 个回合内不提和，免得一上来就敷衍
DRAW_OFFER_MAX = 3           # 一局里最多主动议和 3 回，再多就不提了
RESIGN_AFTER_DECLINE = 6     # 必败局里被拒和棋后，再撑 3 个回合（6 个半回合）才认输


def ai_label():
    """对手怎么称呼：手机版说「手机」（同一部手机里没装电脑），桌面版仍说「电脑」"""
    return "手机" if IS_ANDROID else "电脑"


_CN_DIGIT = "零一二三四五六七八九"


def cn_piece_num(n):
    """棋子的个数念法：1→一、2→两、3→三…（两辆车比二辆车顺口）"""
    n = int(n)
    if n == 2:
        return "两"
    return _CN_DIGIT[n] if 1 <= n <= 9 else str(n)


def piece_phrase(counts):
    """把 {车:1, 兵:2} 说成「一车两兵」，让弹窗里的话与盘面一字对应"""
    num = cn_piece_num
    parts = []
    for pt, word in ((ROOK, "车"), (CANNON, "炮"), (HORSE, "马"), (PAWN, "兵")):
        n = int(counts.get(pt, 0))
        if n:
            parts.append(num(n) + word)
    return "".join(parts) or "无进攻子力"


def side_pieces_text(board, side):
    """某一方盘上还剩什么子，说成「一车一士一象」（只说车马炮兵士象）"""
    counts = {}
    for (pc, pt) in board.values():
        if pc == side and pt != KING:
            counts[pt] = counts.get(pt, 0) + 1
    num = cn_piece_num
    parts = []
    for pt, word in ((ROOK, "车"), (CANNON, "炮"), (HORSE, "马"),
                     (PAWN, "兵"), (ADVISOR, "士"), (ELEPHANT, "象")):
        n = int(counts.get(pt, 0))
        if n:
            parts.append(num(n) + word)
    return "".join(parts) or "只剩光将"


def both_side_phrase(board, ai_side):
    """两边各剩什么：「我只剩一车一士，你也一样」/「我只剩一车一兵，你只剩一车一士」。
    两边完全相同时不重复念一遍，读着不啰嗦，子力也照样对得上。"""
    def say(t):
        return t if t.startswith("只剩") else "只剩" + t
    mine = say(side_pieces_text(board, ai_side))
    foe = say(side_pieces_text(board, RED if ai_side == BLACK else BLACK))
    if mine == foe:
        return "我%s，你也一样" % mine
    return "我%s，你%s" % (mine, foe)


def cpu_hopeless(board, ai_side=None):
    """电脑是不是已经没救：只剩老将（最多再带两枚士象），对方手里有实打实的进攻子力。
    满足就返回一句说明（弹窗里要用），还有救返回 None。抽成模块级函数方便单测。
    用户嫌「红方只一将、我多子了还在磨」——这局已经没有悬念，该低头了。"""
    ai_side = ai_side if ai_side in (RED, BLACK) else AI_SIDE
    human = RED if ai_side == BLACK else BLACK
    mine = [pt for (pc, pt) in board.values() if pc == ai_side]
    if not mine:
        return None                      # 连将都没有，局面本身就不正常，不掺和
    if any(pt in (ROOK, CANNON, HORSE, PAWN) for pt in mine):
        return None                      # 还有能过河的子，说不准能反扑
    # 只剩光杆老将才认输：将带一两个士象时，单车也破不了士象全（那是和棋，
    # 不是必败），这时候走普通提和的流程就行，别白送一局
    if len(mine) > 1:
        return None
    foe = [pt for (pc, pt) in board.values()
           if pc == human and pt in (ROOK, CANNON, HORSE, PAWN)]
    if not foe:
        return None
    heavy = sum(1 for pt in foe if pt in (ROOK, CANNON))
    if heavy < 1 and len(foe) < 2:       # 一个兵 / 一匹马想破士象还差得远
        return None
    counts = {}
    for pt in foe:
        counts[pt] = counts.get(pt, 0) + 1
    return ("我只剩光将、士象全无，你手上还有%s，"
            "真挡不住了。" % piece_phrase(counts))


def cpu_draw_reason(board, moves, quiet, reps, last_declined=-99, ai_side=None,
                    declined=0):
    """电脑想提和的理由（不想提就返回 None）。抽出成模块级函数，方便单测。

    只在三种「确实分不出胜负」的盘面开口：
      · 子力枯竭：双方合计 8 枚以内，谁也不多一个车；
      · 长久无进展：连续 40 个半回合没吃子，局面僵着；
      · 局面打转：同一个局面已经走过两回，谁都换不出新招。
    另外要求已经走过 8 个回合，且距上次被拒的间隔逐次拉长；
    被拒 declined 次后就不再提 —— 用户说「议和后多次议和」，太磨人。
    理由一律用第一人称（「我这边…」），读起来是程序自己在说话。"""
    ai_side = ai_side if ai_side in (RED, BLACK) else AI_SIDE
    if declined >= DRAW_OFFER_MAX:
        return None                       # 问够了，这一局不再主动提和
    if moves < DRAW_OFFER_MIN_MOVES:
        return None
    gap = DRAW_OFFER_GAP * (int(declined) + 1)      # 12 → 24 → 36 个半回合
    if moves - int(last_declined) < gap:
        return None
    if insufficient_material(board):
        return ("这盘谁也杀不动了 —— %s，再走也是绕圈。和了吧？"
                % both_side_phrase(board, ai_side))
    score = evaluate(board)
    mine = score if ai_side == RED else -score      # 电脑视角：正数电脑好
    total = len(board)
    if total <= 8 and abs(mine) <= 90:
        # 把两边剩的子写清楚，弹窗里的话与盘面一一对应
        return ("盘上就 %d 枚子了（%s），谁也啃不动谁。和了吧？"
                % (total, both_side_phrase(board, ai_side)))
    if quiet >= 40 and abs(mine) <= 120:
        return ("已经 %d 个回合没吃到你的子，你也一样，"
                "再下就是耗时间。和了吧？" % (quiet // 2))
    if reps >= 2 and abs(mine) <= 90:
        return "这局面咱俩来回走了三遍，谁也没新招。和了吧？"
    return None


def draw_offer_panel():
    """提议和棋的小弹窗：居中显示（模态，棋盘暂时不可点）"""
    # 第一人称说明常常三四行，弹窗做高一点，免得正文压到按钮上
    return pygame.Rect((SCREEN_W - 452) // 2, (SCREEN_H - 244) // 2, 452, 244)


def draw_offer_rects():
    """弹窗里两个按钮：同意和棋 / 继续下（返回 [(Rect, kind)]）"""
    p = draw_offer_panel()
    w, gap = 190, 16
    y = p.bottom - 58
    x = p.centerx - (w * 2 + gap) // 2
    return [(pygame.Rect(x, y, w, 42), "accept"),
            (pygame.Rect(x + w + gap, y, w, 42), "decline")]


def draw_draw_offer_overlay(screen, offer):
    """程序主动议和 / 认输的弹窗：说清为什么，两个大按钮好按"""
    if not offer:
        return
    resign = offer.get("kind") == "resign"
    who = ai_label() if offer.get("who") is None else offer.get("who")
    p = draw_offer_panel()
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 120))
    screen.blit(shade, (0, 0))
    draw_rect(screen, C((252, 249, 242)), p, 0, 14)
    edge = C((168, 76, 58)) if resign else C((52, 96, 150))
    draw_rect(screen, edge, p, 2, 14)
    title_text = (who + "认输") if resign else (who + "提议和棋")
    title = load_font_song(23).render(title_text, True, edge)
    screen.blit(title, (p.centerx - title.get_width() // 2, p.y + 20))

    body = load_font(14)
    lines = wrap_text(offer.get("reason") or "", body, p.w - 56)
    tail = ("接受就判你胜；想亲手吃将就点「继续下」，这局不结束，"
            "我不再提和、也不再认输。" if resign else
            "同意就握手言和，不同意就接着下。")
    lines += wrap_text(tail, body, p.w - 56)
    y = p.y + 62
    for line in lines[:6]:
        surf = body.render(line, True, C((70, 58, 46)))
        screen.blit(surf, (p.x + 28, y))
        y += 20

    bfont = load_font(17)
    for rect, kind in draw_offer_rects():
        if kind == "accept":
            fill, edge_c, fg = (C((178, 74, 58)), C((150, 58, 46)),
                                K((255, 255, 255))) if resign else (
                                   C((34, 150, 96)), C((26, 124, 78)), K((255, 255, 255)))
        else:
            fill, edge_c, fg = C((250, 246, 238)), C((196, 186, 170)), C((92, 82, 68))
        draw_button_face(screen, rect, fill, edge_c, radius=10)
        if resign:
            label = "接受认输" if kind == "accept" else "继续下"
        else:
            label = "同意和棋" if kind == "accept" else "继续下"
        surf = bfont.render(label, True, fg)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))


def draw_move_track(screen, last_move):
    """绘制最近一步的走子轨迹：起止格半透明高亮 + 外环 + 方向箭头"""
    if not last_move:
        return
    fr, fc, tr, tc, mover = last_move
    sx, sy = board_to_pixel(fr, fc)
    dx, dy = board_to_pixel(tr, tc)
    col = (216, 132, 34)

    # 起止格半透明高亮（覆盖在棋子之上，仍能透出棋子）
    for (cx, cy) in ((sx, sy), (dx, dy)):
        surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        surf.fill((216, 132, 34, 70))
        screen.blit(surf, (cx - CELL // 2, cy - CELL // 2))

    # 起止点外环（半径大于棋子，清晰可见）
    pygame.draw.circle(screen, col, (sx, sy), 30, 3)
    pygame.draw.circle(screen, col, (dx, dy), 30, 3)

    if (sx, sy) == (dx, dy):
        return
    ang = math.atan2(dy - sy, dx - sx)
    r0 = 21
    x1 = sx + r0 * math.cos(ang)
    y1 = sy + r0 * math.sin(ang)
    x2 = dx - r0 * math.cos(ang)
    y2 = dy - r0 * math.sin(ang)
    pygame.draw.line(screen, col, (x1, y1), (x2, y2), 4)
    ah = 13
    left = (x2 - ah * math.cos(ang - 0.5), y2 - ah * math.sin(ang - 0.5))
    right = (x2 - ah * math.cos(ang + 0.5), y2 - ah * math.sin(ang + 0.5))
    pygame.draw.polygon(screen, col, [(x2, y2), left, right])


# ---------------------------- 残局库与摆棋模式 ----------------------------
LIB_PATH = os.path.join(_BASE_DIR, "残局库.json")
LIB_DELETED_PATH = os.path.join(_BASE_DIR, "残局库_已删.json")   # 用户删掉的局，防升级时被补回来
SETTINGS_PATH = os.path.join(_BASE_DIR, "象棋设置.json")
LIB_PAGE_SIZE = 20           # 残局库一屏可见 20 行（尾部同样按 20 行显示）
LIB_ROW_H = 30               # 行高
LIB_ROW_STEP = 33            # 行距
LIB_PANEL_TOP = 56


def load_settings():
    """读取本地设置（如残局库滚动位置），损坏时返回空字典"""
    if not os.path.exists(SETTINGS_PATH):
        return {}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(data):
    tmp = SETTINGS_PATH + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        os.replace(tmp, SETTINGS_PATH)
    except OSError:
        pass

PALETTE = [
    (RED, KING), (RED, ADVISOR), (RED, ELEPHANT), (RED, HORSE),
    (RED, ROOK), (RED, CANNON), (RED, PAWN),
    (BLACK, KING), (BLACK, ADVISOR), (BLACK, ELEPHANT), (BLACK, HORSE),
    (BLACK, ROOK), (BLACK, CANNON), (BLACK, PAWN),
]

# 摆棋底板：每方按全盘 16 枚依次排布（摆一枚少一枚）
PALETTE_ORDER = [KING, ADVISOR, ELEPHANT, HORSE, ROOK, CANNON, PAWN]
PALETTE_ROWS = (EDIT_BAR1_Y, EDIT_BAR1_Y + 32)
PALETTE_X0 = 26
PALETTE_STEP = 32
PALETTE_SLOT = (30, 28)

EDIT_ACTIONS = [("erase", "擦除", 62), ("clear", "清空", 62), ("name", "命名", 62),
                ("save", "保存", 62), ("load", "载入", 62), ("done", "完成", 70),
                ("cancel", "取消", 62)]

# ---------------------------- 中文记谱与棋谱导出 ----------------------------
RED_FILES = ["九", "八", "七", "六", "五", "四", "三", "二", "一"]
BLACK_FILES = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
RED_NUMS = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
FULLWIDTH_DIGITS = ["１", "２", "３", "４", "５", "６", "７", "８", "９"]


def file_label(color, c):
    return RED_FILES[c] if color == RED else BLACK_FILES[c]


def count_label(color, n):
    if color == RED:
        return RED_NUMS[min(n, 9) - 1]
    return BLACK_FILES[min(n, 9) - 1]


def move_notation(board, fr, fc, tr, tc, color):
    """把一步棋转成中文记谱（炮二平五 / 马8进7 …）"""
    piece = board.get((fr, fc))
    if piece is None:
        return "(%d,%d)-(%d,%d)" % (fr, fc, tr, tc)
    kind = piece[1]
    name = CHINESE_PIECES[(color, kind)]

    same = sorted(r for (r, c), p in board.items()
                  if c == fc and p[0] == color and p[1] == kind)
    if len(same) > 1:
        order = same if color == RED else list(reversed(same))
        idx = order.index(fr)
        labels = ["前", "中", "后"] if len(order) == 3 else ["前", "后"]
        if idx >= len(labels):
            return "%s%d-%d" % (name, fr, fc)
        head = labels[idx] + name
    else:
        head = name + file_label(color, fc)

    if fr == tr:
        return head + "平" + file_label(color, tc)

    forward = (tr < fr) if color == RED else (tr > fr)
    verb = "进" if forward else "退"
    if kind in (ROOK, CANNON, PAWN, KING):
        return head + verb + count_label(color, abs(tr - fr))
    return head + verb + file_label(color, tc)


# ---------------------------- 棋谱文本反向解析（导入用） ----------------------------
_PIECE_CHARS = "车馬马象相士仕将帥帅炮兵卒"
_PIECE_POS = re.compile(
    r"([%s])\s*[（(]\s*(\d+)\s*[,，]\s*(\d+)\s*[）)]" % _PIECE_CHARS)
# 两种记谱都要认：普通式「马4退6」与叠子式「前炮进1」（同线两子，无路数）
_MOVE_TOKEN = re.compile(
    r"(?:[%s]\s*[一二三四五六七八九1-9１-９]\s*[进退平]\s*[一二三四五六七八九1-9１-９]"
    r"|(?:前|后|中)\s*[%s]\s*[进退平]\s*[一二三四五六七八九1-9１-９])"
    % (_PIECE_CHARS, _PIECE_CHARS))

# 中文棋子名 → 兵种；同形名（车马炮）由所在行的红/黑标记决定
_NAME_KIND = {"车": ROOK, "馬": HORSE, "马": HORSE,
              "象": ELEPHANT, "相": ELEPHANT,
              "士": ADVISOR, "仕": ADVISOR,
              "将": KING, "帥": KING, "帅": KING,
              "炮": CANNON, "砲": CANNON,
              "兵": PAWN, "卒": PAWN}
_NAME_COLOR = {"帅": RED, "帥": RED, "仕": RED, "相": RED, "兵": RED,
               "将": BLACK, "士": BLACK, "象": BLACK, "卒": BLACK}


def parse_piece_list(text):
    """从棋谱文本里读出初始局面。识别形如「黑方：车(0,0) 马(0,1) …」的行；
    行首没有红/黑标记时，按棋子名推断（帅仕相兵为红，将士象卒为黑）。"""
    board = {}
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        head_color = None
        if s.startswith("红方") or s.startswith("红"):
            head_color = RED
        elif s.startswith("黑方") or s.startswith("黑"):
            head_color = BLACK
        for nm, r, c in _PIECE_POS.findall(s):
            kind = _NAME_KIND.get(nm)
            if kind is None:
                continue
            color = _NAME_COLOR.get(nm, head_color)
            if color is None:
                continue
            r, c = int(r), int(c)
            if in_board(r, c):
                board[(r, c)] = (color, kind)
    return board


def move_by_notation(board, color, token):
    """按中文着法文本找对应的合法着法（如「炮八平五」「前炮进1」）"""
    token = (token or "").strip()
    if not token:
        return None
    for mv in legal_moves(board, color):
        if move_notation(board, mv[0], mv[1], mv[2], mv[3], color) == token:
            return mv
    return None


def replay_notation(board, tokens):
    """按着法序列回放；返回 (最终局面, 着法列表, 重复局面计数, 出错说明)"""
    b = dict(board)
    turn = RED
    moves = []
    rep_counts = {position_key(b, RED): 1}
    err = ""
    for i, tok in enumerate(tokens):
        mv = move_by_notation(b, turn, tok)
        if mv is None:
            err = "第 %d 手「%s」对不上" % (i + 1, tok)
            break
        moves.append({"side": name_of(turn), "text": tok, "left": "",
                      "fr": mv[0], "fc": mv[1], "tr": mv[2], "tc": mv[3]})
        b = apply_move(b, mv[0], mv[1], mv[2], mv[3])
        turn = opponent(turn)
        key = position_key(b, turn)
        rep_counts[key] = rep_counts.get(key, 0) + 1
    return b, moves, rep_counts, err


def parse_record_text(text):
    """解析本程序导出的棋谱文本：返回 dict（start / final / moves / note）或 None"""
    if "初始局面" not in text and "着法记录" not in text:
        return None
    head, _, tail = text.partition("着法记录")
    start = parse_piece_list(head if head else text)
    if not start:
        return None
    tokens = _MOVE_TOKEN.findall(tail)
    final, moves, rep_counts, err = replay_notation(start, tokens)
    note = ("已回放 %d 手" % len(moves)) if moves else ""
    if err:
        note = (note + "，" if note else "") + err
    return {"start": start, "final": final, "moves": moves,
            "rep_counts": rep_counts, "note": note}


def record_text(state, reason=""):
    """生成棋谱文本"""
    history = state["history"]
    lines = ["中国象棋对局记录", "=" * 34,
             "局面：%s" % state["position"],
             "难度：%s    时限：每方 %d 分钟　单步：%s" % (
                 state["difficulty"], state.get("time_limit", TIME_LIMIT) // 60,
                 move_limit_label(state.get("move_limit", 0))),
             "生成时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
             "红方：玩家    黑方：%s%s" % (ai_label(), "（" + state["difficulty"] + "）"),
             "", "初始局面："]
    counts = {}
    for (r, c), (pc, pt) in sorted(state["start_board"].items()):
        counts.setdefault(name_of(pc), []).append(
            "%s(%d,%d)" % (CHINESE_PIECES[(pc, pt)], r, c))
    for side, items in counts.items():
        lines.append("  %s：%s" % (side, " ".join(items)))

    lines += ["", "着法记录（红方先走）："]
    for i in range(0, len(history), 2):
        red = history[i]
        black = history[i + 1] if i + 1 < len(history) else None
        text = "%3d. %-10s" % (i // 2 + 1, red["text"])
        if black:
            text += "  %-10s" % black["text"]
        text += "   [红 %s" % red["left"]
        if black:
            text += " / 黑 %s" % black["left"]
        lines.append(text + "]")

    lines += ["", "结果：%s" % (state["result"] or "未终局（手动导出）")]
    if reason:
        lines.append("备注：%s" % reason)
    lines.append("")
    lines.append("说明：括号内为双方剩余时间；(行,列) 行 0 为黑方底线、列 0 为红方左手第一路。")
    return "\n".join(lines)


def export_record(state):
    """把棋谱写到程序目录下的 棋谱/ 文件夹，返回 (成功, 路径或错误)"""
    if not state["history"]:
        return False, "还没有走过棋，暂时没有棋谱可导出。"
    folder = os.path.join(_BASE_DIR, "棋谱")
    try:
        os.makedirs(folder, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        safe = "".join(ch for ch in state["position"] if ch not in '\\/:*?"<>| ')[:12]
        path = os.path.join(folder, "棋谱_%s_%s.txt" % (safe or "对局", stamp))
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(record_text(state))
    except OSError as exc:
        return False, "导出失败：%s" % exc
    return True, path


def _seed_library():
    """首次运行：把随程序附带的残局库（打包进 exe 里，或与程序同目录）拷到数据目录"""
    if os.path.exists(LIB_PATH):
        return
    for base in (_res_dir(), _base_dir()):
        src = os.path.join(base, "残局库.json")
        if os.path.abspath(src) == os.path.abspath(LIB_PATH):
            continue
        if os.path.exists(src):
            try:
                shutil.copyfile(src, LIB_PATH)
            except OSError:
                pass
            return


def _bundled_library():
    """随程序发布的那份残局库（只读），用于版本升级时补进新局。"""
    for base in (_res_dir(), _base_dir()):
        src = os.path.join(base, "残局库.json")
        if os.path.abspath(src) == os.path.abspath(LIB_PATH):
            continue
        try:
            with open(src, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, ValueError):
            continue
        if isinstance(data, list):
            return [it for it in data
                    if isinstance(it, dict) and isinstance(it.get("pieces"), list)]
    return []


def load_deleted_keys():
    """读「已删名单」：用户删掉的局（名字 + 局面指纹）。
    随程序带的那批局每次启动都会按名字并回来，不记一笔的话删了下次又冒出来。"""
    empty = {"names": set(), "sigs": set()}
    try:
        with open(LIB_DELETED_PATH, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, ValueError):
        return empty
    if not isinstance(data, dict):
        return empty
    return {"names": set(str(x) for x in (data.get("names") or [])),
            "sigs": set(str(x) for x in (data.get("sigs") or []))}


def remember_deleted(entry):
    """把删掉的局记进名单，下次启动补新局时跳过它"""
    keys = load_deleted_keys()
    name = str(entry.get("name") or "")
    if name:
        keys["names"].add(name)
    try:
        sig = position_signature(entry)
    except Exception:
        sig = ""
    if sig:
        keys["sigs"].add(sig)
    tmp = LIB_DELETED_PATH + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fp:
            json.dump({"names": sorted(keys["names"]), "sigs": sorted(keys["sigs"])},
                      fp, ensure_ascii=False, indent=2)
        os.replace(tmp, LIB_DELETED_PATH)
    except OSError as exc:
        print("已删名单写入失败：%s" % exc)


def clear_deleted_keys():
    """恢复备份 / 导库之后清空名单：刚恢复回来的局不该被挡住"""
    try:
        if os.path.exists(LIB_DELETED_PATH):
            os.remove(LIB_DELETED_PATH)
    except OSError:
        pass


def load_library():
    """读取残局库（JSON 文件不存在或损坏时返回空列表）。
    升级时把随程序新增的经典 / 江湖局按名字并进来——手机覆盖安装不会清数据目录，
    老库里没有新局，只靠首次 seed 是补不进去的。用户改过的同名条目不动。"""
    _seed_library()
    clean = []
    if os.path.exists(LIB_PATH):
        try:
            with open(LIB_PATH, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, ValueError) as exc:
            print("残局库读取失败：%s" % exc)
            data = []
        if isinstance(data, list):
            clean = [item for item in data
                     if isinstance(item, dict) and isinstance(item.get("pieces"), list)]
    bundled = _bundled_library()
    if bundled:
        gone = load_deleted_keys()
        have = {it.get("name") for it in clean}
        added = [it for it in bundled
                 if it.get("name") not in have
                 and it.get("name") not in gone["names"]
                 and position_signature(it) not in gone["sigs"]]
        if added:
            clean.extend(added)
            try:
                save_library(clean, backup=False)
            except OSError:
                pass
    return clean


def backup_library():
    """写库前留底：残局库.bak1 ~ .bak3 滚动保留 3 份"""
    if not os.path.exists(LIB_PATH):
        return
    try:
        for i in range(3, 1, -1):
            src = "%s.bak%d" % (LIB_PATH, i - 1)
            dst = "%s.bak%d" % (LIB_PATH, i)
            if os.path.exists(src):
                shutil.copyfile(src, dst)
        shutil.copyfile(LIB_PATH, LIB_PATH + ".bak1")
        # 老版本留过 5 份，多出来的 4 / 5 号顺手清掉，免得占地方又让人分不清
        for i in range(4, 6):
            old = "%s.bak%d" % (LIB_PATH, i)
            if os.path.exists(old):
                try:
                    os.remove(old)
                except OSError:
                    pass
    except OSError as exc:
        print("残局库备份失败：%s" % exc)


def restore_library_backup():
    """从最近一份备份（.bak1）恢复整库。
    恢复前先把当前库转存成 .bak1（旧的往后退一份），所以点错了还能再恢复回来。
    返回 (条目列表 或 None, 提示语)。"""
    src = LIB_PATH + ".bak1"
    if not os.path.exists(src):
        return None, "暂时没有备份可恢复（每次改库才会自动留底）。"
    try:
        with open(src, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, ValueError) as exc:
        return None, "备份读取失败：%s" % exc
    if not isinstance(data, list):
        return None, "备份文件不是残局库格式，没法恢复。"
    clean = [it for it in data
             if isinstance(it, dict) and isinstance(it.get("pieces"), list)]
    if not clean:
        return None, "备份里没有可用的残局。"
    try:
        backup_library()          # 当前库先退到 bak1，上面要恢复的数据已在内存里
        save_library(clean, backup=False)
    except OSError as exc:
        return None, "恢复失败：%s" % exc
    return clean, "已从备份恢复 %d 局（恢复前的库另存在 .bak1，可再恢复回去）。" % len(clean)


def save_library(entries, backup=True):
    if backup:
        backup_library()
    tmp = LIB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fp:
        json.dump(entries, fp, ensure_ascii=False, indent=2)
    os.replace(tmp, LIB_PATH)


# ---------------------------- 残局库条目字段（兼容旧数据） ----------------------------
_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}")


def entry_saved_at(entry):
    """存盘时间：新数据在 saved_at；旧数据把时间写在 saved 里（按格式识别）"""
    v = entry.get("saved_at")
    if v:
        return str(v)
    raw = entry.get("saved")
    if raw and _TS_RE.match(str(raw)):
        return str(raw)
    return ""


def entry_origin(entry):
    """出处：新数据在 origin；旧数据把集名写在 saved 里，或只有 source 文件名"""
    v = entry.get("origin")
    if v:
        return str(v)
    raw = entry.get("saved")
    if raw and str(raw).strip() and not _TS_RE.match(str(raw)):
        return str(raw)
    src = os.path.basename(str(entry.get("source") or ""))
    return os.path.splitext(src)[0] if src else ""


def short_origin(text):
    """出处只留集名：去掉括号注释与扩展名，太长由绘制处再截"""
    t = (text or "").strip()
    t = re.split(r"[（(【\[]", t)[0].strip()
    t = re.sub(r"\.(fen|json|txt|pdb|pgn)$", "", t, flags=re.I)
    return t


def entry_turn(entry):
    """条目先行方（缺省红先）"""
    v = entry.get("turn")
    return v if v in (RED, BLACK) else RED


def entry_done_side(entry):
    """已通关记录里的胜方；旧数据只有 done=True，按红胜记"""
    if not entry.get("done"):
        return ""
    v = entry.get("done_side")
    return v if v in (RED, BLACK) else RED


def stamp_day(ts):
    """存盘时间取「月-日」，行内只放得下这么宽"""
    m = re.match(r"^\d{4}-(\d{2})-(\d{2})", ts or "")
    return "%s-%s" % (m.group(1), m.group(2)) if m else ""


def pick_library_file(save=False):
    """用系统文件对话框选残局库文件；无 tkinter 时退回固定文件名"""
    default = os.path.join(_BASE_DIR, "残局库_导出.json")
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        if save:
            path = filedialog.asksaveasfilename(
                title="导出残局库", defaultextension=".json",
                initialfile="残局库_导出.json",
                filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
        else:
            path = filedialog.askopenfilename(
                title="导入残局库",
                filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
        root.destroy()
        return path or ""
    except Exception:
        return "" if not save else default


def pick_text_file():
    """选择棋谱 / 局面文本文件（.txt .json .fen）；取消返回空串"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="选择棋谱或局面文件",
            initialdir=os.path.join(_BASE_DIR, "棋谱"),
            filetypes=[("棋谱 / 局面", "*.txt *.json *.fen"),
                       ("文本文件", "*.txt"), ("所有文件", "*.*")])
        root.destroy()
        return path or ""
    except Exception:
        return ""


def pick_music_file():
    """选一首音频文件（.mp3 / .ogg / .wav）；取消或无 tkinter 返回空串"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="导入曲子（最多 4 首）",
            filetypes=[("音频文件", "*.mp3 *.ogg *.wav"),
                       ("MP3", "*.mp3"), ("OGG", "*.ogg"), ("WAV", "*.wav"),
                       ("所有文件", "*.*")])
        root.destroy()
        return path or ""
    except Exception:
        return ""


def music_write_dir():
    """导入曲子存哪儿：手机优先外部可写目录（卸载不丢），桌面用程序旁的 曲"""
    ext = extern_files_dir()
    base = ext if (IS_ANDROID and ext) else _BASE_DIR
    d = os.path.join(base, MUSIC_DIR)
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        return None
    return d if os.path.isdir(d) else None


def import_music_file(src):
    """把选中的一首曲子拷进 曲 目录，返回 (是否成功, 提示语)。
    上限 MUSIC_MAX_FILES 首：设置页只有一行位置，多了排不下；名字过长也在这里截短。"""
    if not src:
        return False, "没有选文件，已取消导入。"
    stem, ext = os.path.splitext(os.path.basename(src))
    if ext.lower() not in AUDIO_EXTS:
        return False, "只收 mp3 / ogg / wav 这三种音频，这个格式放不了。"
    have = music_library()
    if len(have) >= MUSIC_MAX_FILES:
        return False, ("曲目录已经有 %d 首（上限 %d 首），先在文件管理里删掉一两首再导入。"
                       % (len(have), MUSIC_MAX_FILES))
    d = music_write_dir()
    if not d:
        return False, "找不到可写的曲目录，导入失败。"
    stem = (stem or "曲子").strip()
    if len(stem) > 12:                 # 名字太长在设置页只会剩省略号，这里先砍短
        stem = stem[:12]
    dst = os.path.join(d, stem + ext.lower())
    if os.path.exists(dst):
        return False, "「%s」已经在曲目录里了。" % stem
    try:
        shutil.copyfile(src, dst)
    except OSError as exc:
        return False, "导入失败：%s" % exc
    _MUSIC_CACHE.pop(stem, None)
    return True, "已导入「%s」，设置里的曲目就多一个（曲目录 %d/%d 首）。" % (
        stem, len(music_library()), MUSIC_MAX_FILES)


def delete_music_file(name):
    """删掉 曲 目录里导入的某一首，返回 (是否成功, 提示语)。
    内置古曲是程序合成的、盘上没有文件，删不掉——那几首留着当兜底。"""
    path = find_audio(MUSIC_DIR, (name,))
    if not path:
        return False, "「%s」是程序内置的合成古曲，盘上没有文件，删不掉。" % name
    if len(music_library()) <= 1:
        return False, "曲目录里只剩这一首了，删掉就没音乐可放了。"
    try:
        os.remove(path)
    except OSError as exc:
        return False, "删除失败：%s" % exc
    _MUSIC_CACHE.pop(name, None)
    return True, "已删掉「%s」，曲目录还剩 %d/%d 首。可选别的曲目顶上。" % (
        name, len(music_library()), MUSIC_MAX_FILES)


def board_to_record(board):
    return [{"r": r, "c": c, "color": pc, "type": pt}
            for (r, c), (pc, pt) in sorted(board.items())]


# ---------------------------- FEN 导入 / 导出 ----------------------------
_XFEN_TYPE = {"K": KING, "A": ADVISOR, "E": ELEPHANT, "B": ELEPHANT,
              "H": HORSE, "N": HORSE, "R": ROOK, "C": CANNON, "P": PAWN}


def fen_to_board(fen):
    """把象棋 FEN（首字段为棋盘摆放，行 0 为黑方底线）解析为内部棋盘；失败返回 None"""
    if not fen:
        return None
    placement = fen.strip().split()[0]
    rows = placement.split("/")
    if len(rows) != BOARD_ROWS:
        return None
    board = {}
    for r, row in enumerate(rows):
        c = 0
        for ch in row:
            if ch.isdigit():
                c += int(ch)
            else:
                color = RED if ch.isupper() else BLACK
                pt = _XFEN_TYPE.get(ch.upper())
                if pt is None or c >= BOARD_COLS:
                    return None
                board[(r, c)] = (color, pt)
                c += 1
        if c != BOARD_COLS:
            return None
    return board


def board_to_fen(board):
    """把内部棋盘导出为象棋 FEN 摆放字段（不含着法计数）"""
    rows = []
    for r in range(BOARD_ROWS):
        row, empty = "", 0
        for c in range(BOARD_COLS):
            p = board.get((r, c))
            if not p:
                empty += 1
                continue
            if empty:
                row += str(empty)
                empty = 0
            pc, pt = p
            ch = {KING: "K", ADVISOR: "A", ELEPHANT: "E", HORSE: "H",
                  ROOK: "R", CANNON: "C", PAWN: "P"}[pt]
            row += ch if pc == RED else ch.lower()
        if empty:
            row += str(empty)
        rows.append(row)
    return "/".join(rows)


def position_key(board, turn):
    """局面指纹（含走子方），用于三次重复局面判定"""
    return board_to_fen(board) + ("|r" if turn == RED else "|b")


REPEAT_BLOCK = 3            # 同一局面第几次出现时拦下（第 3 次才算重复，前两次放行）
LONG_CHECK_STEPS = 6        # 连续将军多少步判长将负
QUIET_HALFMOVES = 120       # 60 个回合（120 个半回合）无吃子判和


def repeat_cycle_verdict(pos_log, key, mover, enemy, seen=None):
    """同一局面第 REPEAT_BLOCK 次出现时的裁决 —— 看「这一轮重复」里究竟谁在将军。

    pos_log 每走一着记一条 {"key": 走完后的局面指纹, "mover": 走子方, "check": 是否将军}。
    以「上一次出现同一局面」为起点，把它之后到现在的所有着法当作一个循环：
      · 只有一方每着都在将军 → 该方长将判负；被迫来回躲闪的一方不受罚；
      · 双方每着都在将军     → 互将，判和；
      · 都不在将军           → 谁都换不出别的着法，判和（三次重复局面）。
    返回 (类型, 结果文字, 胜方或 None)；还没到第 REPEAT_BLOCK 次返回 None。
    类型：long_check（连将方判负）/ draw（和棋）。"""
    cnt = seen if seen is not None else sum(1 for r in pos_log if r["key"] == key)
    if cnt < REPEAT_BLOCK or len(pos_log) < 2:
        return None
    idxs = [i for i, r in enumerate(pos_log) if r["key"] == key]
    if len(idxs) < 2:
        return None
    span = pos_log[idxs[-2] + 1:]        # 上一次出现之后到现在，正好一个循环
    mine = [r for r in span if r["mover"] == mover]
    theirs = [r for r in span if r["mover"] == enemy]
    my_check = bool(mine) and all(r["check"] for r in mine)
    en_check = bool(theirs) and all(r["check"] for r in theirs)
    if my_check and en_check:
        return ("draw", "和棋 —— 三次重复局面（双方互相将军）", None)
    if my_check:
        return ("long_check", "%s胜 —— %s长将判负" % (name_of(enemy), name_of(mover)), enemy)
    if en_check:
        return ("long_check", "%s胜 —— %s长将判负" % (name_of(mover), name_of(enemy)), mover)
    return ("draw", "和棋 —— 三次重复局面（%s已无别的着法可走）" % name_of(mover), None)


def rule_verdict(rep_counts, key, quiet_halfmoves, check_streak, mover, enemy):
    """走完一步后的规则判定：返回 (类型, 结果说明) 或 None
    类型：long_check（长将判负）/ quiet（六十回合无吃子）
    注：v1.2 起「三次重复局面」不再判和，改为走子前禁止重复（见 banned_repeats）"""
    if check_streak.get(mover, 0) >= LONG_CHECK_STEPS:
        return ("long_check",
                "%s胜 —— %s长将判负" % (name_of(enemy), name_of(mover)))
    if quiet_halfmoves >= QUIET_HALFMOVES:
        return ("quiet", "和棋 —— 六十回合无吃子")
    return None


def repeat_kind(board, turn, rep_counts, move):
    """走这一着会让同一局面第几次出现，分三种情况：
    None      —— 还没到第 REPEAT_BLOCK 次，照常走
    "repeat"  —— 非将军的重复（长捉、长跟、来回倒），按温和版禁走，要求换着法
    "check"   —— 将军的重复，也就是长将。这一着不拦，放行；走完由长将规则判负，
                 否则「禁重复」会把长将挡在半路，永远判不出胜负"""
    child = apply_move(board, move[0], move[1], move[2], move[3])
    enemy = opponent(turn)
    seen = rep_counts.get(position_key(child, enemy), 0)
    if seen + 1 < REPEAT_BLOCK:
        return None
    return "check" if in_check(child, enemy) else "repeat"


def is_long_check_repeat(board, turn, rep_counts, move):
    """这一着是否构成「长将」——将军且让同一局面第 REPEAT_BLOCK 次出现"""
    return repeat_kind(board, turn, rep_counts, move) == "check"


def repeating_move(board, turn, rep_counts, move):
    """走这一着后，局面将出现的次数是否已达到 REPEAT_BLOCK（温和版：第 3 次才拦）。
    前两次回到同一局面照常放行，只有再来一次才判为重复走子。"""
    child = apply_move(board, move[0], move[1], move[2], move[3])
    seen = rep_counts.get(position_key(child, opponent(turn)), 0)
    return seen + 1 >= REPEAT_BLOCK


def hint_moves(board, color, rep_counts, sel):
    """某格棋子的可落地（绿点提示用）；与真人走子规则一致，已剔除会造成重复的着法"""
    all_moves = legal_moves(board, color)
    bad = set(banned_repeats(board, color, rep_counts, all_moves))
    return [mv for mv in all_moves if (mv[0], mv[1]) == sel and mv not in bad]


def banned_repeats(board, turn, rep_counts, moves=None, ban_check_repeat=False):
    """返回会导致重复局面的着法清单，分两级：
      · 硬禁（"check"）—— 走完还是将军，也就是长将。这一步会直接判自己负；
      · 软禁（"repeat"）—— 不将军的来回打转，容易被判「三次重复」和棋或逼着换招。
    ban_check_repeat=False：只禁软的那档，长将放行（交给判负）——真人走子用。
    ban_check_repeat=True ：两档都禁，但**先保命再讲效率**——只要还有不打转的着法，
                            就绝不走长将；软的那档也全禁了才退回去允许打转。
    以前的写法是「有任一着法被禁就全放开」，于是「只剩长将可走」时电脑照样走，
    白送一局（用户看到的「黑方长将判负」就是这么来的）。"""
    moves = list(legal_moves(board, turn)) if moves is None else list(moves)
    hard, soft = [], {}
    for mv in moves:
        kind = repeat_kind(board, turn, rep_counts, mv)
        if kind == "check":
            hard.append(mv)
        elif kind == "repeat":
            soft[mv] = True
    if not ban_check_repeat:
        hard = []                       # 真人：长将放行，由裁判判负
    bad = list(hard) + [mv for mv in moves if mv in soft and mv not in hard]
    if len(bad) >= len(moves):
        bad = list(hard)                # 退一步：宁可打转，也别自己走进长将
    if len(bad) >= len(moves):
        return []                       # 连这步都退不了：实在无着可变，允许重复
    return bad


# ---------------------------- 江湖排局专题 ----------------------------
def _jp_dict(name, board):
    """构造一个江湖排局条目（内部棋盘 → record）"""
    return {
        "name": name,
        "category": "江湖排局",
        "saved": "经典排局",
        "pieces": board_to_record(board),
    }


# 经典江湖名局（经过程序合法性校验的简化排局，供「江湖排局」专题展示）
JIANGHU_POSITIONS = [
    _jp_dict("七星聚会", {
        (9, 4): (RED, KING), (0, 3): (BLACK, KING),
        (9, 0): (RED, ROOK), (0, 0): (BLACK, ROOK),
        (7, 4): (RED, CANNON), (2, 4): (BLACK, CANNON),
        (9, 6): (RED, HORSE), (6, 4): (RED, PAWN),
    }),
    _jp_dict("千里独行", {
        (9, 4): (RED, KING), (0, 4): (BLACK, KING),
        (9, 8): (RED, ROOK), (0, 0): (BLACK, ROOK),
        (7, 4): (RED, CANNON), (3, 4): (RED, PAWN), (2, 4): (BLACK, CANNON),
    }),
    _jp_dict("野马操田", {
        (9, 3): (RED, KING), (0, 5): (BLACK, KING),
        (9, 0): (RED, ROOK), (0, 8): (BLACK, ROOK),
        (8, 2): (RED, HORSE), (8, 6): (RED, HORSE),
        (2, 4): (BLACK, CANNON), (6, 4): (RED, PAWN),
    }),
    _jp_dict("蚯蚓降龙", {
        (9, 4): (RED, KING), (0, 4): (BLACK, KING),
        (7, 4): (RED, CANNON), (2, 4): (BLACK, CANNON),
        (9, 0): (RED, ROOK), (0, 8): (BLACK, ROOK),
        (6, 3): (RED, PAWN), (6, 5): (RED, PAWN), (1, 4): (BLACK, PAWN),
    }),
    _jp_dict("鸿雁双飞", {
        (9, 4): (RED, KING), (0, 4): (BLACK, KING),
        (9, 1): (RED, ROOK), (9, 7): (RED, ROOK),
        (0, 1): (BLACK, ROOK), (0, 7): (BLACK, ROOK),
        (5, 4): (RED, CANNON), (4, 4): (BLACK, CANNON),
    }),
    _jp_dict("大鹏展翅", {
        (9, 4): (RED, KING), (0, 4): (BLACK, KING),
        (9, 0): (RED, ROOK), (8, 2): (RED, HORSE), (8, 6): (RED, HORSE),
        (0, 8): (BLACK, ROOK), (2, 2): (BLACK, HORSE), (2, 6): (BLACK, HORSE),
        (5, 4): (RED, CANNON),
    }),
    _jp_dict("红马盘槽", {
        (9, 4): (RED, KING), (0, 4): (BLACK, KING),
        (9, 8): (RED, ROOK), (0, 0): (BLACK, ROOK),
        (7, 7): (RED, HORSE), (7, 1): (RED, HORSE),
        (2, 4): (BLACK, CANNON), (3, 4): (BLACK, PAWN),
    }),
    _jp_dict("炮震山河", {
        (9, 4): (RED, KING), (0, 4): (BLACK, KING),
        (7, 4): (RED, CANNON), (7, 2): (RED, CANNON),
        (2, 4): (BLACK, CANNON), (2, 6): (BLACK, CANNON),
        (9, 0): (RED, ROOK), (0, 8): (BLACK, ROOK),
    }),
]


def ensure_library():
    """读取残局库并为每条目补全分类；首次运行时补入江湖排局专题。幂等。"""
    entries = load_library()
    changed = False
    for e in entries:
        if "category" not in e or not e.get("category"):
            e["category"] = CUSTOM_CATEGORY    # 没有分类的旧条目按「自定残局」归类
            changed = True
    names = {e.get("name") for e in entries}
    gone = load_deleted_keys()       # 用户删掉的江湖局也别再补回来
    for jp in JIANGHU_POSITIONS:
        if jp["name"] in names or jp["name"] in gone["names"]:
            continue
        if position_signature(jp) in gone["sigs"]:
            continue
        entries.append(dict(jp))
        changed = True
    if changed:
        try:
            save_library(entries)
        except OSError:
            pass
    return entries


def record_to_board(records):
    board = {}
    for item in records:
        try:
            r, c = int(item["r"]), int(item["c"])
            color, kind = item["color"], item["type"]
        except (KeyError, TypeError, ValueError):
            continue
        if in_board(r, c) and (color, kind) in CHINESE_PIECES:
            board[(r, c)] = (color, kind)
    return board


def piece_count_message(board):
    """按标准数量核验单方各兵种上限，超限返回提示，否则返回 None"""
    counts = {RED: {}, BLACK: {}}
    for (r, c), (pc, pt) in board.items():
        counts[pc][pt] = counts[pc].get(pt, 0) + 1
    for color in (RED, BLACK):
        for pt, mx in PIECE_MAX.items():
            if counts[color].get(pt, 0) > mx:
                return "%s「%s」最多 %d 个，当前 %d 个。" % (
                    name_of(color), CHINESE_PIECES[(color, pt)], mx,
                    counts[color][pt])
    return None


def validate_position(board, rules=True):
    """摆棋完成校验（按规则逐项检查）：
    1) 双方必须有将/帅（且各仅一枚）；
    2) 除将/帅外，每方至少还要有一枚棋子（不得光杆）；
    3) 士象车马炮每方不超 2 枚，兵卒不超 5 枚；
    4) 落点合法：将帅士不出九宫、象守本方象位不过河、兵卒不后退（rules=False 时跳过，
       用于经典排局这类允许特殊构图的局面）；
    5) 将帅不得照面。
    返回 (是否合规, 提示语)。
    """
    missing = []
    for color in (RED, BLACK):
        if not any(p == (color, KING) for p in board.values()):
            missing.append("%s「%s」" % (name_of(color), CHINESE_PIECES[(color, KING)]))
    if missing:
        return False, "缺少 %s：双方各必须有一枚将/帅。" % "、".join(missing)

    bare = [name_of(color) for color in (RED, BLACK)
            if not any(pc == color and pt != KING for pc, pt in board.values())]
    if bare:
        return False, "%s除将/帅外至少还要有一枚棋子。" % "、".join(bare)

    msg = piece_count_message(board)
    if msg:
        return False, msg
    if rules:
        why = position_rule_message(board)
        if why:
            return False, why
    if kings_face(board):
        return False, "将帅照面，请在两王之间加一个棋子。"
    return True, ""


def placement_check(board, piece, target):
    """摆棋放子核验：返回 (是否允许, 提示语)。
    先核验落点（士象兵卒的合法格位），再扣除目标格原有棋子后计数，
    因此「用炮覆盖别的子」也无法凑出第三枚炮。"""
    pc, pt = piece
    ok, why = square_rule(piece, target[0], target[1])
    if not ok:
        return False, why
    limit = PIECE_MAX.get(pt, 99)
    cur = sum(1 for sq, p in board.items() if p == (pc, pt) and sq != target)
    if cur >= limit:
        return False, "%s「%s」最多 %d 个，当前已 %d 个，不能再添。" % (
            name_of(pc), CHINESE_PIECES[(pc, pt)], limit, cur)
    return True, "已放置%s「%s」（%d/%d）。点「完成」开战。" % (
        name_of(pc), CHINESE_PIECES[(pc, pt)], cur + 1, limit)


def palette_rects(board):
    """摆棋底板：每方按全盘 16 枚固定格位排布，返回 [(rect, piece, 是否还能摆)]。
    盘上已有的棋子会让对应格位变空，摆一枚就少一枚；擦除后自动回到板上。"""
    rects = []
    for row, color in enumerate((RED, BLACK)):
        y = PALETTE_ROWS[row]
        x = PALETTE_X0
        for pt in PALETTE_ORDER:
            need = PIECE_MAX.get(pt, 1)
            used = sum(1 for p in board.values() if p == (color, pt))
            for k in range(need):
                rects.append((pygame.Rect(x, y, PALETTE_SLOT[0], PALETTE_SLOT[1]),
                              (color, pt), k >= used))
                x += PALETTE_STEP
    return rects


def palette_remaining(board, piece):
    """某兵种还可摆放的枚数"""
    pc, pt = piece
    used = sum(1 for p in board.values() if p == (pc, pt))
    return max(0, PIECE_MAX.get(pt, 1) - used)


def edit_action_rects():
    rects, x = [], 10
    for key, label, width in EDIT_ACTIONS:
        rects.append((pygame.Rect(x, EDIT_BAR2_Y, width, 30), (key, label)))
        x += width + 8
    return rects


def library_panel(visible=LIB_PAGE_SIZE):
    """残局库浮层：最多一屏 20 行；条目少时面板跟着收短，不留大片空白"""
    visible = max(1, min(int(visible or 1), LIB_PAGE_SIZE))
    h = 62 + visible * LIB_ROW_STEP + 50      # 多留一行给底部筛选按钮
    return pygame.Rect(40, LIB_PANEL_TOP, SCREEN_W - 80, h)


# 残局库的「阶段」档位：按盘上双方棋子总数分 开局 / 中局 / 残局。
# 原来这里是 ≤4子 / 5-8子 / ≥9子 的子数档，用着不直观；
# 改成阶段后一眼能挑「我要练开局还是残局」。
LIB_PIECE_BANDS = ["全部", "开局", "中局", "残局"]


def entry_stage(entry):
    """按盘上双方棋子总数判阶段：≥20 子算开局，11-19 子算中局，≤10 子算残局。
    （219 局实测分布：开局 29、中局 76、残局 114，三档都有货）"""
    n = len(entry.get("pieces") or [])
    if n >= 20:
        return "开局"
    if n >= 11:
        return "中局"
    return "残局"


def piece_band_ok(count, band):
    """兼容旧调用：count 仍是子数，band 是阶段名"""
    if band in ("开局", "中局", "残局"):
        n = int(count)
        if band == "开局":
            return n >= 20
        if band == "中局":
            return 11 <= n <= 19
        return n <= 10
    return True


def position_signature(entry):
    """残局指纹：棋子布局（排序后）+ 先行方。
    同一个局面哪怕名字不一样，也算同一局 —— 导入时用它去重。"""
    cells = []
    for item in entry.get("pieces") or []:
        try:
            cells.append((int(item["r"]), int(item["c"]),
                          str(item["color"]), str(item["type"])))
        except (KeyError, TypeError, ValueError):
            continue
    cells.sort()
    return (tuple(cells), entry_turn(entry))


# 残局难度三档 + 分档阈值（按 118 局实测分值分布卡出来的三等分点，见 _tools\难度调研.py）
LIB_LEVELS = ["全部", "简单", "中等", "困难"]
LIB_LEVEL_SIMPLE = -1.30     # 不低于此分算「简单」
LIB_LEVEL_MID = -6.00        # 不低于此分算「中等」，再低算「困难」
LIB_LEVEL_COLORS = {"简单": (70, 160, 100), "中等": (222, 158, 44), "困难": (198, 82, 70)}
LIB_LEVEL_SHORT = {"简单": "易", "中等": "中", "困难": "难"}
_DIFF_CACHE = {}             # 局面指纹 -> 难度（一屏 20 行 × 每帧都要用，必须缓存）


def _side_material(board, color):
    """某一方的子力总分（不含将帅）"""
    return sum(PIECE_VALUES.get(pt, 0) for (pc, pt) in board.values()
               if pc == color and pt != KING)


def find_mate_in_one(board, turn):
    """一步将死的那一手（没有则 None）。残局里「看得见杀就该杀」，
    别把这几层深度浪费在搜索上 —— 一手杀是白拿的。
    就地走子再撤销，不复制整盘（这个函数在残局库筛难度时会被叫上百次）。"""
    enemy = opponent(turn)
    for mv in legal_moves(board, turn):
        fr, fc, tr, tc = mv[0], mv[1], mv[2], mv[3]
        piece = board[(fr, fc)]
        victim = board.get((tr, tc))
        board[(tr, tc)] = piece
        del board[(fr, fc)]
        try:
            if in_check(board, enemy) and not legal_moves(board, enemy):
                return mv
        finally:
            board.pop((tr, tc))
            board[(fr, fc)] = piece
            if victim is not None:
                board[(tr, tc)] = victim
    return None


def mate_in_one(board, turn):
    """先手方有没有「一步将死」——有的话这局基本一眼能看出来"""
    return find_mate_in_one(board, turn) is not None


def entry_difficulty(entry):
    """按「先手方」的处境给这局定难度档：简单 / 中等 / 困难。

    解题的人永远是先手一方，所以只从先手方的角度算：
      · 先手方比对方多多少子力 —— 领先得多、能兑子收束，好下；少子硬做，难；
      · 先手方有没有一步杀 —— 一眼就能看到正解，简单；
      · 先手方是不是正被别人将军 —— 第一步就得应付，更难；
      · 盘上棋子越多，可挑选的着法越多，越难找出那唯一一路；
      · 反过来，先手方已经把对方将住了，说明攻势已经到位，容易。
    算出来的分拿库里实测的分档阈值切成三档，两套主题、两次筛选结果都一样。"""
    sig = position_signature(entry)
    hit = _DIFF_CACHE.get(sig)
    if hit is not None:
        return hit
    try:
        board = record_to_board(entry.get("pieces") or [])
        turn = entry_turn(entry)
        enemy = opponent(turn)
        mine = _side_material(board, turn)
        theirs = _side_material(board, enemy)
        score = max(-5.0, min(5.0, (mine - theirs) / 150.0))
        score -= max(0, len(board) - 6) * 0.20
        if in_check(board, turn):
            score -= 3.0               # 第一步就得应付将军，谁都得先算清楚
        if in_check(board, enemy):
            score += 2.0
        if mate_in_one(board, turn):
            score += 5.0               # 真·一步杀（已验过对方无着可走），一眼就到
        # 子力相当、盘面又只剩几枚：这类多是「巧胜 / 巧和」的排局，
        # 每一步都得算到，比子力表上看着磨人
        if abs(mine - theirs) <= 200 and len(board) <= 12:
            score -= 1.6
        # 九宫空虚又对不上对方的重子：这种局面处处受制，比子力表上看着难
        guards = sum(1 for (pc, pt) in board.values()
                     if pc == turn and pt in (ADVISOR, ELEPHANT))
        heavy = any(pc == enemy and pt in (ROOK, CANNON) for (pc, pt) in board.values())
        if guards == 0 and heavy:
            score -= 1.5
    except Exception:                 # 坏条目别把整页拖垮，按中等算
        score = 0.0
    if score >= LIB_LEVEL_SIMPLE:
        level = "简单"
    elif score >= LIB_LEVEL_MID:
        level = "中等"
    else:
        level = "困难"
    _DIFF_CACHE[sig] = level
    return level


def _digit_runs(text):
    """把字符串里的连续数字切出来，例如 "第094局" → ["094"]"""
    runs, cur = [], []
    for ch in str(text):
        if ch.isdigit():
            cur.append(ch)
        elif cur:
            runs.append("".join(cur))
            cur = []
    if cur:
        runs.append("".join(cur))
    return runs


def library_name_hit(name, index, query):
    """搜索词是否命中某个残局。
    - 纯数字：按「局号」理解 —— 既认条目序号（从 1 数），也认名称里的数字串，
      并自动忽略前导零（输 94 能搜到「第094局」）。
    - 其他：按名称包含匹配。"""
    name = str(name or "")
    q = str(query or "").strip()
    if not q:
        return True
    if q.isdigit():
        want = int(q)
        if want == index + 1:          # 序号（列表里第几条）
            return True
        for run in _digit_runs(name):
            if int(run) == want:       # 名称里的局号，忽略前导零
                return True
        return False
    return q.lower() in name.lower()


def library_filter(entries, category="全部", query="", pieces="全部", level="全部"):
    """按分类 + 搜索词 + 阶段档位 + 难度档位筛出条目序号（供布局与计数共用）。
    没有分类字段的老条目一律算作「自定残局」，避免存了却在分项里找不到。"""
    q = (query or "").strip().lower()
    out = []
    for i, e in enumerate(entries):
        cat = e.get("category") or CUSTOM_CATEGORY
        if category == "收藏":
            if not e.get("fav"):
                continue
        elif category and category != "全部":
            if cat != category:
                continue
        if q and not library_name_hit(e.get("name", ""), i, q):
            continue
        if pieces and pieces != "全部":
            if not piece_band_ok(len(e.get("pieces") or []), pieces):
                continue
        if level and level != "全部":
            if entry_difficulty(e) != level:
                continue
        out.append(i)
    return out


def library_max_off(total):
    return max(0, total - LIB_PAGE_SIZE)


def library_layout(entries, off=0, category="全部", query="", pieces="全部",
                   level="全部"):
    """残局库浮层布局：返回 (面板, [(行Rect, 全量序号)], 起始序号, 总数, 滚动条)"""
    idxs = library_filter(entries, category, query, pieces, level)
    total = len(idxs)
    try:
        off = int(off or 0)
    except (TypeError, ValueError):
        off = 0
    off = max(0, min(off, library_max_off(total)))
    page_idxs = idxs[off:off + LIB_PAGE_SIZE]
    panel = library_panel(len(page_idxs))

    rows, y = [], panel.y + 62
    for full_i in page_idxs:
        rows.append((pygame.Rect(panel.x + 12, y, panel.w - 24 - 40, LIB_ROW_H), full_i))
        y += LIB_ROW_STEP

    scroll = None
    if total > LIB_PAGE_SIZE:
        track_x = panel.right - 12
        track_top = panel.y + 62
        track_bottom = panel.y + 62 + LIB_PAGE_SIZE * LIB_ROW_STEP - 4
        track_h = max(1, track_bottom - track_top)
        thumb_h = max(26, int(track_h * LIB_PAGE_SIZE / max(1, total)))
        ratio = off / max(1, library_max_off(total))
        ty = track_top + (track_h - thumb_h) * ratio
        scroll = (pygame.Rect(track_x, track_top, 8, track_h),
                  pygame.Rect(track_x, ty, 8, thumb_h))
    return panel, rows, off, total, scroll


def library_scroll_off(scroll, total, mouse_y, grab):
    """拖动滚动条：按鼠标位置换算起始序号"""
    track, thumb = scroll
    y = mouse_y - grab
    ratio = (y - track.y) / max(1, (track.h - thumb.h))
    return max(0, min(library_max_off(total), int(round(ratio * library_max_off(total)))))


def library_search_rect(panel):
    return pygame.Rect(panel.right - 180, panel.y + 8, 164, 22)


def library_io_rects(panel):
    return (pygame.Rect(panel.right - 240, panel.y + 8, 54, 22),    # 导出库
            pygame.Rect(panel.right - 300, panel.y + 8, 54, 22),    # 导入库
            pygame.Rect(panel.right - 360, panel.y + 8, 54, 22))    # 恢复备份


def library_star_rect(row):
    """行尾的收藏按钮（做成方块按钮，好点也好认）"""
    return pygame.Rect(row.right - 36, row.y + 2, 32, row.h - 4)


# 行内各列宽度（从左到右：编号 | 难度 | 名称 … 状态 | 存盘 | ★ ×）
# 出处列与行尾「改」按钮按用户意见撤掉：来源不写了，改名也不要了。
LIB_COL_NO_W = 28          # 编号区固定 28px 宽，三位数（100+）也压不到难度字
LIB_COL_STAT_W = 46
LIB_COL_TIME_W = 34
LIB_COL_GAP = 8


def library_row_columns(row):
    """返回 (名称区右边界, 状态列x, 存盘列x)"""
    stat_x = row.right - 76 - LIB_COL_STAT_W
    time_x = stat_x - LIB_COL_GAP - LIB_COL_TIME_W
    return stat_x - LIB_COL_GAP, stat_x, time_x


def library_delete_rect(row):
    return pygame.Rect(row.right + 6, row.y + 2, 30, row.h - 4)


def library_view(entries, category, query="", pieces="全部", level="全部"):
    """返回当前分类 + 搜索词 + 阶段 / 难度档位下的残局条目（全量，供计数使用）"""
    return [entries[i] for i in library_filter(entries, category, query, pieces, level)]


def library_page_rects(panel, total):
    """上翻 / 下翻一整屏"""
    if total <= LIB_PAGE_SIZE:
        return None, None
    y = panel.bottom - 50
    return (pygame.Rect(panel.x + 12, y, 62, 22),
            pygame.Rect(panel.right - 74, y, 62, 22))


def library_filter_rects(panel):
    """底部的两个筛选按钮：阶段档位 / 难度档位（与上翻下翻排在同一行，居中）"""
    y = panel.bottom - 50
    w, gap = 104, 10
    x = panel.x + (panel.w - (w * 2 + gap)) // 2
    return (pygame.Rect(x, y, w, 22), pygame.Rect(x + w + gap, y, w, 22))


def library_piece_rect(panel):
    """「阶段」筛选按钮：点一下换一档（全部 → 开局 → 中局 → 残局）"""
    return library_filter_rects(panel)[0]


def library_level_rect(panel):
    """「难度」筛选按钮：点一下换一档（全部 → 简单 → 中等 → 困难）"""
    return library_filter_rects(panel)[1]


def library_category_rects(panel, categories):
    """分类切换标签（全部 / 经典残局 / 江湖排局 / 自定残局 / 收藏）。
    筛选按钮搬到底部后，右侧那块留白用来写「筛出多少局」。"""
    rects = []
    avail = panel.w - 28 - 96
    w = avail // len(categories)
    for i, cat in enumerate(categories):
        rects.append((pygame.Rect(panel.x + 14 + i * w, panel.y + 34, w - 6, 20), cat))
    return rects


def player_panel_rect(side):
    # v1.5：面板加高到 50 / 54，靠棋盘那条边留出一条「轮走箭头带」
    if side == BLACK:
        return pygame.Rect(14, CONTROL_H + 4, SCREEN_W - 28, 50)
    return pygame.Rect(14, BOARD_ORIGIN_Y + BOARD_PX_H + 2, SCREEN_W - 28,
                       RED_PANEL_H)


BOTTOM_Y = 832
BOTTOM_H = 26
RED_PANEL_H = 58          # 红方（下方）计时面板高度：手机版压到 46 好腾出两排按钮
BOTTOM_ROW1_Y = 832       # 手机版第一排按钮的 y（桌面版只有一排，沿用 BOTTOM_Y）
BOTTOM_ROW_H = 26

# 手机专属放大：启动时按真实屏幕尺寸判定（见 main 里的 set_ui_mode）。
# 逻辑画布固定 572 宽，手机 1080 宽时整体放大 1.9 倍，按钮仍显小，
# 所以手机版把顶栏、底栏、主页按钮都单独加高加宽，字号也提一档。
UI_BIG = False


def set_ui_mode(big):
    """切换手机 / 桌面两套尺寸。只改底栏与下方面板的高度，不动棋盘坐标。"""
    global UI_BIG, BOTTOM_Y, BOTTOM_H, RED_PANEL_H, BOTTOM_ROW1_Y, BOTTOM_ROW_H
    UI_BIG = bool(big)
    if UI_BIG:
        # 手机：底部九格挤在一排时每格只有 56 逻辑像素（物理约 105），指头按不准，
        # 改成两排 —— 上排常用五格（悔棋/提示/复盘/存局/返回），下排四格。
        # 红方面板相应从 58 压到 46，让出来的高度给第二排按钮。
        BOTTOM_Y, BOTTOM_H = 828, 36
        RED_PANEL_H = 46
        BOTTOM_ROW1_Y, BOTTOM_ROW_H = 796, 32
    else:
        BOTTOM_Y, BOTTOM_H = 832, 26
        RED_PANEL_H = 58
        BOTTOM_ROW1_Y, BOTTOM_ROW_H = 832, 26


def bottom_button_rects():
    """底部功能栏：悔棋/复盘/提示/存局/认输/提和/棋谱/重开/返回。
    音乐开关与音效一起挪到顶栏，底栏腾出的宽度全给按钮。
    手机版排成两排：上排 悔棋/提示/复盘/存局/返回，下排 认输/提和/棋谱/重开。
    「返回」等同键盘 Esc / 手机返回键：回主页，不存半局。"""
    if UI_BIG:
        rows = (("undo", "hint", "replay", "save", "home"),
                ("surrender", "draw", "export", "restart"))
        out, gap = [], 8
        for ri, keys in enumerate(rows):
            y = BOTTOM_ROW1_Y + ri * (BOTTOM_ROW_H + 4)
            n = len(keys)
            w = (SCREEN_W - 16 - gap * (n - 1)) // n
            for i, key in enumerate(keys):
                out.append((pygame.Rect(8 + i * (w + gap), y, w, BOTTOM_ROW_H), key))
        return out
    y = BOTTOM_Y
    keys = ["undo", "replay", "hint", "save", "surrender",
            "draw", "export", "restart", "home"]
    x0, gap = 8, 6
    w = (SCREEN_W - x0 * 2 - gap * (len(keys) - 1)) // len(keys)
    return [(pygame.Rect(x0 + i * (w + gap), y, w, BOTTOM_H), key)
            for i, key in enumerate(keys)]


def export_button_rect():
    for rect, key in bottom_button_rects():
        if key == "export":
            return rect
    return pygame.Rect(400, BOTTOM_Y, 56, BOTTOM_H)


BOTTOM_LABELS = {"undo": "悔棋", "replay": "复盘", "hint": "提示",
                 "save": "存局", "music": "音乐",
                 "surrender": "认输", "draw": "提和",
                 "export": "棋谱", "restart": "重开", "home": "返回"}


def bottom_label(key):
    """手机上的「返回」写全成「返回主菜单」——手机没有键盘，光写「返回」不知道回哪；
    桌面照旧写「返回」，窄按钮塞五个字反而挤。"""
    if key == "home":
        return "返回主菜单" if UI_BIG else "返回"
    return BOTTOM_LABELS.get(key, key)


def _vgrad(size, top, bot):
    """竖向渐变：先画一条 1×64 的色带再拉伸，比逐行算颜色快得多"""
    strip = pygame.Surface((1, 64))
    for i in range(64):
        strip.set_at((0, i), _mix(top, bot, i / 63.0))
    return pygame.transform.smoothscale(strip, (max(1, size[0]), max(1, size[1])))


def draw_button_face(screen, rect, fill, border, radius=8, active=False, border_w=1,
                     highlight=True):
    """有厚度的按钮：投影 + 竖向渐变 + 顶部高光 + 描边。
    比纯色块更有实体感，墨玉主题下也不会糊成一片。"""
    w, h = max(1, rect.w), max(1, rect.h)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 26), sh.get_rect(), 0, radius)
    screen.blit(sh, (rect.x + 1, rect.y + 2))
    face = _vgrad((w, h),
                  _mix(fill, (255, 255, 255), 0.16 if active else 0.11),
                  _mix(fill, (0, 0, 0), 0.06)).convert_alpha()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), 0, radius)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(face, rect.topleft)
    if highlight:
        hi = pygame.Surface((max(1, w - 10), 2), pygame.SRCALPHA)
        hi.fill((255, 255, 255, 62))
        screen.blit(hi, (rect.x + 5, rect.y + 2))
    draw_rect(screen, border, rect, border_w, radius)


def draw_bottom_buttons(screen, game_over=False, music_on=True):
    # 手机版字号提一档：底栏本来就窄，13 号在 1.9 倍缩放下仍偏小
    bfont = load_font(15 if UI_BIG else 13)
    sfont = load_font(12)
    for rect, key in bottom_button_rects():
        enabled = not (game_over and key in ("hint", "undo"))
        if key == "home":
            enabled = True
        label = bottom_label(key)
        fill = TH["panel_fill"] if enabled else TH["panel_idle"]
        draw_button_face(screen, rect, fill,
                         C((196, 186, 170)) if enabled else C((170, 164, 154)),
                         radius=8)
        col = TH["text"] if enabled else C((150, 144, 132))
        surf = bfont.render(label, True, col)
        if surf.get_width() > rect.w - 8:        # 「返回主菜单」这类长标签降一档字号
            surf = sfont.render(label, True, col)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))


def replay_button_rects():
    y = BOTTOM_Y
    gap = 8
    w = (SCREEN_W - 20 - gap * 3) // 4
    return [(pygame.Rect(10 + i * (w + gap), y, w, BOTTOM_H), key)
            for i, key in enumerate(("prev", "next", "auto", "quit"))]


def draw_replay_controls(screen, index, total, auto):
    bfont = load_font(14)
    labels = {"prev": "上一手", "next": "下一手",
              "auto": "自动" if not auto else "暂停", "quit": "退出复盘"}
    for rect, key in replay_button_rects():
        enabled = True
        if key == "prev" and index <= 0:
            enabled = False
        if key == "next" and index >= total:
            enabled = False
        draw_rect(screen, C((250, 246, 238)) if enabled else C((236, 232, 224)), rect, 0, 8)
        draw_rect(screen, C((196, 186, 170)) if enabled else C((206, 202, 194)), rect, 1, 8)
        surf = bfont.render(labels[key], True,
                            C((92, 82, 68)) if enabled else C((176, 168, 154)))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))


def naming_panel_rect(mode="save"):
    """命名浮层：改名模式多一行「先行方」与条目详情，面板加高"""
    if mode == "rename":
        return pygame.Rect(50, 232, SCREEN_W - 100, 196)
    return pygame.Rect(50, 250, SCREEN_W - 100, 156)


def naming_turn_rect(panel=None):
    """改名浮层里的「先行方」开关（红先 / 黑先）"""
    p = panel or naming_panel_rect("rename")
    return pygame.Rect(p.x + 16, p.y + 96, 108, 28)


def draw_edit_scene(screen, board, edit_piece, message, difficulty, sound_on,
                    move_limit=0, music_on=True):
    draw_board(screen)
    draw_pieces(screen, board, None)
    draw_control_bar(screen, difficulty, sound_on, True, move_limit,
                     music_on=music_on)

    # 全盘棋子底板：每方 16 枚，摆一枚少一枚
    font = load_font(15)
    lab = load_font(12)
    for row, (color, label) in enumerate(((RED, "红"), (BLACK, "黑"))):
        tag = lab.render(label, True, C((176, 44, 44)) if color == RED else C((40, 40, 46)))
        screen.blit(tag, (8, PALETTE_ROWS[row] + 7))
    marked = False
    slots = palette_rects(board)
    for row in (0, 1):
        if not any(avail for r, _p, avail in slots if r.y == PALETTE_ROWS[row]):
            hint = lab.render("（棋子已全部摆上盘）", True, C((170, 158, 140)))
            screen.blit(hint, (PALETTE_X0, PALETTE_ROWS[row] + 7))
    for rect, piece, avail in slots:
        if not avail:                       # 已摆上棋盘：底板上就少这一枚
            continue
        cx, cy = rect.centerx, rect.centery
        ring = C((176, 44, 44)) if piece[0] == RED else C((40, 40, 46))
        pygame.draw.circle(screen, C((252, 240, 212)), (cx, cy), 13)
        pygame.draw.circle(screen, C((120, 92, 60)), (cx, cy), 13, 1)
        pygame.draw.circle(screen, ring, (cx, cy), 11, 2)
        if edit_piece == piece and not marked:   # 标出即将被消耗的这一枚
            pygame.draw.circle(screen, C((24, 150, 96)), (cx, cy), 15, 2)
            marked = True
        txt = font.render(CHINESE_PIECES[piece], True, ring)
        screen.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    # 操作按钮
    bfont = load_font(15)
    for rect, (key, label) in edit_action_rects():
        active = (key == "erase" and edit_piece == "erase")
        draw_button_face(screen, rect,
                         C((34, 150, 96)) if active else C((250, 246, 238)),
                         C((34, 150, 96)) if active else C((196, 186, 170)),
                         radius=8, active=active)
        surf = bfont.render(label, True, C((255, 255, 255)) if active else C((92, 82, 68)))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))

    mfont = load_font(14)
    for i, line in enumerate(wrap_text(message, mfont, SCREEN_W - 24)[:2]):
        screen.blit(mfont.render(line, True, C((80, 68, 54))), (12, EDIT_MSG_Y + i * 16))


def draw_library_overlay(screen, entries, edit_message, off=0, category="全部",
                         del_pending=None, query="", search_focus=False,
                         caret_on=False, io_msg="", pieces="全部", level="全部"):
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 110))
    screen.blit(shade, (0, 0))

    panel, rows, off, total, scroll = library_layout(entries, off, category, query,
                                                     pieces, level)
    draw_rect(screen, C((252, 249, 242)), panel, 0, 12)
    draw_rect(screen, C((34, 150, 96)), panel, 2, 12)

    first = off + 1 if total else 0
    last = min(off + LIB_PAGE_SIZE, total)
    title = load_font(15).render(
        "残局库  %d 局" % len(entries), True, C((60, 52, 42)))
    screen.blit(title, (panel.x + 14, panel.y + 10))

    # 搜索框 + 导出 / 导入整库
    sfield = library_search_rect(panel)
    draw_rect(screen, C((255, 255, 255)), sfield, 0, 6)
    draw_rect(screen, C((34, 150, 96)) if search_focus else C((196, 186, 170)),
              sfield, 2 if search_focus else 1, 6)
    qfont = load_font(12)
    qtxt = query or "搜名称或局号…"
    qsurf = qfont.render(qtxt, True, C((60, 52, 42)) if query else C((168, 158, 142)))
    while qsurf.get_width() > sfield.w - 14 and qtxt:
        qtxt = qtxt[1:]
        qsurf = qfont.render(qtxt, True, C((60, 52, 42)))
    screen.blit(qsurf, (sfield.x + 6, sfield.centery - qsurf.get_height() // 2))
    if search_focus and caret_on:
        cx = sfield.x + 8 + qsurf.get_width()
        pygame.draw.line(screen, C((34, 150, 96)), (cx, sfield.y + 5),
                         (cx, sfield.bottom - 5), 1)

    io_font = load_font(12)
    for rect, text in zip(library_io_rects(panel), ("导出库", "导入库", "恢复")):
        draw_rect(screen, C((250, 246, 238)), rect, 0, 6)
        draw_rect(screen, C((196, 186, 170)), rect, 1, 6)
        surf = io_font.render(text, True, C((92, 82, 68)))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))

    # 分类切换标签
    cfont = load_font(12)
    for rect, cat in library_category_rects(panel, LIB_CATEGORIES):
        active = (cat == category)
        draw_rect(screen, C((34, 150, 96)) if active else C((250, 246, 238)), rect, 0, 6)
        draw_rect(screen, C((34, 150, 96)) if active else C((196, 186, 170)), rect, 1, 6)
        surf = cfont.render(cat, True, K((255, 255, 255)) if active else C((92, 82, 68)))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))

    # 分类行右侧：筛选叠加后还剩多少局（没筛选时不显示，免得跟标题重复）
    cfont = load_font(12)
    if total != len(entries):
        cnt_s = load_font(11).render("筛出 %d 局" % total, True, C((146, 134, 118)))
        screen.blit(cnt_s, (panel.right - 14 - cnt_s.get_width(), panel.y + 37))

    # 阶段档位：点一下换一档（全部 → 开局 → 中局 → 残局）
    prect = library_piece_rect(panel)
    p_active = pieces != "全部"
    draw_rect(screen, C((34, 150, 96)) if p_active else C((250, 246, 238)), prect, 0, 6)
    draw_rect(screen, C((34, 150, 96)) if p_active else C((196, 186, 170)),
              prect, 1, 6)
    plabel = "阶段 " + ("全部" if not p_active else pieces)
    psurf = cfont.render(plabel, True,
                         K((255, 255, 255)) if p_active else C((92, 82, 68)))
    screen.blit(psurf, (prect.centerx - psurf.get_width() // 2,
                        prect.centery - psurf.get_height() // 2))

    # 难度档位：按先手方处境分 简单 / 中等 / 困难，点一下换一档
    lrect = library_level_rect(panel)
    l_active = level and level != "全部"
    draw_rect(screen, C((34, 150, 96)) if l_active else C((250, 246, 238)), lrect, 0, 6)
    draw_rect(screen, C((34, 150, 96)) if l_active else C((196, 186, 170)),
              lrect, 1, 6)
    lsurf = cfont.render("难度 " + (level or "全部"), True,
                         K((255, 255, 255)) if l_active else C((92, 82, 68)))
    screen.blit(lsurf, (lrect.centerx - lsurf.get_width() // 2,
                        lrect.centery - lsurf.get_height() // 2))

    name_font = load_font(15)
    meta_font = load_font(11)
    star_font = load_font(15)
    no_font = load_font(12)
    for row_i, (rect, idx) in enumerate(rows):
        entry = entries[idx]
        done = bool(entry.get("done"))
        draw_rect(screen, C((238, 248, 240)) if done else C((255, 255, 255)), rect, 0, 8)
        draw_rect(screen, C((120, 176, 132)) if done else C((206, 196, 180)), rect, 1, 8)

        # 行号：按当前筛选结果的顺序编号。编号区固定 LIB_COL_NO_W 宽并右对齐，
        # 这样第 100 局以后变成三位数也不会压到后面的难度字上。
        no_s = no_font.render("%02d" % (off + row_i + 1), True, C((146, 134, 118)))
        screen.blit(no_s, (rect.x + LIB_COL_NO_W - 4 - no_s.get_width(),
                           rect.centery - no_s.get_height() // 2))

        # 难度：编号后面一个字（易 / 中 / 难），绿 / 橙 / 红
        lv = entry_difficulty(entry)
        lv_s = load_font(11).render(LIB_LEVEL_SHORT.get(lv, "·"), True,
                                    C(LIB_LEVEL_COLORS.get(lv, (160, 150, 136))))
        screen.blit(lv_s, (rect.x + LIB_COL_NO_W + 2,
                           rect.centery - lv_s.get_height() // 2))

        srect = library_star_rect(rect)
        drect = library_delete_rect(rect)
        name_right, stat_x, time_x = library_row_columns(rect)
        day = stamp_day(entry_saved_at(entry))
        name_x = rect.x + LIB_COL_NO_W + 18

        # 名称：去掉自带的「第001局」，避免与行号重复
        nm = entry.get("name", "未命名")
        stripped = re.sub(r"^第\s*[0-9一二三四五六七八九十百]+\s*局[\s·]*", "", nm)
        if stripped:
            nm = stripped
        nm_col = C((24, 132, 76)) if done else C((58, 50, 40))
        nm_s = fit_text(nm, name_font, name_right - name_x, nm_col)
        screen.blit(nm_s, (name_x, rect.centery - nm_s.get_height() // 2))

        # 状态列：已通关（绿）/ 黑先（橙）/ 子数（灰）
        if done:
            dm = int(entry.get("done_moves") or 0)
            # 钩号在部分中文字体里是方框，改成「胜 N 手」最稳
            stat = ("胜%d手" % dm) if dm else "已通关"
            stat_col = C((24, 132, 76))
        elif entry_turn(entry) == BLACK:
            stat, stat_col = "黑先", C((176, 106, 24))
        else:
            stat, stat_col = "%d子" % len(entry.get("pieces", [])), C((146, 134, 118))
        stat_s = fit_text(stat, meta_font, LIB_COL_STAT_W, stat_col)
        screen.blit(stat_s, (stat_x, rect.centery - stat_s.get_height() // 2))

        # 存盘列：自存条目显示月-日，排局集条目没有存盘时间就留空
        if day:
            day_s = meta_font.render(day, True, C((132, 122, 106)))
            screen.blit(day_s, (time_x, rect.centery - day_s.get_height() // 2))

        # 收藏按钮（★ 明显一点，点一下收藏 / 再点取消）
        fav = bool(entry.get("fav"))
        draw_rect(screen, C((250, 238, 206)) if fav else C((244, 240, 232)), srect, 0, 6)
        draw_rect(screen, C((214, 168, 66)) if fav else C((204, 196, 182)), srect, 1, 6)
        star = star_font.render("★" if fav else "☆", True,
                                C((198, 142, 26)) if fav else C((170, 162, 148)))
        screen.blit(star, (srect.centerx - star.get_width() // 2,
                           srect.centery - star.get_height() // 2))

        if del_pending == idx:
            draw_rect(screen, C((176, 52, 48)), drect, 0, 8)
            cross = load_font(13).render("确认", True, K((255, 245, 235)))
        else:
            draw_rect(screen, C((232, 214, 208)), drect, 0, 8)
            cross = load_font(16).render("×", True, C((168, 60, 54)))
        screen.blit(cross, (drect.centerx - cross.get_width() // 2,
                            drect.centery - cross.get_height() // 2))

    if not rows:
        if query:
            tip = "没有符合条件的结果，换个关键词试试"
        elif (pieces and pieces != "全部") or (level and level != "全部"):
            tip = "这个阶段下没有残局，换个阶段或难度试试"
        elif category == "收藏":
            tip = "还没有收藏：点每行行尾的 ★ 即可收藏"
        elif category == CUSTOM_CATEGORY:
            tip = "还没有自定残局：对战中点「存局」，摆棋点「保存」"
        else:
            tip = "该分类暂无残局"
        empty = load_font(15).render(tip, True, C((140, 128, 112)))
        screen.blit(empty, (panel.x + 24, panel.y + 84))

    # 右侧滚动条
    if scroll:
        track, thumb = scroll
        draw_rect(screen, C((214, 206, 194)), track, 0, 4)
        draw_rect(screen, C((150, 140, 124)), thumb, 0, 4)

    # 底部：上翻 / 下翻 + 位置或操作提示
    prev_rect, next_rect = library_page_rects(panel, total)
    if prev_rect:
        for rect, text, enabled in ((prev_rect, "上翻", off > 0),
                                    (next_rect, "下翻", off < library_max_off(total))):
            draw_rect(screen, C((250, 246, 238)) if enabled else C((236, 232, 224)), rect, 0, 6)
            draw_rect(screen, C((196, 186, 170)), rect, 1, 6)
            surf = load_font(13).render(text, True,
                                        C((92, 82, 68)) if enabled else C((176, 168, 154)))
            screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                               rect.centery - surf.get_height() // 2))
    foot = io_msg or ("%d-%d / 共 %d 局　点行载入　★ 收藏　× 删除"
                      % (first, last, total))
    fcol = C((34, 130, 84)) if io_msg else C((128, 116, 100))
    fs = load_font(12).render(foot, True, fcol)
    if fs.get_width() > panel.w - 160:
        while fs.get_width() > panel.w - 160 and len(foot) > 4:
            foot = foot[:-2]
            fs = load_font(12).render(foot + "…", True, fcol)
    screen.blit(fs, (panel.centerx - fs.get_width() // 2,
                     panel.bottom - 24))


def draw_naming_overlay(screen, name_buf, caret_on, mode="save", turn=RED, detail=""):
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 130))
    screen.blit(shade, (0, 0))

    panel = naming_panel_rect(mode)
    draw_rect(screen, C((252, 249, 242)), panel, 0, 12)
    draw_rect(screen, C((34, 150, 96)), panel, 2, 12)

    caption = "重命名残局" if mode == "rename" else "给这局残局起个名字"
    title = load_font(17).render(caption, True, C((58, 50, 40)))
    screen.blit(title, (panel.x + 16, panel.y + 14))

    field = pygame.Rect(panel.x + 16, panel.y + 48, panel.w - 32, 40)
    draw_rect(screen, C((255, 255, 255)), field, 0, 8)
    draw_rect(screen, C((176, 166, 150)), field, 1, 8)

    font = load_font(18)
    shown = name_buf
    while font.size(shown)[0] > field.w - 24 and shown:
        shown = shown[1:]
    surf = font.render(shown, True, C((48, 42, 34)))
    screen.blit(surf, (field.x + 10, field.centery - surf.get_height() // 2))
    if caret_on:
        cx = field.x + 12 + surf.get_width()
        pygame.draw.line(screen, C((34, 150, 96)), (cx, field.y + 8), (cx, field.bottom - 8), 2)

    if mode == "rename":
        trect = naming_turn_rect(panel)
        red = (turn != BLACK)
        draw_rect(screen, C((238, 246, 240)) if red else C((236, 236, 240)), trect, 0, 8)
        draw_rect(screen, C((110, 176, 132)) if red else C((120, 124, 140)), trect, 1, 8)
        tlabel = load_font(13).render("先行：%s" % name_of(turn), True,
                                      C((30, 112, 66)) if red else C((64, 66, 78)))
        screen.blit(tlabel, (trect.centerx - tlabel.get_width() // 2,
                             trect.centery - tlabel.get_height() // 2))
        hint = load_font(11).render("点这里切换红先 / 黑先（人类执后手）", True, C((150, 138, 122)))
        screen.blit(hint, (trect.right + 10, trect.centery - hint.get_height() // 2))

        tfont = load_font(12)
        # 详情按「　」分段装行，避免把日期时间从中间截断
        lines, cur = [], ""
        for seg in [s for s in detail.split("　") if s]:
            trial = (cur + "　" + seg) if cur else seg
            if tfont.size(trial)[0] <= panel.w - 32:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = seg
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines[:2]):
            screen.blit(tfont.render(line, True, C((128, 116, 100))),
                        (panel.x + 16, panel.y + 132 + i * 18))
        tips = ["回车确认，Esc 取消；改名不影响局面、收藏与通关记录。"]
    else:
        tips = ["支持中文输入法直接输入，也可 Ctrl+V 粘贴；回车确认，Esc 取消。",
                "留空则使用自动命名（残局 月日-时分秒）。"]
    tfont = load_font(12)
    base = panel.y + (168 if mode == "rename" else 96)
    for i, line in enumerate(tips):
        screen.blit(tfont.render(line, True, C((120, 108, 92))),
                    (panel.x + 16, base + i * 18))


# ---------------------------- 主循环 ----------------------------
HUMAN_SIDE = RED
AI_SIDE = BLACK
DEFAULT_HUMAN = RED      # 未指定先行方时人类执红


def set_sides(human):
    """设定人类执子方（电脑执另一方）。黑先排局载入时人类执黑，其余照旧执红"""
    global HUMAN_SIDE, AI_SIDE
    HUMAN_SIDE = human if human in (RED, BLACK) else DEFAULT_HUMAN
    AI_SIDE = opponent(HUMAN_SIDE)
    return HUMAN_SIDE


def side_mark(color):
    """界面上的执子提示：人类一方加「你」"""
    return name_of(color) + ("（你）" if color == HUMAN_SIDE else "")



# ---------------------------- 主页 / 设置 / 说明 / 导入 浮层 ----------------------------
OVERLAY_PANEL = pygame.Rect(36, 64, SCREEN_W - 72, SCREEN_H - 96)      # (36,64,500,742)
OVERLAY_CLOSE = pygame.Rect(OVERLAY_PANEL.right - 42, OVERLAY_PANEL.y + 12, 30, 30)
# 设置面板按内容定制高度，避免底部大片留白
SETTINGS_PANEL = pygame.Rect(OVERLAY_PANEL.x, 70, OVERLAY_PANEL.w, 660)
SETTINGS_CLOSE = pygame.Rect(SETTINGS_PANEL.right - 42, SETTINGS_PANEL.y + 12, 30, 30)


def settings_slider_rects(p=None):
    """音效 / 音乐两条音量滑块的点击区（也用于绘制）"""
    p = p or SETTINGS_PANEL
    y = p.y + 240
    return (pygame.Rect(p.x + 96, y - 8, 140, 24),
            pygame.Rect(p.x + 336, y - 8, 140, 24))

_ASSET_DIR = _res_dir()
_HOME_CACHE = {}

HOME_BG_ANGLE = -11.0                  # 背景棋盘斜放角度（度），负值向左倾
HOME_BG_GAP = 46                       # 背景棋盘每格边长
HOME_BG_CENTER = (296, 486)            # 棋盘中心落在屏幕的位置（偏下，让开标题）
# 背景上的几枚棋子：(行, 列, 颜色, 兵种)。只摆下半盘（红方），
# 上半盘被按钮挡着，露半个子反而显脏。
HOME_BG_PIECES = [
    (6, 4, RED, PAWN), (7, 1, RED, CANNON), (7, 7, RED, HORSE),
    (9, 0, RED, ROOK), (9, 4, RED, KING), (9, 8, RED, ROOK),
]


def _bg_point(c, r, gap=None, angle=None, center=None):
    """棋盘行列 → 屏幕坐标：先按格间距铺开，再整体旋转、平移到屏幕中心"""
    gap = HOME_BG_GAP if gap is None else gap
    angle = HOME_BG_ANGLE if angle is None else angle
    cx, cy = HOME_BG_CENTER if center is None else center
    lx, ly = (c - 4) * gap, (r - 4.5) * gap
    rad = math.radians(angle)
    return (cx + lx * math.cos(rad) - ly * math.sin(rad),
            cy + lx * math.sin(rad) + ly * math.cos(rad))


def make_home_bg():
    """自绘主页背景《楚河汉界》：斜放的象棋盘 + 几枚棋子，全部按当前主题取色，
    原木主题是墨线，墨玉主题自动改用浅色线，深浅两套皮都好看。
    想换成自己的画：把图片命名成 主页背景.jpg 放程序目录，会优先用它。"""
    cache = _HOME_CACHE.setdefault("drawn", {})
    if THEME_CURRENT in cache:
        return cache[THEME_CURRENT]

    surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ink = TH["line"]
    river = TH["river"]
    face = TH["piece_face"]
    edge = TH["piece_edge"]
    red_ink = TH["accent_red"]
    dark = THEME_CURRENT == "墨玉"

    def line(p1, p2, alpha, width=1):
        pygame.draw.line(surf, ink + (alpha,), p1, p2, width)

    # 纸纹：细碎的深浅斑点，别太密
    rnd = random.Random(20261102)
    speck = (255, 255, 255) if dark else (120, 86, 52)
    for _ in range(900):
        x, y = rnd.randrange(SCREEN_W), rnd.randrange(SCREEN_H)
        r = rnd.choice((1, 1, 1, 2))
        pygame.draw.circle(surf, speck + (rnd.randrange(5, 13),), (x, y), r)

    # 棋盘：十条横线、九条竖线（河界处断开）、两个九宫的斜线
    # 墨玉主题的浅色线本来就扎眼，透明度再压低一点
    grid_a = 26 if dark else 34
    for r in range(BOARD_ROWS):
        line(_bg_point(0, r), _bg_point(8, r), grid_a)
    for c in range(BOARD_COLS):
        if c in (0, BOARD_COLS - 1):
            line(_bg_point(c, 0), _bg_point(c, 9), grid_a)
        else:
            line(_bg_point(c, 0), _bg_point(c, 4), grid_a)
            line(_bg_point(c, 5), _bg_point(c, 9), grid_a)
    for r1, c1, r2, c2 in ((0, 3, 2, 5), (0, 5, 2, 3), (7, 3, 9, 5), (7, 5, 9, 3)):
        line(_bg_point(c1, r1), _bg_point(c2, r2), grid_a - 6)
    # 外框加粗
    corners = [_bg_point(0, 0), _bg_point(8, 0), _bg_point(8, 9), _bg_point(0, 9)]
    pygame.draw.lines(surf, ink + (50,), True, corners, 3)

    # 楚河 · 汉界：字跟着棋盘一起斜
    river_font = load_font_song(24)
    for text, col in (("楚 河", 2.0), ("汉 界", 6.0)):
        glyph = river_font.render(text, True, river)
        glyph.set_alpha(62)
        glyph = pygame.transform.rotozoom(glyph, HOME_BG_ANGLE, 1.0)
        gx, gy = _bg_point(col, 4.5)
        surf.blit(glyph, (gx - glyph.get_width() / 2, gy - glyph.get_height() / 2))

    # 几枚棋子：投影 + 饼面 + 内圈 + 字（字单独转一次，避免歪掉）
    glyph_font = load_font_song(22)
    for r, c, pc, pt in HOME_BG_PIECES:
        x, y = _bg_point(c, r)
        rad = int(HOME_BG_GAP * 0.40)
        pygame.draw.circle(surf, (40, 30, 20, 26) if not dark else (0, 0, 0, 46),
                           (int(x) + 2, int(y) + 3), rad)
        pygame.draw.circle(surf, face + (105,), (int(x), int(y)), rad)
        pygame.draw.circle(surf, edge + (85,), (int(x), int(y)), rad, 2)
        pygame.draw.circle(surf, (red_ink if pc == RED else edge) + (80,),
                           (int(x), int(y)), rad - 5, 2)
        name = CHINESE_PIECES.get((pc, pt), "")
        if name:
            g = glyph_font.render(name, True, red_ink if pc == RED else edge)
            g.set_alpha(130)
            g = pygame.transform.rotozoom(g, HOME_BG_ANGLE, 1.0)
            surf.blit(g, (x - g.get_width() / 2, y - g.get_height() / 2))

    cache[THEME_CURRENT] = surf
    return surf


def load_home_bg():
    """主页背景：默认用程序自绘的《楚河汉界》象棋盘；
    若程序目录里有 主页背景.jpg，则优先用它（居中裁切铺满、半透明融入底色）。"""
    key = "file"
    if key in _HOME_CACHE:
        surf = _HOME_CACHE[key]
    else:
        surf = None
        path = os.path.join(_ASSET_DIR, "主页背景.jpg")
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert()
                target = SCREEN_W / SCREEN_H
                w, h = raw.get_width(), raw.get_height()
                if w / h > target:                     # 画面过宽：居中竖裁
                    nw = int(h * target)
                    raw = raw.subsurface(((w - nw) // 2, 0, nw, h))
                else:
                    nh = int(w / target)
                    raw = raw.subsurface((0, (h - nh) // 2, w, nh))
                surf = pygame.transform.smoothscale(raw, (SCREEN_W, SCREEN_H))
                surf.set_alpha(90)                     # 融入底色，不夺主体
            except (pygame.error, OSError):
                surf = None
        _HOME_CACHE[key] = surf
    return surf or make_home_bg()
    return surf


_SEAL_PNG_B64 = {
    "中": (
        "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"
        "QmCC"
    ),
    "国": (
        "iVBORw0KGgoAAAANSUhEUgAAAPoAAAD6CAQAAAAi5ZK2AAAAIGNIUk0AAHomAACAhAAA+gAAAIDo"
        "AAB1MAAA6mAAADqYAAAXcJy6UTwAAAACYktHRAD/h4/MvwAAAAd0SU1FB+oJBxUwOuhrRlYAABd1"
        "SURBVHja7Z15nB5Fmce/M/POmbmPnAKTQMJlCCFyhlWufDCAghyCrMCCuguIBlDQJeuuCPJhZbm8"
        "QBCCgGZFEFhQwplIgiQSoiQkISGBHGRyzn0f7/vuH3NkZt6q7urz7eq3f/2BvNNHdVX9+vdU1dPV"
        "T0GECBEiRIgQIUKECBEiRIgQIUKECBEiRIgQwU1kBSQfBRxEOWWUUUE+RQP7ugBI0gRAguaBs1vp"
        "G7qyieTAr8HjcVqI0xKRG0TSc5nB8RzHoRzEeA/Sj9NCguYR/yVpIkkTCZppoZU2WmmideBXRLqn"
        "dM/hEs6lNGC10UgbrbTRQtPAr2aaaaOFBuppoIHeiHQ7yOYC7mSKpvXVRaNgq2Mn9XRHpItxJAuZ"
        "HlKr2UbDwFZPA7vYwAa2DvU4Mpb0C1lAcUb1mTrYwAbW8wGr2RCUB8BP0i/gKbIzuNPcymqW8RZv"
        "sy9TSD+Wv1AYDZeAJOtZxCL+Qk+4SS9gHZMjvkeNFZ7hCd4MbwHnk4w24fYeVxILI+XjaIvoNdjW"
        "c7afdPjzjF3FGJMzNrGebdSxj84B52uMEgCKKaaEUsopoYRCysmjmDHkjXKq9A78Augb8K510wFA"
        "+0Dr2UyC/e7aXtoAhu446Ny9hvN9FsVhvMijzBvITyiQxSbpM97N05xHja10K6igwoMh4G/TpPe/"
        "2ayHQOIUaTEXMiGA+X3RkJp2GmjxiPZVphZRG/Mubq/6uJInA/mQlkn27+E2XmArAHlUU81EDmUa"
        "05jKga6Mg2byK74aDqX/Q/hUzw9sft8T5rfB8H1BIcdwBXfxMjscqn1OOHruCUHR6sgPbI63CMn4"
        "sfL1VZzKPBayzRbpoRi3ny8s2gOBdpqIcvxPNlKaxEXcyyqLtB+pP+m3Cgt2bYDHGnFhjsc5SLOW"
        "G1kqSTd1+77+pD8rLNjlgc1vqYQK513e8VyrpPqX9Cd9s2vG0h8cIMxv3LX0j+ePwl7O/u0T3Skv"
        "EBawZ2DqYxBxpJCITgspfI5X2c4CgzIezV8NSE+M8DZqiGnCYr0b4ByfJMyx+qTJq4fa7ocMzsrm"
        "bgPaP6U36XOEhfplgHM8V5jjDsWrrx/hYq40PPdvUtKP9raIXs9kqRXufTvApIv9cTlK1x7HT4b9"
        "lccMw7Ofkh6p0Jv0AyXPuG6k5ym0s+U8Re6IPUcYnv9mWEkfL3R+bAww6bK5+NWmV/6ag0btqTI8"
        "f31YSa+RtGX6kT7V5LofcUHKPuM5cK3sCSfpIn2sCnTXs0Sy/zSDawp5mB8I9ptNfPwoc0hfoyXp"
        "8zhYuD+fy1jH14XHmkzutVmyv9LbInr9Pl1k3lcHmvRSaQdvJQ/xBtvZRy9QxniO4LOcbdDab7NJ"
        "+ng0Ro7gJUNXwOd+LnJxJszBJvf6huS6FTqb90pB+muHfVuuk9Kto0naZg9C9qXLBJ1Jr9CuRZe3"
        "6dax1HSUsk9q3rP1Jb1auxbdTaX/1PQMGem53s6L9V/pqzNE6Q/zmm3SPTbwXrfpupn3bFeU3sTN"
        "XK1wXgMJyZGJ+g7ZUklvYXfAjXuOo+u7WMLTPGM6Qu9HnEaJq1Zj0quUR6ZBQbmtq+J8yD/4G8t5"
        "1+Lnx/US0ieESembAk56jSWq17OSd1jFGtpt3q85E8x70JU+Semsj1jEIha78MFha/hITzVdWwJO"
        "ulll17OQJ1ycD9CWCUrfEXDSDzE4tpu7eNC2Ic8YpetH+tGS/UkW8B3FPrkbpI8lx8Vp175in6vf"
        "iXiPHMknTQmu8eiOd0lf1nj4ps1b58xoR0cvewNN+imSIdu9nn1712rBSmpBeuGoaYLQJPVABQOy"
        "b8Pv9OyOoSO9VHlUGgzM5DLh/h4P2nKz3runU6b8Jb0pwJRP4EmJCzaPuWkgvTIi3WvMYanBLPVf"
        "8WmP7tsZmXf/kcXhXM9SXjGc2jSe5dxAgQf3706HeY8FTunFzGIG1dQwjpKBaHI5A2kNRnwbRMeI"
        "Shtc9kMWH274PfoXDjmYKYpUjuEevssCfu/yq+GudCg9FiilH8ddzHb4ctM7TGQ+89nOUt5mLZv4"
        "xIWPNjKAdGOlj+PVwC3wkYoDuJRLByxJHfvYRz3NtNBMM400D/1uj0hXUfpnNaB8pB/iYIOeQB+N"
        "7GEnO9lNHXvYwW52pjz2ctLLwkK68SonVYQJMWqoSYkU1cVKbuMVBdJLvMual733YsHTb4RGwo8C"
        "TuZFTlcgfYyepKfGXDFe4OrVjKAdcoe5dbstSEYL0sdYVHoD5wX+1as7OGaobrrCRnqRRdLhTaZx"
        "BX9gg67vkhWxP35Ul0FD4Fl/K+Yr6ebrF3bwOI8DBRxOLRWUU04F5eQDWSkvPrsG3JiD7pjBFVaT"
        "Q73kwZVY+508Y8gjmzKgkAL6vV79K7uWkkMuk3xZTSrJ/KGGLEGflIPiQL+rkODtlIkBXwh4jtd7"
        "Hsi/gQWcMOKenf4HFgua0tOL3RwmdaJ8n1JKKBtYVqSUYkrIV/AsJNlHPbtYxxreZ0VKHfRKHcHF"
        "OpJutSOXfuyRHunlfmkp8ykf1vQUkzvg9W8hTiv1JhNHev3vyvlLelbglW4d7bTT4OCeff6P1L2d"
        "LuXnI5Yu0p2ix0LzqOU4PSfgpO9Jwz3lSs/Xj/Q8ga4jpVtp0wv0I130nEZKD7nS833uNkZKj0gP"
        "AekhUXrQzXt7GlY7jZSeduyK2nS3Sc+NSHdYgxqSXhCRnoKk/6THNCU9l1omcgBjyRvyendQTz07"
        "+MjBVAw3u3KHMJcD+C3vGZ6V8L9N95d0p89uNkdyCifxaaYZLq/RwfusYDmvWv40epdLFvEsbmE2"
        "ABeYhAVO+k+6dzhH8Ib4Dgd0n8GD7Lb49rqPZcyzFCbs65KUuiykcTrvjghoUGh49hvS3D+mH+kX"
        "CIpxt62UiriODx1MXGjj54x18Kj2Pz6qJv25lGuNV395XZrvJ/TryMVcMlgX8gE/MwwAZIYxfJON"
        "ikv6ytr0HIXXwmP4b9ZybsqQrMGmeY+Fg3SrbXoBT/IHDnAhN2X8ggUKy2ztsk3BOazlZsEd6kwm"
        "UchJz/GTGneQ41jphbw60BlyB/9Cl2nAoN0kJZrON/CdTeJ+wVpN/Vhqe8iWkUr/pauUA1w9alJi"
        "KnqolxwplT7c81gnpRwesU16jn6kO1X6MVzhQa5+YHrGFkukn8BK7jOYHrmIxZlEulOlX+/JjLoz"
        "TXsIH0l7BaNRxcO8ZbgYboNC1Pc0mPeYr6SrK72ILwmNbwMNNFA/9G89TcRpIUkzVVRSxTRmc5z0"
        "m88cLuIeF0jP4iruNBmMdXMxWx2QHvR3kkKlOll66gzB1f9h4YE7V/CpRf9mZm5l7pkrh50zw3DR"
        "+8HFt9U+7fiTNIXFXlET1HH6yUJjqYo+nuckrhPOND3RZOAmU3rtwL8V3M9KTjTJwTZO5QWlvIa+"
        "I6feps8U7Gu1dP8kv+BiwRg5n6MMr/tQsn8ykMeNbOLbJo1inIeYoWzVQj9kU1e66POiFst5eE4Y"
        "4PMzhtdsl6yhdDo3sZG7TWPB/IkZ/JuFTw+T/nMTzN57DlMcK70fPxY4Vo81ueZd4d6J/CRlffTU"
        "K0/jHNZatEi+I5jmvUb4yNghvYOFAg+AMVbaKm8vN3Gsjc6XnPSscChddbqUeK2iFlv5+F3Knim2"
        "lI5Jo3Aq/5MO1QZf6apdE3GcqVZb+XgnJZJNqUm4rhWWyfuAWbxls54SYSI95oD0AheVDutS9hxo"
        "eH6dyQSn0fiEzwd88YI0k67WTuUJFWF3yZy10jG3DM9YSL2LMxX8bnaUrmGbLnYtqLXqog5fm+0W"
        "c3vKHrPAHg+bhDkcjjsEliRje+8xBw6HfNda9P7HZTTMQnDu5vuKabdII1RkZO89xwHpeR6Tbh7Y"
        "4z5OZZtC2s/b7mlkkNLtm3f7ldthg3RYwlyF6ZDL0BDekZ7lQOmis+yvfJhji3RYx6Om52x1XE85"
        "YTLvWQ6MWY+wl2wXBTZJhwWmZ8Q9JF1DpWc7cEWI+s6dtnNiP3L6StNGxfk65zEbgznNlB63rXT7"
        "pE9QeqhE6DNdsWWWh0rvCwvp9pVu37xPVnqoZIM3Y5ztIem9+pHuxLx3uar0WbaVjnRC9CAO4TTP"
        "zHtolB63XdV2lT5F4GlXJ9182scdDnvZkXk3MKrdNvNxkWCf+goS5aZnHM/5kdKNU1ZTuiiem72g"
        "mflc52h0rdI7v9vRykqR0gfQLDDm9pbv+q7w5Yoq6XlMVzjrIH4RdeSMSFf1NG8RVK11zOa/hPtV"
        "ST9KcYLXPzv4BCsDzLsq6asFfXCreT2ePwl9/b3KMWnOVb7Xg6afRmawecc26RUWO0xXsETS1q5R"
        "rM7YiK9azHr5zzI1UnqWy0qH+00+U9iP8TzDY9Lh1tuKqZzHJAvlHc9flPOXZqV7hxeE32epopQu"
        "wdU9/J5LTVr3Qr5Ho+FXZmpetCI2WY5u081CZlisJ3k0nQf1I/1FQTESDq8f3JpYzqPczDkcPEwp"
        "pXyO+9ljQky94nc2D9kMa9TL7ZYiY34sTeln+pEu+hrTyovIqxQrOUE9m9nMXhJK59+idPdDiTuI"
        "Z/UuhyqXc5s0lXv1I/3PDkkvthw1TmXbpPgu/QaH92lW7nbWSdO4KxxDNivzwdochBqUoYsvKwb3"
        "PtHhnUp5mp8ozROKhmyjxr6bXc1RN19mleK50yT7P+FZ/sgahcc3i5tYREUQh2ze4RVhJ8cajqbd"
        "NcPezOct3LlR2DhdP6TLg7iDZoW7fmA6em+SXvuf+pH+qgukw8WK3TOz7T2pdsXGWZTG7aPOGstj"
        "Crmr51TDe7U67HIGCq8Jx9nW8RWDJWjVtk5utRi2sFYYYbZU+FC2md6/h68Y3Eteupv1I/11l0iH"
        "2aZjb/kWZ6GNuLIzBCnJIshMV3Di9HGV9F490qtu1I/0N4QeK3uo4Tc2zHwHCzjc1v0+p2Dc96NC"
        "2JSN9iZ8S3K1vFzf1o/0xS6SDnA6qyzo+69821Kc95H4giDN6w3Oz+URhVxdKRw9yc+/Rj/SlzgM"
        "lS8m/n9N/Oo7WMjVll6UiHChDd3NN7VFPYJJlLkG53/DK2q8ixjpxUc5r/M6MU5gOkfxKSqppJce"
        "etjDDrayhrVKHx2aQ/QBpdnC1j/mQx4x9Pfl8jSzWT9qH2Eapy8V9qP1wJWCvKtMiTqUdSZqXztq"
        "HFFlcO4l+nnkdIZIf5MVrtvASbxoeMYR3Drib6OhZJd+pIvMuybRl4TmvVbpyia+yI2GHdbvjPDr"
        "FxiO4LUjPVtj0sUOG7VeSpJ7OYmN0uM5I96eFYaLdL86d15A9HAWKq/4BKuYxQPSR3w2Zwz9zg+/"
        "ec/RmHRVA9+PNq7lDOkqEdeHVenhI93qzPs3mM59woHXqUNteUEmKD0rQ5Q+qPcbOIY3U/YXDUWi"
        "Lgi/0nXRulukA6zhFC4a5ZLZPz4ojEgPCrpdJB2SPM10rhg2a2cv76TTvMci0pWre7yDFOM8zuN8"
        "hrM5gr38fCgqXlrMu3ekZ4dO6dWO012ZEku+0CAPGgYa8vshcxNijVV5cCe50jtAP9J1VrrYvBfZ"
        "DIxghEKDnr+GpIevTfdC6wXhIl1n8y4jvdpH0tt1JD0RKd0R6a06kh4PIenuKz1kbXqk9Axs0+Oh"
        "G7L526Z7SLp3JPQ5uF8ZuZQC5WRRTC4FFBIbsTx2sXRKYaPgrzgtdNNBBx3UK1SnTOnl4ejIxXxW"
        "eqp5P4rjqGUi5ZRTThkVlHv8Lq6behrYzmY2s5q3BbruJiG0gcUR6Xba9NGzz07nNd+Ndz4Tmcin"
        "h1T9GremuEe7hV2sMa7nJWQdObHSR1fb3LS33wWcwwq+pNSq+6n0EJNeRBCQnfL9SpdS7r1Uekt4"
        "Sf8kIP31k0bVRKdPpMttR3N4SB+t7DcCQnreqJ55h0/mXR7muElH0hNKWlnBU4EgvXuUOe3wRek5"
        "Bs1bU3iUPrraklzMWTxrIey+N3h8lF+h3RfSSwwGpx6a91iaSQd4iZfI4TCmcgi1jKeSKioZ4/p4"
        "vYd2kjTRSdOwbS/b2JgSF9of824Uw74pPKQXSc9eK1jyOkYJBRQC2SMiOheM6PWW0TJi/mrT0F8J"
        "moFmEnRYDIjQLhlgZbs6ianEoHFsCbfS5ehLm9kXKz2LMa6+8pQrvdW7GXL+d+SCMS63SzqWQv06"
        "Id3Thz070EpPH9rTTHpTRLr/6PSF9JJ09N29JL1Ha9Jlnu+8SOnWtVIeKX0Y5JMy9uhJurgrVBO1"
        "6cMgn361L0xKr9bkY+WONJNeHybSc22upBgpXWPzrouB7/ClI1cdkZ55Sq/MDPMOB0RKD695l7kX"
        "DtRa6W7WV5HBZClNSW/UmnSZ0t18DSJv0Xt19cg1hlLpbsa8nGSg86SepDdI9h+kidKTnitd3rvZ"
        "6W3hvGzTxRU0TYvI0wnJpAs3SZfbvE90JT0haZeKbIfmCkKr7qbZ/ZT0SJ2upMvHmkdq3Kr7Q/pO"
        "fUnfIdl/hMakJyKlG0PWMn1GY/PuT5u+Q1/St0v2z47adKCMCZmk9AkcrAHpXvfejRq5uvApHU7W"
        "lvQe19I/Snqky1snrLekfyw9cra2pLsXpHe2Qb0l9SV9g3Tp7LkWVzkODuluRWzN4hTpsc1eF81L"
        "0nvYIDlSPGzpmswkfaaBE1Zr0uF96ZHLA096j6ekn2dwTHPS10iPfMnANZEJbXqISV8uPRLjXwNO"
        "epfwQYi7kvYUphsc/Uhv0v9qoIxvGcwQC6rS/TDuCelqbpqQ3sUy6bFybtGuTXeL9K8aHPvQuwV7"
        "/CEdw9CA32SaZubdnUABM5lpcPQf3hfNa9KfN3A0FPCbAEeFFpn3Xa6k/DXDo3/Xn/QNBgYeTuDf"
        "tTLvbrznLuRSw+Or9Ccdfm149IecpZHS3SD9EirSrXTvUcQ+kgZbE4cHMt+XCvL6XcepxthoWBtb"
        "/Sia90rv4EeGx8t4hckBJL3FE6VfyVTD40sICXJNnu4kmwPonztZkM/THKZZwR6TmriM0OAsEiaF"
        "/ThwM+emCHLp9NF8yqQWugLusLKIu0yKm6TRsY7cRt2oHDodsM0zrYNnCBVivGla5F6+F6g4Fb8d"
        "lb8nHfba46Y1cCIhQzXvmRY6yYuMC0yOjx2Rs05mOUjrW/SZlv11Qohq/q5A+z5Dz7S/eGyYFTrP"
        "dirl/E6h3AmOJZSoYolC8ZO8PLSsTrrHHY8SJ8kHzLGZQhaXs0OpzE8QWsS4X6kK+njA4FNeP1Fp"
        "O3ZGNl9WatKSJNmjTbA1m/gqzUoV0cUDgXTbqA34fsRWRcKTJLmA0KOWxYqV0cdzzNEk9lw/yric"
        "xaZ+iZHbPWQEsrmBduVK+YjbOCzwZZrENbxMtyW6kyR5ye8VaNOpocn8ks9bOP99XuD/eMeleWpu"
        "II9qaphADZP5ArNs1eYyznRtRo4GpANcyk8tLlDdxnLe4i2We7msfAoKGMdExjKJGmoYz1hqGOuC"
        "0/RlLvRyrcVgkg5T+TOH2LguzmpWs4GNfMAmiyu0GKGISqqoYcIQzeMYb/IO3C4e4VoXv47TiHSo"
        "4VmHny/H2cJ26tjL3oH/d9NCD+0pC/YMLgVUQowKiqiikqqBrX+VqEKfSt3JdTxKBiPGnRb7u7pv"
        "yziUCJzP3gwhfAdXaRFhyxeM5enQE76P+dosaeIbzmVzaAn/mJs8WKI3FCjgFhpDRnc3f+DMyKQb"
        "o4LbaQkJ4eu5ibERpWooYZ6lVxZB2+Ks5IeOJl5kKHI5j2fo0ozudp7na0FWtw7vr8r5IpdxeuDz"
        "2skqlvEaS130D2Ys6f2YwlzmcMqIJbWDgWb+zhIWsyLoZOtH+qDv7jjO4AyOSeNody9bB7YtbGWr"
        "t0tkRqTvRw5TmclMZnKMpx8IxNnNTnaykzp2sp0tbPH7RWhEugjVTKaWWiZTy4FUUWVrIa12Gmmk"
        "gUZ2sos6dlHHTnZ7uXh9RLq7w70qqqmiFCgjm4IR787itACddNFINx0000ajLu1xhAgRIkSIECFC"
        "hAgRIkSIECFChAgRIkSIECF4+H/tyJnGgxHNLgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyNi0wOS0w"
        "N1QyMTo0ODo1OCswMDowMLkuN4cAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjYtMDktMDdUMjE6NDg6"
        "NTgrMDA6MDDIc487AAAAKHRFWHRkYXRlOnRpbWVzdGFtcAAyMDI2LTA5LTA3VDIxOjQ4OjU4KzAw"
        "OjAwn2au5AAAAABJRU5ErkJggg=="
    ),
    "象": (
        "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"
        "MjQ6MTgrMDA6MDDwfvIRAAAAAElFTkSuQmCC"
    ),
    "棋": (
        "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"
    ),
}


def _seal_image(name):
    """印章字形原图：优先用同目录的 印章_x.png；缺失就用内置的那份。
    安卓 APK 里只带 .py、没有这几张图，全靠内置数据兜底。"""
    path = os.path.join(_ASSET_DIR, "印章_%s.png" % name)
    if os.path.exists(path):
        try:
            return pygame.image.load(path)
        except (pygame.error, OSError):
            pass
    data = _SEAL_PNG_B64.get(name)
    if data:
        try:
            import base64 as _b64
            import io as _io
            raw = _b64.b64decode("".join(data))
            return pygame.image.load(_io.BytesIO(raw))
        except (pygame.error, OSError, ValueError):
            pass
    return None


def load_seal_glyphs():
    """小篆印章字形（透明底黑字 PNG → 白字），顺序：中/国/象/棋"""
    if "seal" in _HOME_CACHE:
        return _HOME_CACHE["seal"]
    glyphs = []
    for name in ("中", "国", "象", "棋"):
        g = None
        raw = _seal_image(name)
        if raw is not None:
            try:
                s = pygame.transform.smoothscale(raw.convert_alpha(), (28, 28))
                # 黑字转白字：RGB 拉满、透明度保持不变
                s.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                g = s
            except (pygame.error, OSError):
                g = None
        glyphs.append(g)
    _HOME_CACHE["seal"] = glyphs
    return glyphs


def draw_seal(screen):
    """右上角小篆印章：红底白字，右列「中/国」、左列「象/棋」"""
    seal = pygame.Rect(SCREEN_W - 92, 24, 68, 68)
    draw_rect(screen, (176, 52, 48), seal, 0, 4)
    draw_rect(screen, (252, 240, 212), seal.inflate(-8, -8), 1, 2)
    glyphs = load_seal_glyphs()
    fallback_font = None
    for path in (r"C:\Windows\Fonts\simkai.ttf", r"C:\Windows\Fonts\simsun.ttc"):
        if os.path.exists(path):
            try:
                fallback_font = pygame.font.Font(path, 26)
                break
            except (OSError, pygame.error):
                pass
    # (字, 列, 行)：右上=中，右下=国，左上=象，左下=棋（传统印章序）
    cells = [("中", 1, 0), ("国", 1, 1), ("象", 0, 0), ("棋", 0, 1)]
    for ch, col, row in cells:
        gx = seal.x + 4 + col * 32
        gy = seal.y + 4 + row * 32
        g = glyphs[("中国象棋".index(ch))]
        if g:
            screen.blit(g, (gx, gy))
        elif fallback_font:
            st = fallback_font.render(ch, True, (255, 245, 235))
            screen.blit(st, (gx + 14 - st.get_width() // 2,
                             gy + 14 - st.get_height() // 2))


def home_button_rects():
    """主页功能按钮：返回 [(rect, key, label, style), ...]
    手机版整排加高加大，并多一个「退出」——直接回手机桌面，
    不用再靠上滑手势（上滑会切到系统桌面，回来时偶发黑屏）。"""
    cx = SCREEN_W // 2
    if UI_BIG:
        bw, bh, gap = 340, 74, 18
        ys = [232, 324, 416, 508]
        sbw, sbh, sgap, sy = 158, 56, 10, 602
    else:
        bw, bh, gap = 300, 62, 20
        ys = [248, 330, 412, 494]
        sbw, sbh, sgap, sy = 140, 46, 10, 586
    x = cx - bw // 2
    out = []
    for y, key, label in zip(ys,
                             ["battle", "endgame", "edit", "import"],
                             ["对　战", "残　局", "摆　棋", "导　入"]):
        out.append((pygame.Rect(x, y, bw, bh), key, label, "primary"))
    total = sbw * 3 + sgap * 2
    sx = cx - total // 2
    for i, (key, label) in enumerate((("settings", "设　置"),
                                      ("instructions", "说　明"),
                                      ("quit", "退　出"))):
        out.append((pygame.Rect(sx + i * (sbw + sgap), sy, sbw, sbh),
                    key, label, "secondary"))
    return out


def draw_home(screen, bgm_name, hover=None):
    """古典风格主页：象棋盘水印背景、标题、功能按钮、小篆印章、版本落款"""
    screen.fill(BG_COLOR)
    bg = load_home_bg()
    if bg:
        screen.blit(bg, (0, 0))
    # 古典双线边框（墨玉主题下换成浅金，不然边框会糊在深底上）
    draw_rect(screen, C((120, 86, 52)),
              pygame.Rect(14, 14, SCREEN_W - 28, SCREEN_H - 28), 2, 12)
    draw_rect(screen, C((168, 128, 86)),
              pygame.Rect(20, 20, SCREEN_W - 40, SCREEN_H - 40), 1, 10)

    cx = SCREEN_W // 2
    # 标题
    draw_spaced_text(screen, "中 国 象 棋", cx, 116,
                     load_font_song(54), C((60, 42, 30)), gap=18)
    # 副标题
    sub = load_font_song(17).render("楚　河　汉　界　·　象　弈　之　道",
                                    True, C((126, 92, 58)))
    screen.blit(sub, (cx - sub.get_width() // 2, 164))
    # 小篆印章
    draw_seal(screen)
    # 分隔线
    pygame.draw.line(screen, (176, 52, 48), (cx - 120, 196), (cx + 120, 196), 2)

    # 功能按钮：实体卡片，鼠标移上去会亮起来并微微抬起
    for rect, key, label, style in home_button_rects():
        hot = hover is not None and rect.collidepoint(hover)
        box = rect.move(0, -1) if hot else rect
        if style == "primary":
            draw_button_face(screen, box, (255, 252, 246) if hot else (252, 248, 240),
                             (34, 150, 96), radius=10, active=hot, border_w=2)
            draw_rect(screen, (34, 150, 96),
                      pygame.Rect(box.x + 2, box.y + 6, 6, box.h - 12), 0, 3)
            surf = load_font(28 if UI_BIG else 26).render(label, True, (58, 46, 36))
        else:
            draw_button_face(screen, box, (246, 239, 226) if hot else (244, 236, 222),
                             (34, 150, 96) if hot else (196, 186, 170), radius=8, active=hot)
            surf = load_font(20 if UI_BIG else 18).render(label, True, (86, 74, 60))
        screen.blit(surf, (box.centerx - surf.get_width() // 2,
                           box.centery - surf.get_height() // 2))

    # 右下角版本与创作者（宋体小字）——向左提一格，不贴右边框
    ver = load_font_song(16 if UI_BIG else 13).render(
        "中国象棋·智算单机版 v%s　·　制作人：%s" % (VERSION, CREATOR), True, C((92, 68, 46)))
    screen.blit(ver, (SCREEN_W - 18 - HOME_CREDIT_DX - ver.get_width(), SCREEN_H - 46))
    # 左下角背景出处
    if bg:
        credit_txt = ("背景：主页背景.jpg" if _HOME_CACHE.get("file")
                      else "背景：程序自绘《楚河汉界》")
        credit = load_font_song(11).render(credit_txt, True, C((128, 100, 74)))
        screen.blit(credit, (20, SCREEN_H - 44))


def settings_hitboxes(state):
    """返回 ([(rect, 类别, 值), ...], panel)"""
    p = SETTINGS_PANEL
    items = []
    y = p.y + 74
    x = p.x + 26
    for val in ["简单", "普通", "困难", "大师"]:
        items.append((pygame.Rect(x, y, 64, 30), "difficulty", val))
        x += 72
    y = p.y + 136
    x = p.x + 26
    for val, b in [("开", True), ("关", False)]:
        items.append((pygame.Rect(x, y, 64, 30), "sound", b))
        x += 72
    # 背景音乐开关：紧接在音效开关下方，同样「开 / 关」两键
    y = p.y + 198
    x = p.x + 26
    for val, b in [("开", True), ("关", False)]:
        items.append((pygame.Rect(x, y, 64, 30), "bgm_on", b))
        x += 72
    # 音量滑块（点击或拖动轨道）
    s_rect, m_rect = settings_slider_rects(p)
    items.append((s_rect, "vol_sound", None))
    items.append((m_rect, "vol_music", None))
    y = p.y + 322
    x = p.x + 26
    for m in TIME_OPTIONS:
        items.append((pygame.Rect(x, y, 66, 30), "time", m))
        x += 74
    # 单步限时（秒）：只影响圆表计时与超时判定，不改变总包干时间
    y = p.y + 380
    x = p.x + 26
    for m in MOVE_TIME_OPTIONS:
        items.append((pygame.Rect(x, y, 66, 30), "move_time", m))
        x += 74
    # 曲目：每行 4 个、最多 BGM_MAX 个（曲 目录里放几首就多几个，自动换行）
    y = p.y + 438
    for i, name in enumerate(bgm_names()[:BGM_MAX]):
        col, row = i % 4, i // 4
        items.append((pygame.Rect(p.x + 26 + col * 100, y + row * 32, 96, 30),
                      "bgm", name))
    # 导入 / 删曲：放在「背景古曲」标题那一行的右端，曲目行保持一行 4 个
    items.append((pygame.Rect(p.right - 194, p.y + 412, 84, 26),
                  "music_import", "导入曲子"))
    items.append((pygame.Rect(p.right - 100, p.y + 412, 72, 26),
                  "music_delete", "删曲"))
    y = p.y + 532
    x = p.x + 26
    for label, val in UNDO_LIMITS:
        items.append((pygame.Rect(x, y, 62, 30), "undo", val))
        x += 70
    y = p.y + 590
    x = p.x + 26
    for name in THEME_NAMES:
        items.append((pygame.Rect(x, y, 76, 30), "theme", name))
        x += 84
    items.append((SETTINGS_CLOSE, "close", None))
    return items, p


def draw_settings_overlay(screen, state):
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 130))
    screen.blit(shade, (0, 0))
    p = SETTINGS_PANEL
    draw_rect(screen, C((252, 249, 242)), p, 0, 14)
    draw_rect(screen, C((34, 150, 96)), p, 2, 14)
    t = load_font_song(24).render("设　置", True, C((60, 48, 36)))
    screen.blit(t, (p.centerx - t.get_width() // 2, p.y + 30))
    draw_rect(screen, C((232, 214, 208)), SETTINGS_CLOSE, 0, 6)
    cross = load_font(18).render("×", True, C((168, 60, 54)))
    screen.blit(cross, (SETTINGS_CLOSE.centerx - cross.get_width() // 2,
                        SETTINGS_CLOSE.centery - cross.get_height() // 2))
    lfont = load_font(17)
    sfont = load_font(14)
    for y, text in [(p.y + 50, "对战难度"), (p.y + 112, "音效开关"),
                    (p.y + 174, "背景音乐开关"), (p.y + 298, "对战时间（分钟）"),
                    (p.y + 356, "单步限时（秒）"),
                    (p.y + 414, "背景古曲"), (p.y + 508, "悔棋限制"),
                    (p.y + 566, "棋盘配色")]:
        screen.blit(lfont.render(text, True, C((78, 64, 50))), (p.x + 24, y))
    # 音量滑块标签
    screen.blit(sfont.render("音效音量", True, C((96, 82, 66))), (p.x + 24, p.y + 232))
    screen.blit(sfont.render("音乐音量", True, C((96, 82, 66))), (p.x + 262, p.y + 232))
    # 曲目小提示：曲目录里有几首（有上限）、没文件的曲目用内置合成音
    n_music = len(music_library())
    tip = "曲目录 %d/%d 首：绿框是文件（选中后点「删曲」），灰框是合成" % (
        n_music, MUSIC_MAX_FILES)
    if len(bgm_names()) > BGM_MAX:
        tip += "　只看前 %d 首" % BGM_MAX

    items, _ = settings_hitboxes(state)
    bfont = load_font(14)

    def active(cat, val):
        if cat == "difficulty":
            return state["difficulty"] == val
        if cat == "sound":
            return bool(state["sound_on"]) == bool(val)
        if cat == "bgm_on":
            return bool(state["bgm_on"]) == bool(val)
        if cat == "time":
            return state["time_limit"] // 60 == val
        if cat == "move_time":
            return int(state.get("move_limit", 0)) == int(val)
        if cat == "bgm":
            return state["bgm"] == val
        if cat == "undo":
            return int(state.get("undo_limit", 0)) == val
        if cat == "theme":
            return THEME_CURRENT == val
        return False

    for rect, cat, val in items:
        if cat == "close":
            continue
        if cat in ("vol_sound", "vol_music"):
            draw_volume_slider(screen, rect,
                               state.get("sound_vol" if cat == "vol_sound"
                                         else "music_vol", 0.8))
            continue
        on = active(cat, val)
        action_off = False          # 动作按钮是否置灰（比如没选中文件曲目时的「删曲」）
        if cat in ("music_import", "music_delete"):
            # 动作按钮，不是开关：白底绿边；「删曲」在没选中文件曲目时置灰
            if cat == "music_delete":
                action_off = not (isinstance(state.get("bgm"), str)
                                  and has_music_file(state["bgm"]))
            draw_rect(screen, C((246, 250, 244)) if not action_off else C((242, 240, 234)),
                      rect, 0, 8)
            draw_rect(screen, C((34, 150, 96)) if not action_off else C((198, 192, 180)),
                      rect, 1, 8)
        elif cat == "bgm":
            real = has_music_file(val)
            draw_rect(screen, C((34, 150, 96)) if on else
                      (C((244, 240, 232)) if real else C((250, 246, 238))), rect, 0, 8)
            if on:
                edge = K((255, 255, 255)) if real else C((196, 186, 170))
            else:
                edge = C((34, 150, 96)) if real else C((196, 186, 170))
            draw_rect(screen, edge, rect, 2 if real else 1, 8)
            dot = (rect.right - 9, rect.y + 9)      # 右上角：实心＝曲 目录里的文件
            if real:
                pygame.draw.circle(screen, K((255, 255, 255)) if on else C((34, 150, 96)), dot, 3)
            else:
                pygame.draw.circle(screen, K((255, 255, 255)) if on else C((176, 166, 150)),
                                   dot, 3, 1)
        else:
            draw_rect(screen, C((34, 150, 96)) if on else C((250, 246, 238)), rect, 0, 8)
            draw_rect(screen, C((34, 150, 96)) if on else C((196, 186, 170)), rect, 1, 8)
        if isinstance(val, bool):
            label = "开" if val else "关"
        elif cat == "undo":
            label = {v: k for k, v in UNDO_LIMITS}.get(val, str(val))
        elif cat == "move_time":
            label = move_limit_label(val)
        else:
            label = str(val)
        col = K((255, 255, 255)) if on else C((86, 74, 60))
        if action_off:
            col = C((168, 160, 146))
        surf = (fit_text(label, bfont, rect.w - 18, col) if cat == "bgm"
                else bfont.render(label, True, col))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))

    # 底部一行：有操作回执就显示回执，没有就显示曲目提示
    msg = str(state.get("settings_msg") or "")
    line = msg or tip
    color = C((34, 150, 96)) if msg else C((150, 138, 122))
    ms = fit_text(line, load_font(12), p.w - 52, color)
    screen.blit(ms, (p.x + 26, p.y + 620))


def draw_volume_slider(screen, rect, value):
    """音量滑块：轨道 + 已填充部分 + 圆形滑块"""
    value = max(0.0, min(1.0, float(value)))
    y = rect.centery
    track = pygame.Rect(rect.x, y - 3, rect.w, 6)
    draw_rect(screen, C((214, 206, 192)), track, 0, 3)
    fill = pygame.Rect(track.x, track.y, int(track.w * value), track.h)
    draw_rect(screen, C((34, 150, 96)), fill, 0, 3)
    kx = track.x + int(track.w * value)
    pygame.draw.circle(screen, C((255, 255, 255)), (kx, y), 7)
    pygame.draw.circle(screen, C((34, 150, 96)), (kx, y), 7, 2)


# ---- 使用说明（多页浮层） ----
HELP_PANEL = pygame.Rect(36, (SCREEN_H - 700) // 2, SCREEN_W - 72, 700)   # 居中
HELP_CLOSE = pygame.Rect(HELP_PANEL.right - 42, HELP_PANEL.y + 12, 30, 30)
HELP_PREV = pygame.Rect(HELP_PANEL.x + 24, HELP_PANEL.bottom - 40, 96, 30)
HELP_NEXT = pygame.Rect(HELP_PANEL.right - 120, HELP_PANEL.bottom - 40, 96, 30)
HELP_TEXT_TOP = HELP_PANEL.y + 76
HELP_TEXT_BOTTOM = HELP_PANEL.bottom - 56
HELP_FONT_SIZE = 14
HELP_LH = 21

HELP_PARAS = [
    "欢迎使用《中国象棋·智算单机版 v%s》—— 计时对弈与残局研究。" % VERSION,
    "【两个版本】同一份程序，规则、AI、残局库、按钮文案完全一致，只在「怎么操作」上各让一步。"
    "安卓版：竖屏全屏、手指点选；底栏排成两排——上排 悔棋/提示/复盘/存局/返回主菜单，"
    "下排 认输/提和/棋谱/重开，格子比桌面版大一号，拇指够得着；冷启动有一段开机动画，"
    "棋子在转，等的时候不干等；设置、残局库、曲子都存在应用私有目录，不占相册、不用存储权限；"
    "设置里能直接导入曲子、删曲子，不用连电脑。"
    "桌面版：窗口可缩放，鼠标右键摆棋删子；导入曲子走系统文件对话框，能一次挑好几个文件；"
    "键盘 Esc 关浮层、回车确认；存档、棋谱、曲目录都在 exe 旁边，拷走就能搬去另一台机器。"
    "一句话：手机上胜在随手就能下，桌面上胜在摆棋、整理谱子方便。",
    "【对战】红方先行：点棋子再点落点，绿点可走、红圈可吃；电脑执黑，每方限时包干。"
    "轮到哪方走，他的将/帅旁边就亮起一只单步计时圆表：十二个刻度像座钟，指针一圈"
    "走完这一手的限时，圈心写这手还剩几秒，旁边一句「该你走」/「思考中…」；"
    "不走的一方不画表。将死、困毙定胜负；子力不足（双方只剩将帅士象，至多各一匹单马）"
    "立刻判和，不再磨到六十回合。六十回合无吃子判和。同一局面第 3 次出现时"
    "按整轮循环裁决：哪一方每一着都在将军，哪一方判长将负（被连将、只能来回躲帅的一方"
    "不受罚）；双方都不将军则判和。走子前会先拦住重复，留出换着法的余地；"
    "电脑也会另择路线，不主动长将。",
    "【和棋】除了规则判和，程序会自己开口提和：盘上只剩 8 枚子以内、或连续 40 个"
    "半回合没吃子、或同一局面反复出现，而它也没占到便宜时，会弹窗把盘面说清楚"
    "（我剩什么子、你剩什么子、多少回合没吃子），话很直白，不讲条文。"
    "点「同意和棋」就握手言和、这一局到此结束；点「继续下」接着走，"
    "过了几手它可能再提一次（间隔一次比一次长，约 6 / 12 / 18 个回合），一局最多提三回，"
    "第三回被拒就不再提。弹窗开着时计时暂停，慢慢看、慢慢决定；"
    "您也可以点「提和」主动找它和，它觉得自己没占到明显便宜就会答应。",
    "【认输】它只剩光杆老将、您手上还有车能破防时，先低头求和："
    "答应就和棋；不答应它就再撑 3 个回合，然后弹「认输」。认输弹窗里点"
    "「继续下」，这局就不算完 —— 它不再提和也不再认输，非得您把将吃掉（将死）才结束。",
    "【单步限时】设置面板与对战顶部栏的「步限」按钮都能调：不限 / 15 / 30 / 60 秒。"
    "选「不限」时圆表只正计时（指针 60 秒一圈，圈心写这一手用了多久）；设了限时则倒计时，"
    "剩 10 秒内圆表转红，一圈走完还没落子即判单步超时负。",
    "【残局】按 全部 / 经典残局 / 江湖排局 / 自定残局 / 收藏 切换；每行开头是编号"
    "（100 局以后是三位数，照样不挤），行尾 ★ 收藏、× 删除（点两次确认）；"
    "行内标「已通关 / 黑先 / 子数」和存盘日期。"
    "底下一行两个筛选按钮：「阶段」按盘上棋子多少分成 全部 / 开局 / 中局 / 残局"
    "（双方合计 20 子以上算开局，11-19 子算中局，10 子以下才算残局），"
    "想练开局还是专挑残局一眼就能分开；"
    "「难度」按钮按先手方（解题那方）的处境把每局分成 简单 / 中等 / 困难："
    "先手方子力领先得多、或有一眼就能看到的直接杀着，算简单；少子硬做、第一步就被将军、"
    "盘上着法又多得挑不出唯一正解，算困难。行号后面那道竖线就是难度色：绿 / 橙 / 红。"
    "搜索框里敲数字按局号找：输 94 能搜到「第094局」，输 3 也能定位列表第 3 条。"
    "↑↓ 逐行、PgUp/PgDn 整屏、Home/End 到两端；"
    "「导出库 / 导入库」备份或合并整库，写库前留 3 份 .bak；"
    "「恢复」用最近一份备份盖回当前库（4 秒内点两次才执行，覆盖前会把当前库另存一份），"
    "改乱了、误删了一片，点它就能退回去；"
    "导入按「局面 + 先行方」去重，同一个局面换个名字也不会重复堆一遍。",
    "【存局】对战、残局、摆棋都能存：底部「存局」（摆棋里「保存」），先按规则校验，"
    "再起名字，存入「自定残局」分类。",
    "【摆棋】棋子摆一枚少一枚。双方各须一枚将/帅、除将帅外至少一枚子，"
    "士象车马炮每方最多 2 枚、兵卒最多 5 枚；落点须合法（将帅士不出九宫、象不过河、"
    "兵卒不后退），将帅不得照面。",
    "【导入】粘贴整份棋谱全文（自动回放到最后一手）、FEN 或 JSON，或点「选文件」"
    "挑 棋谱 目录里的 .txt；载入后从最后一手接着下。对战中按 Esc 只回主页、不再存半局，"
    "要保局请在对局中点「存局」存进残局库（自定残局）。",
    "【走子】两种手法都行：点一下棋子再点落点；或者按住棋子直接拖到落点松手"
    "（拖动时棋子跟着鼠标走，落点有绿点提示）。走子有滑行动画，被吃的子会淡出，"
    "落定后荡开一圈涟漪；落子声上三路清脆、下三路低沉，听着像在真棋盘上敲。"
    "电脑算完不会立刻落子，至少「想」半秒，看得清它走哪。",
    "【对局按钮】手机上下两排：上排 悔棋 / 提示 / 复盘 / 存局 / 返回主菜单，"
    "下排 认输 / 提和 / 棋谱 / 重开（桌面是一排九个）；"
    "「提示」在后台深搜一手建议并标在棋盘上（约四五秒，界面不卡）；"
    "「提和」由电脑按形势决定；「音乐」开关挪到顶栏、紧挨着「音效」；"
    "「返回主菜单」等于退出这一局回主页，不存半局；"
    "悔棋次数可在设置里限定为不限 / 三次 / 五次。",
    "【难度】简单 / 普通 / 困难 / 大师四档：简单会随手走错，普通偶尔失手，"
    "困难与大师不失手、算得更深（大师每步最多算 8 层，约 5.5 秒），越往后防守越紧。"
    "v2.3 的电脑开局会照谱走（中炮、仙人指路、飞相、起马等常见开法都有应对），"
    "中局搜索换成 PVS + 后期着法削减 + 空着裁剪，同样节点数比上一版少算一成，"
    "折算下来同样时间能多算一两层；残局还会主动把对方将往边上赶，"
    "车兵残局这类「赢了但不会杀」的局能收下来了。"
    "走完一手后底部会写「电脑算到第 N 层」。",
    "【设置】难度、音效与音乐开关、音量滑块、对战总时间、单步限时、背景曲、悔棋限制、"
    "棋盘配色（原木 / 墨玉）都能调整并自动保存，墨玉下浮层也换成深色；"
    "电脑改在后台思考，算棋时窗口照常响应。主页背景想换成自己的画：把图片命名成 主页背景.jpg 放在程序目录即可。",
    "【自己加曲子】设置面板里点「导入曲子」，挑一首 mp3 / ogg / wav，最多收 4 首，"
    "导入后曲目行立刻多一个按钮（名字太长会自动截短，免得一格放不下）。"
    "想删：先点中那首导入的曲子，再点「删曲」，4 秒内点第二次即删（内置古曲删不掉）。"
    "也可以直接把文件丢进程序旁的 曲 目录，删掉即消失，不必改程序。"
    "内置四首古曲（高山流水 / 平沙落雁 / 渔舟唱晚 / 广陵散）"
    "在没有同名文件时用程序合成的旋律顶上。音效同理：音效 目录放 "
    "select.wav / 落子.wav / 吃子.wav / 将军.wav / 胜利.wav 即替换内置音效。",
    "【退出】按 Esc、点底部「返回」或点窗口关闭键都不会直接退出：浮层先关，"
    "对局先回主页；回到主页再点右下角「退出」才真正结束程序（手机上是回手机桌面）。",
    "【升级安装】手机换新版安装包时，系统若提示「签名不一致 / 无法覆盖安装」，"
    "是两版安装包签名不同，不是程序坏了。处理办法：先在残局库点「导出库」把库存到"
    "手机别的目录（卸载会清掉应用内的残局库.json、自定义曲子和音效），"
    "再在手机设置里卸载旧版，然后装新版，装完用「导入库」把库恢复即可。"
    "同一签名之后的版本都能直接覆盖安装，不必再卸。",
    "快捷键：E 摆棋 · U 悔棋 · P 复盘 · H 提示 · G 棋谱 · L 残局库 · M 音乐 · "
    "R 重开 · 1/2 示例与开局 · Esc 返回。本说明能用鼠标翻：滚轮上下、点「上一页 / 下一页」，"
    "点正文左半往回、右半往前；也可以用 ← → 或 PgUp / PgDn。",
]


def help_paras():
    """说明页段落。安卓上换成触屏说法：键盘快捷键整段撤掉，
    「按 Esc」「按 R」这类改成点按钮，曲子目录改成手机能拷进去的位置。"""
    if not IS_ANDROID:
        return HELP_PARAS
    out = []
    for para in HELP_PARAS:
        p = para
        if p.startswith("快捷键"):
            continue
        p = p.replace("↑↓ 逐行、PgUp/PgDn 整屏、Home/End 到两端；", "")
        p = p.replace("搜索框里敲数字按局号找：输 94 能搜到「第094局」，"
                      "输 3 也能定位列表第 3 条。", "")
        p = p.replace("对战中按 Esc 只回主页、不再存半局，",
                      "对战中点底部「返回」只回主页、不再存半局，")
        p = p.replace("（拖动时棋子跟着鼠标走，落点有绿点提示）",
                      "（拖动时棋子跟着手指走，落点有绿点提示）")
        p = p.replace("主页背景想换成自己的画：把图片命名成 主页背景.jpg 放在程序目录即可。", "")
        p = p.replace("悔棋 / 复盘 / 提示 / 存局 / 认输 / 提和 / 棋谱 / 重开 / 返回：",
                      "悔棋 / 提示 / 复盘 / 存局 / 返回主菜单 / 认输 / 提和 / 棋谱 / 重开：")
        p = p.replace("「返回」等于退出这一局回主页，不存半局；",
                      "「返回主菜单」等于退出这一局回主页，不存半局；")
        if p.startswith("【退出】"):
            p = ("【退出】点底部「返回主菜单」回主页，浮层点右上角 × 关闭；"
                 "手机的返回键也一样：先关浮层、再回主页。"
                 "回到主页后点右下角「退出」即回手机桌面（不用再靠上滑手势）。")
        elif p.startswith("【自己加曲子】"):
            p = ("【自己加曲子】手机没有系统文件对话框，所以「导入曲子」按钮会告诉你放在哪："
                 "把 mp3 / ogg / wav 拷到 Android/data/org.songyq.xiangqi/files/曲 目录"
                 "（没有就新建一个），回来设置面板就能看到新曲目，最多收 4 首，"
                 "名字太长会截短显示。想删掉导入的曲子：在设置里点中它，再点「删曲」，"
                 "4 秒内点第二次即删（内置古曲删不掉）。拷法：数据线连电脑选「文件传输」，"
                 "或用手机文件管理进那个目录。内置四首古曲（高山流水 / 平沙落雁 / "
                 "渔舟唱晚 / 广陵散）在没有同名文件时用程序合成的旋律顶上。"
                 "音效同理：同目录建 音效 文件夹，放 select.wav / 落子.wav / "
                 "吃子.wav / 将军.wav / 胜利.wav 即替换内置音效。")
        elif p.startswith("【导入】"):
            p = p.replace("或点「选文件」挑 棋谱 目录里的 .txt；", "")
        # 手机版把「电脑」都改口成「手机」：同一个手机里没有电脑这回事，
        # 只有「数据线连电脑」那句说的是真的电脑，先护住再换。
        p = p.replace("数据线连电脑", "\x00PC\x00")
        p = p.replace("电脑", "手机")
        p = p.replace("\x00PC\x00", "数据线连电脑")
        out.append(p)
    return out


def help_pages():
    """把说明切成一页一页：整段不拆开（除非这一段自己就超过一页），
    返回 [[行文字, ...], ...]，页与页之间不重复标题。"""
    font = load_font(HELP_FONT_SIZE)
    max_w = HELP_PANEL.w - 48
    cap = max(4, (HELP_TEXT_BOTTOM - HELP_TEXT_TOP) // HELP_LH)
    pages, cur = [], []
    # 注意：这里要走 help_paras() 而不是 HELP_PARAS ——
    # 手机上 help_paras() 会把快捷键那段和「按 Esc」这类桌面说法换掉，
    # 以前这里直接读 HELP_PARAS，等于安卓的改写白做了。
    for para in help_paras():
        block = [""] + wrap_text(para, font, max_w) if cur else wrap_text(para, font, max_w)
        if len(cur) + len(block) > cap:
            if cur:
                pages.append(cur)
            cur = []
            block = wrap_text(para, font, max_w)
            while len(block) > cap:          # 单段超长：硬切成两页
                pages.append(block[:cap])
                block = block[cap:]
        cur.extend(block)
    if cur:
        pages.append(cur)
    return pages or [[]]


def help_page_rects():
    """上一页 / 下一页按钮（末页的「下一页」变灰，但矩形照旧返回便于判定）"""
    return HELP_PREV, HELP_NEXT


def help_body_rect():
    """正文可点区：点左半翻上一页、点右半翻下一页"""
    return pygame.Rect(HELP_PANEL.x + 16, HELP_TEXT_TOP - 6,
                       HELP_PANEL.w - 32, HELP_TEXT_BOTTOM - HELP_TEXT_TOP + 8)


def draw_instructions_overlay(screen, page=0, hover=None):
    """使用说明：面板居中、分页显示，底部「上一页 / 下一页」+ 页码。
    hover 传当前鼠标的逻辑坐标：按钮会亮起来，鼠标指着哪儿一目了然。"""
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 130))
    screen.blit(shade, (0, 0))
    p = HELP_PANEL
    draw_rect(screen, C((252, 249, 242)), p, 0, 14)
    draw_rect(screen, C((34, 150, 96)), p, 2, 14)
    t = load_font_song(24).render("使　用　说　明", True, C((60, 48, 36)))
    screen.blit(t, (p.centerx - t.get_width() // 2, p.y + 28))
    draw_rect(screen, C((232, 214, 208)), HELP_CLOSE, 0, 6)
    cross = load_font(18).render("×", True, C((168, 60, 54)))
    screen.blit(cross, (HELP_CLOSE.centerx - cross.get_width() // 2,
                        HELP_CLOSE.centery - cross.get_height() // 2))

    pages = help_pages()
    total = len(pages)
    page = max(0, min(int(page), total - 1))
    font = load_font(HELP_FONT_SIZE)
    y = HELP_TEXT_TOP
    for line in pages[page]:
        if line:
            screen.blit(font.render(line, True, C((70, 58, 46))), (p.x + 24, y))
        y += HELP_LH

    # 本页没写满又还有下一页：在正文底部点明「后面还有」，免得以为只有一页
    if page < total - 1 and y < HELP_TEXT_BOTTOM - HELP_LH:
        more_text = ("↓ 后面还有 %d 页，点「下一页」继续看" if IS_ANDROID
                     else "↓ 后面还有 %d 页，点「下一页」或滚动滚轮继续看")
        more = load_font(13).render(
            more_text % (total - page - 1), True, C((34, 150, 96)))
        screen.blit(more, (p.centerx - more.get_width() // 2, HELP_TEXT_BOTTOM - 6))

    bfont = load_font(14)
    for rect, label, on in ((HELP_PREV, "< 上一页", page > 0),
                            (HELP_NEXT, "下一页 >", page < total - 1)):
        hot = bool(on and hover and rect.collidepoint(hover))
        if on:                                   # 可翻：实心绿底白字，一眼看出还能往后
            bg = C((42, 168, 108)) if hot else C((34, 150, 96))
            bd, fg = C((28, 128, 80)), K((255, 255, 255))
        else:                                    # 到头：灰底灰字
            bg, bd, fg = C((238, 234, 226)), C((206, 202, 194)), C((176, 168, 154))
        draw_rect(screen, bg, rect, 0, 8)
        draw_rect(screen, bd, rect, 1, 8)
        surf = bfont.render(label, True, fg)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))
    num = load_font(15).render("第 %d / %d 页" % (page + 1, total), True, C((110, 96, 78)))
    screen.blit(num, (p.centerx - num.get_width() // 2, HELP_PREV.centery - num.get_height() // 2))
    tip = load_font(12).render("点左右翻页" if IS_ANDROID else "滚轮 / 点左右翻页",
                               True, C((156, 144, 128)))
    screen.blit(tip, (HELP_CLOSE.x - 14 - tip.get_width(), p.y + 36))
    return total


IMPORT_PANEL_H = 226    # 只剩「外部导入」一块，面板固定高度


def import_layout(state):
    """导入浮层布局：只留外部导入（粘贴 / 选文件），面板固定高度、垂直居中。
    「暂存半局」已按用户意见撤掉 —— 保局走残局库的「存局」，此处不再重复。"""
    p = pygame.Rect(OVERLAY_PANEL.x, (SCREEN_H - IMPORT_PANEL_H) // 2,
                    OVERLAY_PANEL.w, IMPORT_PANEL_H)
    sec_y = p.y + 74
    field = pygame.Rect(p.x + 24, sec_y + 26, p.w - 48, 40)
    do_r = pygame.Rect(p.x + p.w - 152, field.bottom + 12, 64, 30)
    clear_r = pygame.Rect(p.x + p.w - 78, field.bottom + 12, 60, 30)
    file_r = pygame.Rect(p.x + 24, field.bottom + 12, 76, 30)
    msg_y = field.bottom + 50
    return p, [], field, do_r, clear_r, sec_y, msg_y, file_r


def import_close_rect(p):
    """导入浮层的关闭按钮（面板高度是动态的，不能沿用全局常量）"""
    return pygame.Rect(p.right - 42, p.y + 12, 30, 30)


def draw_import_overlay(screen, state):
    shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 130))
    screen.blit(shade, (0, 0))
    p, snap_rows, field, do_r, clear_r, sec_y, msg_y, file_r = import_layout(state)
    draw_rect(screen, C((252, 249, 242)), p, 0, 14)
    draw_rect(screen, C((34, 150, 96)), p, 2, 14)
    t = load_font_song(24).render("导　入　对　局", True, C((60, 48, 36)))
    screen.blit(t, (p.centerx - t.get_width() // 2, p.y + 30))
    close_r = import_close_rect(p)               # 面板高度是动态的，关闭键跟着面板走
    draw_rect(screen, C((232, 214, 208)), close_r, 0, 6)
    cross = load_font(18).render("×", True, C((168, 60, 54)))
    screen.blit(cross, (close_r.centerx - cross.get_width() // 2,
                        close_r.centery - cross.get_height() // 2))

    # 外部导入
    screen.blit(load_font(17).render("外部导入（棋谱文本 / FEN / JSON）", True, C((78, 64, 50))),
                (p.x + 24, sec_y))
    focus = state.get("import_focus")
    draw_rect(screen, C((255, 255, 255)), field, 0, 8)
    if focus:
        draw_rect(screen, C((34, 150, 96)), field, 2, 8)      # 聚焦：绿色描边
    else:
        draw_rect(screen, C((176, 166, 150)), field, 1, 8)
    buf = state.get("import_buf", "")
    caret_on = (pygame.time.get_ticks() // 500) % 2 == 0
    tfont = load_font(14)
    inner = field.inflate(-20, -10)
    tx = inner.x + (8 if focus else 0)          # 聚焦时留出光标位
    if buf:
        tsurf = tfont.render(buf, True, C((60, 50, 40)))
        if tsurf.get_width() > inner.w - 8:     # 过长只显示尾部，绝不出框
            tsurf = tsurf.subsurface((tsurf.get_width() - (inner.w - 8), 0,
                                      inner.w - 8, tsurf.get_height()))
        ty = field.centery - tsurf.get_height() // 2
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(inner.x, inner.y, inner.w - 8, inner.h))
        screen.blit(tsurf, (tx, ty))
        screen.set_clip(old_clip)
        caret_x = min(tx + tsurf.get_width() + 1, inner.right - 4)
    else:
        tsurf = tfont.render("粘贴棋谱全文 / FEN / JSON（Ctrl+V），或点左下「选文件」",
                             True, C((170, 160, 146)))
        ty = field.centery - tsurf.get_height() // 2
        screen.blit(tsurf, (tx, ty))
        caret_x = tx - 6
    if focus and caret_on:                       # 闪烁光标（空内容时也可见）
        x = max(inner.x + 2, caret_x)
        pygame.draw.line(screen, C((46, 120, 78)),
                         (x, ty + 3), (x, ty + tsurf.get_height() - 3), 2)
    for r, txt, col in [(do_r, "导入", C((34, 150, 96))),
                        (clear_r, "清空", C((196, 186, 170))),
                        (file_r, "选文件", C((120, 132, 122)))]:
        draw_rect(screen, col, r, 0, 6)
        sur = load_font(14).render(
            txt, True, K((255, 255, 255)) if col == C((34, 150, 96)) else C((92, 82, 68)))
        screen.blit(sur, (r.centerx - sur.get_width() // 2,
                          r.centery - sur.get_height() // 2))
    if state.get("import_msg"):
        ms = load_font(13).render(state["import_msg"], True, C((168, 60, 54)))
        screen.blit(ms, (p.x + 24, msg_y))


def finish_app():
    """主动退出：手机上限时结束 Activity 才能回到桌面（只 sys.exit 有些机型会留黑屏）。"""
    if IS_ANDROID:
        try:
            from android import mActivity          # type: ignore
            if mActivity is not None:
                mActivity.finish()
        except Exception:
            try:
                from jnius import autoclass        # type: ignore
                autoclass("org.kivy.android.PythonActivity").mActivity.finish()
            except Exception:
                pass


class BootSplash:
    """手机冷启动的开机动画：一枚棋子当表盘，外圈金点绕着转，下面一条进度条
    跟着加载步骤往前走。桌面不显示——窗口一闪就开，动画反而挡事。

    只在主线程画：初始化里最重的 ensure_library 丢给后台线程，主线程一直 tick，
    「棋子在转」和「残局库在读」是同时发生的，不会卡成一张静止图。
    """

    MIN_SECONDS = 1.4          # 至少转一圈，别一闪而过
    FADE_SECONDS = 0.25

    def __init__(self, screen, present):
        self.screen = screen
        self.present = present
        self.t0 = time.perf_counter()
        self.msg = "正在载入棋局"
        self.progress = 0.08
        self.frames = 0
        self._font_pair = None
        self._font_dead = False

    def _fonts(self):
        """中文字体第一次画才去找；找不到就退回几何纹样，绝不让启动画面自己崩"""
        if self._font_dead:
            return None
        if self._font_pair is None:
            try:
                self._font_pair = (load_font_song(92), load_font_song(17))
            except Exception:
                self._font_dead = True
                return None
        return self._font_pair

    def _paint(self, t):
        scr = self.screen
        scr.fill(C((24, 32, 28)))
        cx, cy = SCREEN_W // 2, 396
        for r in (196, 158):
            pygame.draw.circle(scr, C((36, 46, 40)), (cx, cy), r, 1)

        # 外圈：24 颗点，连续 6 颗点亮，随时间绕着走
        ticks = 24
        head = int(t * 26) % ticks
        for i in range(ticks):
            ang = i * 2 * math.pi / ticks - math.pi / 2
            px = cx + int(math.cos(ang) * 168)
            py = cy + int(math.sin(ang) * 168)
            lit = (i - head) % ticks < 6
            pygame.draw.circle(scr, C((216, 172, 86)) if lit else C((56, 68, 58)),
                               (px, py), 4 if lit else 3)

        # 棋子圆盘 + 双圈
        pygame.draw.circle(scr, C((240, 228, 200)), (cx, cy), 116)
        pygame.draw.circle(scr, C((124, 86, 50)), (cx, cy), 116, 3)
        pygame.draw.circle(scr, C((178, 142, 94)), (cx, cy), 99, 2)

        pair = None if self.frames < 1 else self._fonts()
        if pair:
            big, small = pair
            word = big.render("象", True, C((112, 66, 36)))
            scr.blit(word, (cx - word.get_width() // 2,
                            cy - word.get_height() // 2 - 6))
            tip = small.render(self.msg, True, C((198, 180, 148)))
            scr.blit(tip, (cx - tip.get_width() // 2, cy + 148))
            ver = small.render("中国象棋·智算单机版 v%s　安卓版" % VERSION,
                               True, C((122, 110, 90)))
            scr.blit(ver, (cx - ver.get_width() // 2, SCREEN_H - 56))
        else:
            # 字体还没热起来的第一帧：画个内纹，别让画面空着
            pygame.draw.line(scr, C((178, 142, 94)), (cx - 44, cy), (cx + 44, cy), 2)
            pygame.draw.line(scr, C((178, 142, 94)), (cx, cy - 44), (cx, cy + 44), 2)

        bar = pygame.Rect(cx - 130, cy + 196, 260, 6)
        draw_rect(scr, C((46, 58, 50)), bar, 0, 3)
        if self.progress > 0:
            fill = pygame.Rect(bar.x, bar.y,
                               max(6, int(bar.w * self.progress)), bar.h)
            draw_rect(scr, C((216, 172, 86)), fill, 0, 3)

    def tick(self, msg=None, progress=None):
        if msg:
            self.msg = msg
        if progress is not None:
            self.progress = max(0.02, min(1.0, progress))
        for _ev in pygame.event.get():      # 加载期间的事件一律吞掉，别攒进主循环
            pass
        self._paint(time.perf_counter() - self.t0)
        self.frames += 1
        self.present()
        pygame.time.wait(12)

    def finish(self):
        """收尾：补够最短时长，再淡出，不硬切"""
        while time.perf_counter() - self.t0 < self.MIN_SECONDS:
            self.tick(progress=max(self.progress, 0.92))
        self.tick(progress=1.0)
        begin = time.perf_counter()
        while time.perf_counter() - begin < self.FADE_SECONDS:
            k = (time.perf_counter() - begin) / self.FADE_SECONDS
            self._paint(time.perf_counter() - self.t0)
            veil = pygame.Surface((SCREEN_W, SCREEN_H))
            veil.fill((0, 0, 0))
            veil.set_alpha(int(255 * min(1.0, k)))
            self.screen.blit(veil, (0, 0))
            self.present()
            pygame.time.wait(12)


def bg_prepare(fn, splash=None, msg=None):
    """把耗时的准备活丢到后台线程，主线程继续转动画，结束再把结果 / 异常交回来。
    异常原样抛回主线程，不在后台悄悄吞掉。"""
    box = {}

    def work():
        try:
            box["value"] = fn()
        except BaseException as exc:
            box["error"] = exc

    th = threading.Thread(target=work, name="xq-boot", daemon=True)
    th.start()
    while th.is_alive():
        if splash is not None:
            splash.tick(msg)
        else:
            time.sleep(0.02)
    if "error" in box:
        raise box["error"]
    return box.get("value")


def main():
    # 触屏：让 SDL 把手指事件同时映射成鼠标事件，整套点选逻辑不用改
    os.environ.setdefault("SDL_TOUCH_MOUSE_EVENTS", "1")
    os.environ.setdefault("SDL_MOUSE_TOUCH_EVENTS", "1")
    # 切到后台（手机手势上滑 / 来电）时别让 SDL 把窗口缩成 0，回来容易黑屏
    os.environ.setdefault("SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS", "0")
    pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
    pygame.init()

    sounds = {}
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(SAMPLE_RATE, -16, 2, 512)
        sounds = build_sounds()
    except (pygame.error, OSError) as exc:
        print("音效初始化失败，将以静音运行：%s" % exc)

    # ---- 窗口自适应：逻辑画布固定 572×838，等比缩放并居中（手机竖屏四边留黑） ----
    if IS_ANDROID:
        # 安卓直接吃满全屏；先要尺寸再算缩放比，个别机型返回 0 时回退
        try:
            display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except pygame.error:
            display = pygame.display.set_mode((0, 0))
        win_w, win_h = display.get_size()
        if win_w < 240 or win_h < 320:            # 个别机型/模拟器返回 0 尺寸
            try:
                win_w, win_h = pygame.display.get_desktop_sizes()[0]
            except Exception:
                win_w, win_h = 1080, 1920
            win_w, win_h = max(240, win_w), max(320, win_h)
            try:
                display = pygame.display.set_mode((win_w, win_h), pygame.FULLSCREEN)
            except pygame.error:
                display = pygame.display.set_mode((win_w, win_h))
        try:
            pygame.mouse.set_visible(False)       # 触屏不需要鼠标指针
        except pygame.error:
            pass
    else:
        dinfo = pygame.display.Info()
        avail_w = max(320, dinfo.current_w - 60)
        avail_h = max(420, dinfo.current_h - 110)
        scale = min(1.0, avail_w / SCREEN_W, avail_h / SCREEN_H)
        win_w = max(320, int(SCREEN_W * scale))
        win_h = max(420, int(SCREEN_H * scale))
        display = pygame.display.set_mode((win_w, win_h))
    # 屏幕探针：main.py 启动时先量真实分辨率写进 XQ_BIG_UI；直接跑源码时按窗口尺寸判断。
    # 手机（短边 ≥720 物理像素）自动切到放大版界面，桌面保持原尺寸。
    big_env = os.environ.get("XQ_BIG_UI")
    if big_env == "1":
        set_ui_mode(True)
    elif big_env == "0" and not IS_ANDROID:
        set_ui_mode(False)
    else:
        set_ui_mode(IS_ANDROID or min(win_w, win_h) >= 720)
    draw_w, draw_h, off_x, off_y = fit_layout(win_w, win_h)
    screen = pygame.Surface((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("%s v%s · 计时对弈" % (APP_NAME, VERSION))
    try:                                   # 窗口左上角图标（缺文件不影响运行）
        pygame.display.set_icon(pygame.image.load(_asset("图标.png")))
    except (pygame.error, OSError):
        pass

    def present():
        """把逻辑画布等比缩放贴到窗口正中并刷新（多余部分留黑边）"""
        if (win_w, win_h) == (SCREEN_W, SCREEN_H):
            display.blit(screen, (0, 0))
        else:
            if (draw_w, draw_h) != (win_w, win_h):
                display.fill((0, 0, 0))          # 上下或左右的黑边
            if (draw_w, draw_h) == (SCREEN_W, SCREEN_H):
                display.blit(screen, (off_x, off_y))
            else:
                target = display.subsurface(
                    pygame.Rect(off_x, off_y, draw_w, draw_h))
                pygame.transform.smoothscale(screen, (draw_w, draw_h), target)
        pygame.display.flip()

    def to_logical(pos):
        return window_to_logical(pos, win_w, win_h)

    # v2.9：手机冷启动要等好几秒，先上一段开机动画。桌面不显示。
    boot = BootSplash(screen, present) if IS_ANDROID else None
    if boot:
        boot.tick("正在载入设置", 0.10)

    settings0 = load_settings()
    apply_theme(settings0.get("theme", THEME_NAMES[0]))
    if boot:
        boot.tick("正在准备棋盘", 0.22)
    # 背景音乐：旧存档里 "bgm": "关" 视为关闭，曲目回落到第一首
    pool = bgm_names()
    bgm0 = settings0.get("bgm", pool[0])
    bgm_on0 = bool(settings0.get("bgm_on", bgm0 != "关"))
    if bgm0 not in pool:
        bgm0 = pool[0]
    S = {
        "screen": "home",                 # home（主页）/ battle（对局）
        "home_overlay": None,             # None / settings / instructions / import
        "help_page": 0,                   # 说明浮层当前页码（多页显示）
        "board": dict(DEFAULT_ENDGAME),
        "selected": None,
        "turn": RED,
        "time_limit": int(settings0.get("time_limit", TIME_LIMIT)),
        "move_limit": int(settings0.get("move_limit", 0)),   # 单步限时（秒），0 = 不限
        "remain": {RED: float(settings0.get("time_limit", TIME_LIMIT)),
                   BLACK: float(settings0.get("time_limit", TIME_LIMIT))},
        "counts": {RED: 0, BLACK: 0},
        "turn_start": time.perf_counter(),
        "over": False,
        "message": ("欢迎使用中国象棋 · 计时对局 v%s。从主页选择「对战 / 残局 / 摆棋 / 导入」开始。"
                    % VERSION),
        "difficulty": settings0.get("difficulty", "普通"),
        "sound_on": bool(settings0.get("sound_on", True)),
        "bgm": bgm0,
        "bgm_on": bgm_on0,
        "editing": False,
        "edit_piece": (RED, PAWN),
        "backup": None,
        "edit_msg": ("摆棋：点棋子后点棋盘放置，右键删除。规则：双方各须一枚将/帅，"
                     "除将帅外至少还要一枚棋子，士象车马炮最多 2、兵卒最多 5；"
                     "落点亦须合法——将帅士不出九宫、象不过河、兵卒不后退。"),
        "position": "残局示例",
        "entries": (bg_prepare(ensure_library, boot, "正在整理残局库")
                    if boot else ensure_library()),
        "lib_open": False,
        "lib_category": "全部",
        "lib_pieces": "全部",     # 阶段筛选档位（全部 / 开局 / 中局 / 残局）
        "lib_level": "全部",      # 难度筛选档位（全部 / 简单 / 中等 / 困难，按先手方处境算）
        "lib_off": max(0, int(settings0.get("lib_page", 0))),
        "history": [],
        "start_board": dict(DEFAULT_ENDGAME),
        "result": "",
        "custom_name": "",
        "naming": False,
        "name_buf": "",
        "naming_from": "edit",
        "undo_stack": [],
        "last_move": None,
        "battle_start": time.perf_counter(),
        "anim": None,            # 走子滑行动画：{fr,fc,tr,tc,piece,victim,t0}
        "drag": None,            # 正在拖的棋子：{fr,fc,piece,pos,moved}
        "ripple": None,          # 落子涟漪：(行, 列, 起始时刻)
        "replay": False,
        "replay_index": 0,
        "replay_auto": False,
        "replay_last": 0.0,
        "scroll_drag": False,
        "scroll_grab": 0,
        "lib_del_pending": None,
        "bgm_state": {},
        "import_buf": "",
        "import_focus": False,
        "import_msg": "",
        "settings_msg": "",        # 设置面板底部的一行回执（导入曲子 / 换曲目）
        # ---- v1.1 新增 ----
        "sound_vol": max(0.0, min(1.0, float(settings0.get("sound_vol", DEFAULT_SOUND_VOL)))),
        "music_vol": max(0.0, min(1.0, float(settings0.get("music_vol", DEFAULT_MUSIC_VOL)))),
        "undo_limit": int(settings0.get("undo_limit", 0)),
        "undo_left": int(settings0.get("undo_limit", 0)),
        "vol_drag": None,
        "move_hints": [],
        "hint": None,
        "rep_counts": {},
        "pos_log": [],            # 每着一记录（局面指纹 / 走子方 / 是否将军），长将裁决用
        "quiet_halfmoves": 0,
        "check_streak": {RED: 0, BLACK: 0},
        "surrender_pending": False,
        "lib_query": "",
        "lib_focus": False,
        "lib_io_msg": "",
        "ai_job": None,          # 后台思考中的 AI 任务（AiJob）
        "hint_job": None,        # 后台算「提示」的任务（AiJob），不卡界面
        "cpu_offer": None,       # 电脑提议和棋 / 认输：{kind, reason} 或 None（弹窗显示中）
        "cpu_offer_no": -99,     # 上次人类拒绝提和时的半回合数（隔几手才再提）
        "cpu_offer_times": 0,    # 这一局已经主动议和过几次（最多 DRAW_OFFER_MAX 回）
        "music_del_pending": 0.0,  # 设置里点「删曲」的时间，4 秒内再点一次才真删
        "cpu_given_up": False,   # 人类拒绝过「电脑认输」：之后不再提和、不再认输
        "resign_at": 10 ** 9,    # 必败局里被拒和棋后，走到这个半回合数就认输
        "offer_elapsed": 0.0,    # 弹窗弹出时的本手用时（弹窗期间冻结计时）
        "quit_requested": False,  # 主页点了「退出」
        "lib_entry": "",
        "start_turn": RED,                # 当前局面的起始先行方（黑先排局为黑）
        "naming_mode": "save",            # save（存局）/ edit（摆棋）/ rename（改名）
        "rename_idx": None,
        "rename_turn": RED,
    }
    if boot:
        boot.tick("马上就好", 0.90)

    # v2.4：暂存半局功能已撤掉，旧设置里攒下的条目不再读入（见 persist_settings 里清键）

    def apply_volumes():
        """把音量设置作用到音效对象上（音乐音量在 bgm_tick 里用）"""
        if not sounds:
            return
        vol = max(0.0, min(1.0, S["sound_vol"]))
        for name in SOUND_NAMES:
            snd = sounds.get(name)
            if snd is not None:
                try:
                    snd.set_volume(vol)
                except pygame.error:
                    pass

    def set_volume_from_x(cat, rect, x):
        """按点击位置算音量（0~1）"""
        v = round(max(0.0, min(1.0, (x - rect.x) / max(1, rect.w))), 2)
        if cat == "vol_sound":
            S["sound_vol"] = v
            apply_volumes()
        else:
            S["music_vol"] = v

    apply_volumes()

    def beep(name):
        """受音效开关控制的声音播放"""
        if S["sound_on"] and sounds:
            play(sounds, name)

    def persist_settings():
        """把设置（难度/音效/音量/时限/背景音乐/悔棋限制/配色/页码）写入本地文件。
        v2.4：顺手把旧版留下的 snapshots 键删掉，免得文件里一直躺着 10 条死数据。"""
        sd = load_settings()
        sd["difficulty"] = S["difficulty"]
        sd["sound_on"] = S["sound_on"]
        sd["time_limit"] = S["time_limit"]
        sd["move_limit"] = int(S.get("move_limit", 0))
        sd["bgm"] = S["bgm"]
        sd["bgm_on"] = S["bgm_on"]
        sd["sound_vol"] = round(S["sound_vol"], 2)
        sd["music_vol"] = round(S["music_vol"], 2)
        sd["undo_limit"] = S["undo_limit"]
        sd["theme"] = THEME_CURRENT
        sd["lib_page"] = int(S.get("lib_off", 0))
        sd.pop("snapshots", None)     # v2.4 撤掉暂存半局，旧条目一并清掉
        save_settings(sd)

    def cancel_ai():
        """打断后台思考：换局、悔棋、摆棋、回主页时都要先叫停，
        否则旧局面算出的着法会落到新局面里。"""
        job = S.get("ai_job")
        S["ai_job"] = None
        if job is not None:
            job.cancel()

    def persist_lib_page():
        """把当前残局库页码写入本地设置，下次启动恢复"""
        persist_settings()

    if "snapshots" in (settings0 or {}):
        persist_settings()        # v2.4：旧设置里的暂存条目开局就清掉，立刻落盘

    def start_from(board, title, turn=RED, human=None):
        """以给定局面开始新对局，并重置计时与棋谱。
        turn：轮到哪一方走（黑先排局可传黑）；human：人类执哪一方，缺省执红。"""
        cancel_ai()
        turn = turn if turn in (RED, BLACK) else RED
        set_sides(human if human in (RED, BLACK) else DEFAULT_HUMAN)
        S["board"] = dict(board)
        S["start_board"] = dict(board)
        S["start_turn"] = turn
        S["position"] = title
        S["selected"] = None
        S["turn"] = turn
        S["remain"] = {RED: float(S["time_limit"]), BLACK: float(S["time_limit"])}
        S["battle_start"] = time.perf_counter()   # 记录这一局从什么时候开始（通关用时）
        S["counts"] = {RED: 0, BLACK: 0}
        S["turn_start"] = time.perf_counter()
        S["over"] = False
        S["history"] = []
        S["result"] = ""
        S["undo_stack"] = []
        S["last_move"] = None
        S["replay"] = False
        S["replay_index"] = 0
        S["replay_auto"] = False
        # v1.1：重复局面 / 无吃子回合 / 长将 / 悔棋余量
        S["rep_counts"] = {position_key(S["board"], turn): 1}
        S["pos_log"] = [{"key": position_key(S["board"], turn), "mover": None, "check": False}]
        S["lib_entry"] = ""        # 换了局面就不再算「库中那一局」，避免错标通关
        S["quiet_halfmoves"] = 0
        S["check_streak"] = {RED: 0, BLACK: 0}
        S["move_hints"] = []
        S["hint"] = None
        S["surrender_pending"] = False
        S["cpu_offer"] = None      # 新开一局：把上一局的提和弹窗关掉
        S["cpu_offer_no"] = -99
        S["cpu_offer_times"] = 0   # 议和次数按局清零，新局还能再提三回
        S["cpu_given_up"] = False  # 上一局「不用你认输」的态度不带进新局
        S["resign_at"] = 10 ** 9
        S["undo_left"] = S["undo_limit"]

    def reset_position(title):
        """R 键重开：库中残局/导入局面用其起始局面，内置局面查表"""
        board = POSITIONS.get(title, S["start_board"])
        lib_entry = S.get("lib_entry", "")
        start_from(board, title, turn=S.get("start_turn", RED), human=HUMAN_SIDE)
        S["lib_entry"] = lib_entry if (lib_entry and lib_entry == title) else ""
        S["message"] = "%s就绪，%s先行（每方 %d 分钟包干）。" % (
            title, name_of(S["turn"]), S["time_limit"] // 60)

    def enter_edit():
        cancel_ai()
        S["backup"] = dict(S["board"])
        S["editing"] = True
        S["selected"] = None
        S["edit_msg"] = ("摆棋：下方为双方全盘棋子，摆一枚少一枚；右键擦除后会自动回到板上。"
                         "点「完成」校验：双方各须一枚将/帅、除将帅外至少一枚子、"
                         "士象车马炮≤2、兵卒≤5、将帅不照面。")
        beep("select")

    def leave_edit(restore=True):
        if restore and S["backup"] is not None:
            S["board"] = dict(S["backup"])
        S["editing"] = False
        S["backup"] = None

    def finish_edit():
        ok, msg = validate_position(S["board"])
        if not ok:
            S["edit_msg"] = msg
            beep("illegal")
            return
        start_from(S["board"], "自定残局")
        S["editing"] = False
        S["backup"] = None
        S["message"] = "自定残局开始，红方先行。按 E 可继续调整，点「保存」可存入残局库。"
        beep("win")

    def current_save_category():
        """存盘分类：从残局库载入的沿用原分类，其余（对战 / 摆棋）归「自定残局」"""
        name = S.get("lib_entry") or ""
        if name:
            for e in S["entries"]:
                if e.get("name") == name and e.get("category"):
                    return e["category"]
        return CUSTOM_CATEGORY

    def save_current(category=None):
        """保存当前局面到残局库：先按规则校验，再查同名与同局面，禁止重复存盘。
        摆棋时按完整规则查（士象兵卒走位、将帅照面）；对战中存的是走出来的局面，
        只做结构校验，免得从残局库/棋谱导入的排局反而存不回去。"""
        S["entries"] = load_library()
        ok, why = validate_position(S["board"], rules=S["editing"])
        if not ok:
            S["edit_msg"] = "不符合摆棋要求（%s），未存盘。" % why
            S["message"] = S["edit_msg"]
            beep("illegal")
            return
        name = (S["custom_name"] or "").strip()
        if not name:
            name = time.strftime("残局 %m%d-%H%M%S")

        # 同名检查：避免覆盖已有残局
        if any(e.get("name") == name for e in S["entries"]):
            S["edit_msg"] = "已存在同名残局「%s」，请换个名字再保存。" % name
            S["message"] = S["edit_msg"]
            beep("illegal")
            open_naming("save")          # 打开命名框让用户改名（已预填）
            return

        # 同局面检查：棋盘完全一致则视为重复
        cur = sorted(board_to_record(S["board"]),
                     key=lambda x: (x["r"], x["c"], x["color"], x["type"]))
        for e in S["entries"]:
            er = sorted(e.get("pieces", []),
                        key=lambda x: (x["r"], x["c"], x["color"], x["type"]))
            if er == cur and cur:
                S["edit_msg"] = "该局面已保存在「%s」中，无需重复保存。" % e.get("name")
                S["message"] = S["edit_msg"]
                beep("illegal")
                return

        cat = category or current_save_category()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "name": name,
            "saved": now,             # 旧字段保留，老版本读库不会错位
            "saved_at": now,
            "category": cat,
            "pieces": board_to_record(S["board"]),
            "turn": S["turn"] or RED,  # 存的是哪一方该走，载入时照此开局
        }
        S["entries"].append(entry)
        try:
            save_library(S["entries"])
        except OSError as exc:
            S["edit_msg"] = "保存失败：%s" % exc
            S["message"] = S["edit_msg"]
            beep("illegal")
            return
        S["edit_msg"] = "已存入残局库「%s」（%s），共 %d 局。" % (
            name, cat, len(S["entries"]))
        S["message"] = "已保存为第 %d 条「%s」（分类：%s），按 L 打开残局库查看。" % (
            len(S["entries"]), name, cat)
        beep("select")

    def open_naming(source="save", idx=None):
        """打开命名浮层：save（存局）/ edit（摆棋命名）/ rename（改库中条目的名）"""
        S["naming_from"] = source
        S["naming_mode"] = source
        S["naming"] = True
        S["name_fresh"] = (source == "rename")   # 改名：输入即替换旧名
        if source == "rename" and idx is not None:
            S["rename_idx"] = idx
            entry = S["entries"][idx]
            S["rename_turn"] = entry_turn(entry)
            S["name_buf"] = str(entry.get("name", ""))
        else:
            S["rename_idx"] = None
            S["name_buf"] = S["custom_name"] or ""
        try:
            pygame.key.start_text_input()
        except (AttributeError, pygame.error):
            pass

    def rename_detail(idx):
        """改名浮层里的条目详情：分类 / 出处 / 存盘时间 / 子数"""
        if idx is None or not (0 <= idx < len(S["entries"])):
            return ""
        entry = S["entries"][idx]
        bits = [entry.get("category") or CUSTOM_CATEGORY]
        origin = short_origin(entry_origin(entry))
        if origin:
            bits.append("出处 " + origin)
        stamp = entry_saved_at(entry)
        if stamp:
            bits.append("存于 " + stamp)
        bits.append("%d 子" % len(entry.get("pieces", [])))
        return "　".join(bits)

    def apply_rename():
        """确认改名：查重、写库，并同步已载入局面名"""
        idx = S.get("rename_idx")
        if idx is None or not (0 <= idx < len(S["entries"])):
            return
        entry = S["entries"][idx]
        old = str(entry.get("name", ""))
        new = (S["name_buf"] or "").strip()[:24]
        if not new:
            S["edit_msg"] = "名字不能为空，未改名。"
            beep("illegal")
            return
        for i, e in enumerate(S["entries"]):
            if i != idx and str(e.get("name", "")) == new:
                S["edit_msg"] = "已存在同名残局「%s」，换个名字吧。" % new
                beep("illegal")
                return
        entry["name"] = new
        turn = S.get("rename_turn", entry_turn(entry))
        if turn in (RED, BLACK):
            entry["turn"] = turn
        try:
            save_library(S["entries"])
        except OSError as exc:
            S["edit_msg"] = "改名写入失败：%s" % exc
            beep("illegal")
            return
        if S.get("lib_entry") == old:
            S["lib_entry"] = new              # 通关标记仍能对上
        if S.get("position") == old:
            S["position"] = new
        S["edit_msg"] = "已改名为「%s」（%s先行）。" % (new, name_of(entry_turn(entry)))
        S["message"] = S["edit_msg"]
        beep("select")

    def close_naming(confirm):
        mode = S.get("naming_mode", "save")
        if confirm and mode != "rename":
            S["custom_name"] = S["name_buf"].strip()[:24]
        S["naming"] = False
        try:
            pygame.key.stop_text_input()
        except (AttributeError, pygame.error):
            pass
        if not confirm:
            return
        if mode == "rename":
            apply_rename()
        elif mode == "save":
            save_current()              # 命名后继续保存流程
        elif S["custom_name"]:
            S["edit_msg"] = "名称已设为「%s」，保存时生效。" % S["custom_name"]
            S["message"] = S["edit_msg"]

    def paste_clipboard():
        try:
            pygame.scrap.init()
            data = pygame.scrap.get(pygame.SCRAP_TEXT)
        except (AttributeError, pygame.error):
            return ""
        if not data:
            return ""
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("gbk", "ignore")
        return text.replace("\x00", "").strip()

    def load_entry(idx):
        entry = S["entries"][idx]
        board = record_to_board(entry["pieces"])
        name = entry.get("name", "残局")
        ok, why = validate_position(board, rules=False)   # 排局允许特殊构图
        if not ok:
            S["edit_msg"] = "「%s」局面不合规（%s），无法载入。" % (name, why)
            beep("illegal")
            return
        turn = entry_turn(entry)
        # 条目自带先行方：黑先排局由人类执黑、电脑执红先动，通关也照样记
        start_from(board, name, turn=turn, human=turn)
        S["lib_entry"] = name
        S["lib_open"] = False
        S["lib_focus"] = False
        S["editing"] = False
        S["backup"] = None
        S["message"] = ("「%s」已载入，%s先行（你执%s，每方 %d 分钟包干）。"
                        "按 E 可进入摆棋调整。"
                        % (name, name_of(turn), name_of(HUMAN_SIDE),
                           TIME_LIMIT // 60))
        beep("select")

    def export_library():
        """把整库导出成 JSON 文件"""
        path = pick_library_file(save=True)
        if not path:
            S["edit_msg"] = "已取消导出。"
            beep("illegal")
            return
        try:
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(S["entries"], fp, ensure_ascii=False, indent=2)
        except OSError as exc:
            S["edit_msg"] = "导出失败：%s" % exc
            beep("illegal")
            return
        S["edit_msg"] = "已导出 %d 局 → %s" % (len(S["entries"]),
                                             os.path.basename(path))
        beep("select")

    def import_library():
        """从 JSON 文件导入整库（按名称 + 局面去重）"""
        path = pick_library_file(save=False)
        if not path:
            S["edit_msg"] = "已取消导入。"
            beep("illegal")
            return
        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, ValueError) as exc:
            S["edit_msg"] = "导入失败：%s" % exc
            beep("illegal")
            return
        if not isinstance(data, list):
            S["edit_msg"] = "导入失败：该文件不是残局库格式。"
            beep("illegal")
            return
        # 去重按「局面 + 先行方」：同一个局面被换了个名字、或者从别的库并进来，
        # 都不会重复堆一遍（以前只按名字+棋子判，改个名字就能塞进第二条）
        existing = {position_signature(e) for e in S["entries"]}
        added = 0
        skipped = 0
        for item in data:
            if not isinstance(item, dict) or not isinstance(item.get("pieces"), list):
                continue
            sig = position_signature(item)
            if sig in existing:
                skipped += 1
                continue
            S["entries"].append(item)
            existing.add(sig)
            added += 1
        try:
            save_library(S["entries"])
        except OSError as exc:
            S["edit_msg"] = "写入失败：%s" % exc
            beep("illegal")
            return
        S["lib_off"] = 0
        S["edit_msg"] = ("已导入 %d 局，跳过重复 %d 局，库中共 %d 局。"
                         % (added, skipped, len(S["entries"])))
        beep("select")

    def stop_bgm():
        """立刻停掉正在响的背景音符，并清空调度状态（下次开启从头循环）"""
        S["bgm_state"] = {}
        try:
            pygame.mixer.Channel(BGM_CHANNEL).stop()
        except (pygame.error, AttributeError):
            pass

    def bgm_tick():
        """背景古曲循环播放：每帧调度下一音符，曲目切换时自动重头循环。
        曲 目录里有同名音频（wav / ogg / mp3）时，直接用文件循环，不再合成。"""
        if not S["bgm_on"] or not sounds:
            return
        ch = pygame.mixer.Channel(BGM_CHANNEL)
        now = time.perf_counter()
        st = S["bgm_state"]
        if st.get("name") != S["bgm"]:
            st["name"] = S["bgm"]
            st["idx"] = 0
            st["next_time"] = now + 0.05
            st["user"] = load_user_music(S["bgm"])
            try:
                ch.stop()                 # 换曲先停掉上一首
            except pygame.error:
                pass
        if st.get("user") is not None:
            vol = max(0.0, min(1.0, S["music_vol"]))
            if not ch.get_busy():
                ch.play(st["user"], loops=-1)
            ch.set_volume(vol)            # 拖音量滑块立刻生效，不必等换曲
            return
        track = BGM_TRACKS.get(S["bgm"])
        if not track:
            return
        if ch.get_busy():
            return
        if now < st["next_time"]:
            return
        if st["idx"] >= len(track):
            st["idx"] = 0
        freq, dur = track[st["idx"]]
        play_note(freq, dur, 0.14 * max(0.0, min(1.0, S["music_vol"])), BGM_CHANNEL)
        st["idx"] += 1
        st["next_time"] = now + dur

    def open_overlay(name):
        S["home_overlay"] = name
        if name == "settings":
            S["settings_msg"] = ""        # 每次打开都干净起手，不带上次的回执
        if name == "instructions":
            S["help_page"] = 0            # 每次都从第一页看起
        if name == "import":
            S["import_buf"] = ""
            S["import_msg"] = ""
            S["import_focus"] = True
            try:
                pygame.key.start_text_input()
            except (AttributeError, pygame.error):
                pass
        beep("select")

    def close_overlay():
        S["home_overlay"] = None
        S["import_focus"] = False
        try:
            pygame.key.stop_text_input()
        except (AttributeError, pygame.error):
            pass

    def help_turn_page(step):
        """说明浮层翻页：step 为 -1 / +1，到头就停住（键盘、滚轮、点按钮都走这里）"""
        total = max(1, len(help_pages()))
        page = int(S.get("help_page", 0))
        new = max(0, min(total - 1, page + step))
        if new != page:
            S["help_page"] = new
            beep("select")
        return new

    def esc_back_home():
        """对战中按 Esc：直接返回主页（程序仅主页可关闭）。
        「暂存半局」按用户意见撤掉：保局统一走残局库的「存局」，
        不再另存一份看不见的快照列表，免得数据存了却没处取。"""
        cancel_ai()
        moves = len(S["history"])
        if moves >= 2:
            msg = "已返回主页。这局没有存，想保下来请在局中点「存局」存进残局库。"
        else:
            msg = "已返回主页。"
        S["screen"] = "home"
        S["editing"] = False
        S["lib_open"] = False
        S["replay"] = False
        S["selected"] = None
        S["message"] = msg
        beep("select")

    def import_from_text(text, source=""):
        """导入外部内容：整份棋谱（含逐手回放）、FEN、或棋谱 JSON"""
        text = (text or "").strip()
        if not text:
            S["import_msg"] = "请先粘贴内容，或点「选文件」挑一份棋谱。"
            beep("illegal")
            return

        # 1) 本程序导出的整份棋谱：解析起始局面并逐手回放
        rec = parse_record_text(text)
        if rec:
            ok, why = validate_position(rec["start"], rules=False)
            if not ok:
                S["import_msg"] = "棋谱的起始局面不合法：%s" % why
                beep("illegal")
                return
            moves = rec["moves"]
            start_from(rec["start"], "导入棋谱")
            if moves:
                S["history"] = list(moves)
                S["board"] = dict(rec["final"])
                S["rep_counts"] = dict(rec["rep_counts"])
                # 导入后重建每着记录，长将 / 三次重复裁决仍能回看整轮循环
                log = [{"key": position_key(rec["start"], RED),
                        "mover": None, "check": False}]
                b2, t2 = dict(rec["start"]), RED
                for h in moves:
                    b2 = apply_move(b2, h["fr"], h["fc"], h["tr"], h["tc"])
                    en2 = opponent(t2)
                    log.append({"key": position_key(b2, en2), "mover": t2,
                                "check": in_check(b2, en2)})
                    t2 = en2
                S["pos_log"] = log
                S["turn"] = RED if len(moves) % 2 == 0 else BLACK
                h = moves[-1]
                S["last_move"] = (h["fr"], h["fc"], h["tr"], h["tc"],
                                  RED if h["side"] == "红方" else BLACK)
            S["screen"] = "battle"
            S["home_overlay"] = None
            S["editing"] = False
            S["lib_open"] = False
            S["import_buf"] = ""
            S["import_msg"] = ""
            S["message"] = ("棋谱已导入（%s），可按「复盘」逐步看全谱。"
                            % (rec["note"] or "已解析") if moves
                            else "已导入棋谱里的起始局面（未找到可回放的着法）。")
            beep("select")
            return

        board = None
        if "/" in text:
            first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
            try:
                board = fen_to_board(first)
            except (ValueError, KeyError, IndexError):
                board = None
        if board is None:
            try:
                obj = json.loads(text)
                if isinstance(obj, dict):
                    if "pieces" in obj:
                        board = record_to_board(obj["pieces"])
                    elif "fen" in obj:
                        board = fen_to_board(obj["fen"])
                elif isinstance(obj, list):
                    board = record_to_board(obj)
            except (ValueError, KeyError, TypeError):
                board = None
        if not board:
            S["import_msg"] = ("无法识别：可给整份棋谱文本、合法 FEN，"
                               "或含 pieces/fen 的棋谱 JSON。")
            beep("illegal")
            return
        ok, msg = validate_position(board)
        if not ok:
            S["import_msg"] = "局面不合法：" + msg
            beep("illegal")
            return
        start_from(board, "导入对局")
        S["screen"] = "battle"
        S["home_overlay"] = None
        S["editing"] = False
        S["lib_open"] = False
        S["import_buf"] = ""
        S["import_msg"] = ""
        S["message"] = "已从外部棋谱载入，红方先行。"
        beep("select")

    def import_from_file():
        """选一个棋谱 / 局面文件，读出全文再走导入流程"""
        path = pick_text_file()
        if not path:
            S["import_msg"] = "没有选中文件（或系统文件对话框不可用）。"
            beep("illegal")
            return
        content = None
        for enc in ("utf-8-sig", "gbk", "utf-16"):
            try:
                with open(path, "r", encoding=enc) as fp:
                    content = fp.read()
                break
            except (OSError, UnicodeError):
                content = None
        if content is None:
            S["import_msg"] = "读取失败：文件可能是二进制，或编码无法识别。"
            beep("illegal")
            return
        import_from_text(content, os.path.basename(path))

    def home_event(event):
        """主页与浮层的事件处理；返回后由主循环 continue 跳过对局逻辑"""
        if (event.type == pygame.TEXTINPUT and S["home_overlay"] == "import"
                and S.get("import_focus")):
            S["import_buf"] = (S["import_buf"] + event.text)[:4000]
            return
        if event.type == pygame.KEYDOWN:
            if S["home_overlay"] == "import" and S.get("import_focus"):
                if event.key == pygame.K_BACKSPACE:
                    S["import_buf"] = S["import_buf"][:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    import_from_text(S["import_buf"])
                elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                    S["import_buf"] = (S["import_buf"] + paste_clipboard())[:4000]
                return
            if S["home_overlay"] == "instructions" and event.key in (
                    pygame.K_LEFT, pygame.K_PAGEUP, pygame.K_RIGHT, pygame.K_PAGEDOWN):
                help_turn_page(-1 if event.key in (pygame.K_LEFT, pygame.K_PAGEUP) else 1)
                return
            if event.key == pygame.K_ESCAPE:
                if S["home_overlay"]:
                    close_overlay()
                else:
                    nonlocal running
                    running = False
            return
        # 说明浮层：滚轮上下翻页（老式滚轮是 button 4 / 5，也照收）
        # 以前滚一格常常一下翻两页：Windows 滚轮一格会连发两个 MOUSEWHEEL 事件。
        # 现在 0.15 秒内的重复滚动算同一次，想连翻两页就分两次滚（间隔够 0.15 秒）。
        if S["home_overlay"] == "instructions":
            if event.type == pygame.MOUSEWHEEL:
                now = time.perf_counter()
                if now - S.get("help_wheel_t", 0.0) >= 0.15:
                    S["help_wheel_t"] = now
                    help_turn_page(-1 if event.y > 0 else 1)
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                now = time.perf_counter()
                if now - S.get("help_wheel_t", 0.0) >= 0.15:
                    S["help_wheel_t"] = now
                    help_turn_page(-1 if event.button == 4 else 1)
                return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos
        ov = S["home_overlay"]
        if ov == "settings":
            for rect, cat, val in settings_hitboxes(S)[0]:
                if rect.collidepoint(pos):
                    if cat == "close":
                        close_overlay()
                    elif cat == "difficulty":
                        S["difficulty"] = val
                        persist_settings()
                        beep("select")
                    elif cat == "sound":
                        S["sound_on"] = val
                        persist_settings()
                        beep("select")
                    elif cat in ("vol_sound", "vol_music"):
                        set_volume_from_x(cat, rect, pos[0])
                        S["vol_drag"] = cat
                        beep("select")
                    elif cat == "undo":
                        S["undo_limit"] = val
                        S["undo_left"] = val
                        persist_settings()
                        beep("select")
                    elif cat == "theme":
                        apply_theme(val)
                        persist_settings()
                        beep("select")
                    elif cat == "time":
                        S["time_limit"] = int(val) * 60
                        persist_settings()
                        beep("select")
                    elif cat == "move_time":
                        S["move_limit"] = int(val)
                        persist_settings()
                        beep("select")
                    elif cat == "bgm_on":
                        S["bgm_on"] = val
                        if not val:
                            stop_bgm()
                        elif S["bgm_state"].get("name") != S["bgm"]:
                            S["bgm_state"] = {}
                        persist_settings()
                        beep("select")
                    elif cat == "bgm":
                        S["bgm"] = val
                        stop_bgm()
                        persist_settings()
                        S["settings_msg"] = "曲目已换成「%s」。" % val
                        if not S["bgm_on"]:
                            S["settings_msg"] = "已换曲目，但背景音乐还关着（上面点「开」）。"
                        beep("select")
                    elif cat == "music_import":
                        if IS_ANDROID:
                            # 安卓没有 tkinter 文件对话框：告诉用户把文件放哪儿，
                            # 拷进去后曲目会自动出现在上面那一行
                            d = music_write_dir() or "曲"
                            S["settings_msg"] = (
                                "拷到 Android/data/org.songyq.xiangqi/files/曲 即可（最多 %d 首）"
                                % MUSIC_MAX_FILES)
                            beep("illegal")
                        else:
                            ok, msg = import_music_file(pick_music_file())
                            S["settings_msg"] = msg
                            beep("select" if ok else "illegal")
                    elif cat == "music_delete":
                        # 删曲只删「当前选中」那一首，而且只删曲 目录里的文件；
                        # 内置古曲删不掉（程序合成的，删了没得听）。点两次才真删。
                        name = S.get("bgm") or ""
                        if not has_music_file(name):
                            S["settings_msg"] = (
                                "「%s」是内置古曲，删不了；先在上面选中一首导入的曲子再点「删曲」。"
                                % (name or "当前曲目"))
                            beep("illegal")
                        else:
                            now = time.perf_counter()
                            if now - float(S.get("music_del_pending") or 0) <= 4.0:
                                S["music_del_pending"] = 0.0
                                ok, msg = delete_music_file(name)
                                S["settings_msg"] = msg
                                if ok:
                                    names = bgm_names()
                                    if S["bgm"] not in names and names:
                                        stop_bgm()
                                        S["bgm"] = names[0]
                                    persist_settings()
                                    beep("select")
                                else:
                                    beep("illegal")
                            else:
                                S["music_del_pending"] = now
                                S["settings_msg"] = (
                                    "4 秒内再点一次「删曲」才真删「%s」。" % name)
                                beep("select")
                    return
            return
        if ov == "instructions":
            if HELP_CLOSE.collidepoint(pos):
                close_overlay()
            elif HELP_PREV.collidepoint(pos):
                help_turn_page(-1)
            elif HELP_NEXT.collidepoint(pos):
                help_turn_page(1)
            elif help_body_rect().collidepoint(pos):
                # 正文区也能点：左半页往回、右半页往前
                half = HELP_PANEL.centerx
                help_turn_page(-1 if pos[0] < half else 1)
            return
        if ov == "import":
            p, snap_rows, field, do_r, clear_r, sec_y, msg_y, file_r = import_layout(S)
            if import_close_rect(p).collidepoint(pos):
                close_overlay()
            elif field.collidepoint(pos):
                S["import_focus"] = True
            elif file_r.collidepoint(pos):
                import_from_file()
            elif do_r.collidepoint(pos):
                import_from_text(S["import_buf"])
            elif clear_r.collidepoint(pos):
                S["import_buf"] = ""
                S["import_msg"] = ""
            else:
                S["import_focus"] = False       # 点空白处取消聚焦
            return
        # 无浮层：主页功能按钮
        for rect, key, label, style in home_button_rects():
            if not rect.collidepoint(pos):
                continue
            if key == "battle":
                start_from(POSITIONS["标准开局"], "标准开局")
                S["screen"] = "battle"
                S["editing"] = False
                S["lib_open"] = False
                S["message"] = "标准开局，红方先行。"
            elif key == "endgame":
                S["entries"] = load_library()
                S["screen"] = "battle"
                S["lib_open"] = True
                S["lib_del_pending"] = None
                S["edit_msg"] = ""
                S["lib_off"] = max(0, min(library_max_off(len(S["entries"])),
                                          int(S.get("lib_off", 0))))
            elif key == "edit":
                enter_edit()
                S["screen"] = "battle"
            elif key == "import":
                open_overlay("import")
            elif key == "settings":
                open_overlay("settings")
            elif key == "instructions":
                open_overlay("instructions")
            elif key == "quit":
                # 主页「退出」：桌面关窗口，手机结束 Activity 回桌面
                S["quit_requested"] = True
            beep("select")
            return


    def mark_entry_done(winner=None):
        """从残局库载入的局面打赢了，就在库里标「已通关」并记下胜方。
        按实际胜方判定：只有人类执子方获胜才算通关（黑先排局人类执黑同样算）。"""
        winner = winner or HUMAN_SIDE
        if winner != HUMAN_SIDE:
            return
        name = S.get("lib_entry") or ""
        if not name:
            return
        moves = len(S.get("history") or [])
        for entry in S["entries"]:
            if entry.get("name") == name:
                if entry.get("done") and entry.get("done_side") == winner:
                    # 已经通关过：只有走得更少才更新记录，否则不动
                    old_moves = int(entry.get("done_moves") or 0)
                    if old_moves and moves >= old_moves:
                        return
                entry["done"] = True
                entry["done_side"] = winner
                entry["done_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                entry["done_moves"] = moves
                entry["done_secs"] = int(max(0.0, time.perf_counter()
                                             - float(S.get("battle_start") or
                                                     time.perf_counter())))
                try:
                    save_library(S["entries"])
                except OSError:
                    pass
                return

    def toggle_bgm():
        """对局中随手开关背景音乐（M 键或底部「音乐」按钮）"""
        S["bgm_on"] = not S["bgm_on"]
        if not S["bgm_on"]:
            stop_bgm()
        else:
            S["bgm_state"] = {}
        persist_settings()
        S["message"] = "背景音乐已%s。" % ("开启" if S["bgm_on"] else "关闭")
        beep("select")

    def save_from_battle():
        """把当前对局局面存进残局库（对战 / 残局都可用，走摆棋那套校验与命名）"""
        if S["over"]:
            S["message"] = "对局已结束，不能再存局。按「重开」后可继续。"
            beep("illegal")
            return
        ok, why = validate_position(S["board"])
        if not ok:
            S["message"] = "当前局面不符合存库要求（%s），未保存。" % why
            beep("illegal")
            return
        if not (S["custom_name"] or "").strip():
            open_naming("save")
            S["message"] = "给这局局面起个名字，回车即存入残局库。"
            return
        save_current()

    def cancel_hint():
        job = S.get("hint_job")
        S["hint_job"] = None
        if job is not None:
            job.cancel()

    def give_hint():
        """算一手推荐着法，标在棋盘上。
        以前是主线程直接搜 3 层、0.9 秒：残局里常常算不到关键着，提示的棋很"傻"，
        而且这段时间界面完全不动（手机上这时上滑必然黑屏/无响应）。
        现在改成后台线程，深度放到 8 层、最多 2 秒，界面照常 60 帧。"""
        job = S.get("hint_job")
        if job is not None and not job.done:
            S["message"] = "还在为你想这一手，稍等…"
            beep("illegal")
            return
        if S.get("ai_job") is not None:
            S["message"] = "%s还在思考，等它走完再要提示。" % ai_label()
            beep("illegal")
            return
        if S["over"] or S["replay"]:
            S["message"] = "对局已结束，无法提示。"
            beep("illegal")
            return
        if S["turn"] != HUMAN_SIDE:
            S["message"] = "等%s走完再提示。" % ai_label()
            beep("illegal")
            return
        avoid = banned_repeats(S["board"], HUMAN_SIDE, S["rep_counts"],
                               ban_check_repeat=True)   # 提示不推荐走成长将的着法
        S["hint"] = None
        S["move_hints"] = []
        # 残局里「提示的棋不对」多半是搜得太浅：以前 8 层 / 2.4 秒，穷一点的局面
        # 连两三步的兑子都算不完。现在放后台深搜到 12 层、给到 5 秒（桌面 4 秒），
        # 反正不占主线程，界面照常 60 帧，多出的时间全换成层数。
        S["hint_job"] = AiJob(S["board"], HUMAN_SIDE, 12, banned=avoid,
                              budget=5.0 if IS_ANDROID else 4.0)
        S["hint_job"].start()
        S["message"] = "正在为你想一手（深搜四五秒，界面不会卡住）…"
        beep("select")

    def offer_draw():
        """人类提和：电脑按形势判断是否接受。
        以前只有「红方分值 >= -120」才接受，等于默认人类执红；
        现在按电脑自己的处境算，它没占到明显便宜（不到一个兵的优）就答应。"""
        if S["over"]:
            S["message"] = "对局已结束。"
            beep("illegal")
            return
        if S["cpu_offer"]:
            accept_offer()
            return
        score = evaluate(S["board"])          # 正数红方好
        mine = score if AI_SIDE == RED else -score
        if mine <= 120 or insufficient_material(S["board"]):
            S["over"] = True
            S["turn"] = None
            S["cpu_offer_times"] = DRAW_OFFER_MAX   # 已经和了，别再开口
            S["message"] = "和棋 —— %s接受提和，握手言和。" % ai_label()
            S["result"] = "和棋 —— 双方协议"
            beep("select")
        else:
            S["message"] = "%s拒绝了提和：它觉得自己占优，接着下。" % ai_label()
            beep("illegal")

    def offer_reason():
        """电脑想提和的理由：判定逻辑在模块级 cpu_draw_reason 里，这里只喂当前状态"""
        reps = max(S["rep_counts"].values()) if S["rep_counts"] else 0
        return cpu_draw_reason(S["board"], len(S["history"]), S["quiet_halfmoves"],
                               reps, S.get("cpu_offer_no", -99), AI_SIDE,
                               declined=int(S.get("cpu_offer_times", 0)))

    def maybe_cpu_offer():
        """电脑走完一手后自检：该提和还是该认输。
        必败的残局（只剩老将、对方多子）先低头求和；人类不答应，
        再撑几个回合就主动认输——但认输弹窗也给了「继续下」，让人类亲手吃将。"""
        if S["over"] or S["cpu_offer"] or S["replay"] or S["editing"]:
            return
        if S.get("cpu_given_up"):
            return                      # 已经说过「不用你认输」，之后不再打扰
        asked = int(S.get("cpu_offer_times", 0))
        hopeless = cpu_hopeless(S["board"], AI_SIDE)
        if hopeless:
            if len(S["history"]) >= int(S.get("resign_at", 10 ** 9)):
                S["cpu_offer"] = {"kind": "resign", "who": ai_label(), "reason": (
                    "上一回跟你求和没谈成，我又撑了几个回合，实在没招了，认输。"
                    "你要想亲手把将吃掉，点「继续下」就行。")}
                S["offer_elapsed"] = max(0.0, time.perf_counter() - S["turn_start"])
                S["message"] = ("%s认输 —— 接受，或点「继续下」自己把将吃下来。"
                                % ai_label())
                beep("select")
                return
            if (asked < DRAW_OFFER_MAX
                    and len(S["history"]) - int(S.get("cpu_offer_no", -99))
                    >= DRAW_OFFER_GAP * (asked + 1)):
                S["cpu_offer"] = {"kind": "draw", "who": ai_label(),
                                  "reason": hopeless + (
                    "要不先和了？不答应我再撑几个回合，撑不住就认输。")}
                S["offer_elapsed"] = max(0.0, time.perf_counter() - S["turn_start"])
                S["message"] = ("%s提议和棋 —— 同意或继续下，看弹窗里的说明。"
                                % ai_label())
                beep("select")
                return
        reason = offer_reason()
        if not reason:
            return
        if not reason.endswith(("。", "？")):
            reason += "。"
        # 用户要的口气：不逼人，「不答应也行，过几步再来问」。第三次是最后一次，
        # 就别许空诺，改成「我不再提了」，免得话说出去做不到。
        if int(S.get("cpu_offer_times", 0)) < DRAW_OFFER_MAX - 1:
            reason += "不答应也行，过几步我再提一回。"
        else:
            reason += "不答应就接着下，我不再提了。"
        S["cpu_offer"] = {"kind": "draw", "who": ai_label(), "reason": reason}
        S["offer_elapsed"] = max(0.0, time.perf_counter() - S["turn_start"])
        S["message"] = ("%s提议和棋 —— 同意或继续下，看弹窗里的说明。" % ai_label())
        beep("select")

    def accept_offer():
        """同意和棋 / 接受认输"""
        kind = (S["cpu_offer"] or {}).get("kind", "draw")
        S["cpu_offer"] = None
        S["over"] = True
        S["turn"] = None
        if kind == "resign":
            S["result"] = "%s胜 —— %s认输" % (name_of(HUMAN_SIDE), name_of(AI_SIDE))
            S["message"] = S["result"] + "（%s只剩老将，撑不下去了）。" % ai_label()
            mark_entry_done(HUMAN_SIDE)
            beep("win")
        else:
            S["result"] = "和棋 —— %s提议，双方同意" % ai_label()
            S["message"] = "和棋 —— 双方握手言和，这一局到此结束。"
            S["cpu_offer_times"] = DRAW_OFFER_MAX   # 已经和了，别再开口
            beep("select")

    def decline_offer():
        """拒绝提和 / 不接受认输：接着下。
        提和被拒后记下手数，间隔一次比一次长、最多问三回；必败局则几个回合后认输。"""
        kind = (S["cpu_offer"] or {}).get("kind", "draw")
        S["cpu_offer"] = None
        S["cpu_offer_no"] = len(S["history"])
        S["cpu_offer_times"] = int(S.get("cpu_offer_times", 0)) + 1
        S["turn_start"] = time.perf_counter()      # 弹窗期间冻结的计时从这里继续
        if kind == "resign":
            S["cpu_given_up"] = True
            S["message"] = "好，不用你认输 —— 接着走，把将吃掉这局才算完。"
        elif cpu_hopeless(S["board"], AI_SIDE):
            S["resign_at"] = len(S["history"]) + RESIGN_AFTER_DECLINE
            S["message"] = ("好，接着下。我再撑 %d 个回合，翻不了盘就认输。"
                            % (RESIGN_AFTER_DECLINE // 2))
        else:
            left = DRAW_OFFER_MAX - S["cpu_offer_times"]
            if left <= 0:
                S["message"] = "好，接着下。这一局我不再提和了，陪你走到终局。"
            else:
                S["message"] = ("好，接着下。我过几手若还觉得分不出胜负才会再提，"
                                "这一局最多还提 %d 回。" % left)
        beep("select")

    def perform_move(fr, fc, tr, tc, mover):
        """执行一步棋：保存快照、记谱、结算用时、播放音效、判断将军与胜负"""
        cancel_hint()          # 局面变了，上一手算出来的提示不能再标在盘上
        S["undo_stack"].append({
            "board": dict(S["board"]),
            "turn": S["turn"],
            "counts": dict(S["counts"]),
            "remain": dict(S["remain"]),
            "over": S["over"],
            "result": S["result"],
            "history": list(S["history"]),
            "last_move": S["last_move"],
            "turn_start": S["turn_start"],
            "rep_counts": dict(S["rep_counts"]),
            "pos_log": list(S["pos_log"]),
            "quiet": S["quiet_halfmoves"],
            "streak": dict(S["check_streak"]),
        })
        captured = (tr, tc) in S["board"]
        mover_piece = S["board"].get((fr, fc))
        victim_piece = S["board"].get((tr, tc))
        notation = move_notation(S["board"], fr, fc, tr, tc, mover)
        board = apply_move(S["board"], fr, fc, tr, tc)
        S["board"] = board
        # 走子动画：棋子从起点滑到落点，落定后再荡开一圈涟漪
        stamp = time.perf_counter()
        S["anim"] = {"fr": fr, "fc": fc, "tr": tr, "tc": tc,
                     "piece": mover_piece, "victim": victim_piece,
                     "t0": stamp, "dur": 0.22}
        S["ripple"] = (tr, tc, stamp + 0.22)
        S["drag"] = None
        S["remain"][mover] = max(0.0, S["remain"][mover]
                                 - (time.perf_counter() - S["turn_start"]))
        S["counts"][mover] += 1
        S["selected"] = None
        S["move_hints"] = []
        S["hint"] = None
        S["surrender_pending"] = False
        S["last_move"] = (fr, fc, tr, tc, mover)
        S["history"].append({
            "side": name_of(mover),
            "text": notation + ("（吃子）" if captured else ""),
            "left": fmt_time(S["remain"][mover]),
            "fr": fr, "fc": fc, "tr": tr, "tc": tc,
        })

        enemy = opponent(mover)
        if captured:
            beep("capture")
        else:
            # 上三路清脆、下三路低沉，中间一档过渡
            beep("move_a" if tr <= 3 else ("move_b" if tr <= 6 else "move_c"))

        checked = in_check(board, enemy)
        # 规则计数：重复局面 / 无吃子半回合 / 连续将军
        key = position_key(board, enemy)
        S["rep_counts"][key] = S["rep_counts"].get(key, 0) + 1
        S["pos_log"].append({"key": key, "mover": mover, "check": checked})
        S["quiet_halfmoves"] = 0 if captured else S["quiet_halfmoves"] + 1
        if checked:
            S["check_streak"][mover] = S["check_streak"].get(mover, 0) + 1
            S["check_streak"][enemy] = 0
        else:
            S["check_streak"][mover] = 0

        if not legal_moves(board, enemy):
            S["over"] = True
            S["turn"] = None
            if checked:
                S["message"] = "%s胜 —— 将死%s。" % (name_of(mover), name_of(enemy))
                S["result"] = "%s胜 —— 将死%s" % (name_of(mover), name_of(enemy))
            else:
                S["message"] = "%s胜 —— %s困毙无子可动。" % (name_of(mover), name_of(enemy))
                S["result"] = "%s胜 —— %s困毙" % (name_of(mover), name_of(enemy))
            if mover == HUMAN_SIDE:
                mark_entry_done(mover)
            beep("win")
            return

        # 子力不足：双方都只剩将帅士象（至多各一匹单马），再走也分不出胜负。
        # 以前这种盘面要磨到「六十回合无吃子」才判和，用户看着就是和定了还在下。
        if insufficient_material(board):
            S["over"] = True
            S["turn"] = None
            S["result"] = "和棋 —— 双方子力不足"
            S["message"] = ("和棋 —— 盘上只剩将帅士象（或单马），"
                            "谁都将不死对方，按子力不足判和。")
            beep("select")
            return

        # 三次重复局面：按整个循环里谁在将军来裁决（被迫应着的一方不算长将）
        rp = repeat_cycle_verdict(S["pos_log"], key, mover, enemy,
                                  S["rep_counts"].get(key, 0))
        if rp is not None:
            kind, text, winner = rp
            S["over"] = True
            S["turn"] = None
            S["result"] = text
            if kind == "draw":
                S["message"] = text + "（同一局面第 %d 次出现）。" % REPEAT_BLOCK
                beep("select")
            else:
                S["message"] = ("%s（同一局面第 %d 次出现，这一轮里一直在将军，按长将判负）。"
                                % (text, REPEAT_BLOCK))
                if winner == HUMAN_SIDE:
                    mark_entry_done(winner)
                    beep("win")
                else:
                    beep("lose")
            return

        verdict = rule_verdict(S["rep_counts"], key, S["quiet_halfmoves"],
                               S["check_streak"], mover, enemy)
        if verdict is not None:
            kind, result = verdict
            S["over"] = True
            S["turn"] = None
            S["result"] = result
            if kind == "long_check":
                S["message"] = result + "。"
                if enemy == HUMAN_SIDE:
                    mark_entry_done(enemy)
                beep("win")
            else:
                S["message"] = "和棋 —— 六十回合内没有吃子，判和。"
                beep("select")
            return

        if checked:
            beep("check")
        S["turn"] = enemy
        S["turn_start"] = time.perf_counter()
        S["message"] = ("将军！%s应将。" if checked else "%s走棋。") % name_of(enemy)

    def rebuild_board(steps):
        """根据开局局面重放前 steps 着，得到复盘用棋盘"""
        board = dict(S["start_board"])
        for i in range(steps):
            h = S["history"][i]
            board = apply_move(board, h["fr"], h["fc"], h["tr"], h["tc"])
        return board

    def undo():
        """悔棋：回退到玩家上一步之前（连退对手的应着）"""
        cancel_ai()
        cancel_hint()
        S["cpu_offer"] = None      # 悔棋等于不认这次提和，弹窗先关掉
        if not S["undo_stack"]:
            S["message"] = "当前没有可以悔的棋。"
            beep("illegal")
            return
        if S["undo_limit"] and S["undo_left"] <= 0:
            S["message"] = "本局悔棋次数已用完（设置里可改为「不限」）。"
            beep("illegal")
            return
        if S["undo_limit"]:
            S["undo_left"] -= 1
        while S["undo_stack"]:
            snap = S["undo_stack"].pop()
            S["board"] = dict(snap["board"])
            S["turn"] = snap["turn"]
            S["counts"] = dict(snap["counts"])
            S["remain"] = dict(snap["remain"])
            S["over"] = snap["over"]
            S["result"] = snap["result"]
            S["history"] = list(snap["history"])
            S["last_move"] = snap["last_move"]
            S["selected"] = None
            S["rep_counts"] = dict(snap.get("rep_counts", {}))
            S["pos_log"] = list(snap.get("pos_log", []))
            S["quiet_halfmoves"] = snap.get("quiet", 0)
            S["check_streak"] = dict(snap.get("streak", {RED: 0, BLACK: 0}))
            S["move_hints"] = []
            S["hint"] = None
            if S["turn"] == HUMAN_SIDE:
                break
        S["turn_start"] = time.perf_counter()
        left = ("，本局还可悔 %d 次" % S["undo_left"]) if S["undo_limit"] else ""
        S["message"] = "已退回上一步，请重新走子%s。" % left
        beep("select")

    def enter_replay():
        """进入复盘：从最后一手开始逐步回放"""
        if not S["history"]:
            S["message"] = "还没有可复盘的棋谱，先走几步吧。"
            beep("illegal")
            return
        S["replay"] = True
        S["replay_index"] = len(S["history"])
        S["replay_auto"] = False
        S["replay_last"] = time.perf_counter()
        S["selected"] = None
        beep("select")

    if boot:
        boot.finish()          # 补够最短时长 + 淡出，然后进主页
    fps = pygame.time.Clock()
    running = True
    frame_no = 0
    while running:
        frame_no += 1
        if S.get("quit_requested"):
            running = False
            break
        # 手机切后台再回来时偶尔会丢 Surface（表现为整屏黑），每半秒核对一次尺寸
        if IS_ANDROID and frame_no % 30 == 0:
            try:
                _sz = pygame.display.get_window_size()
            except (pygame.error, AttributeError):
                _sz = (win_w, win_h)
            if _sz[0] > 0 and _sz[1] > 0 and tuple(_sz) != (win_w, win_h):
                win_w, win_h = _sz
                draw_w, draw_h, off_x, off_y = fit_layout(win_w, win_h)
                screen = pygame.Surface((SCREEN_W, SCREEN_H))
        # 拖动只在「对局中、轮到玩家」时有效，换屏 / 终局 / 复盘一律清掉，免得残留
        if S["drag"] is not None and (S["screen"] != "battle" or S["over"]
                                      or S["replay"] or S["editing"]
                                      or S["turn"] != HUMAN_SIDE):
            S["drag"] = None
        # ---- 超时判定（仅对局中）：先看总包干，再看单步限时 ----
        if (S["screen"] == "battle" and not S["editing"] and not S["over"]
                and not S["replay"] and S["turn"] is not None):
            spent = time.perf_counter() - S["turn_start"]
            move_cap = int(S.get("move_limit", 0))
            if S["remain"][S["turn"]] - spent <= 0:
                loser = S["turn"]
                S["remain"][loser] = 0.0
                S["over"] = True
                S["turn"] = None
                S["message"] = "%s胜 —— %s超时判负。" % (
                    name_of(opponent(loser)), name_of(loser))
                S["result"] = "%s胜 —— %s超时判负" % (
                    name_of(opponent(loser)), name_of(loser))
                if loser == AI_SIDE:
                    mark_entry_done(opponent(loser))
                    beep("win")
                else:
                    beep("lose")
            elif move_cap > 0 and spent >= move_cap:
                loser = S["turn"]
                S["over"] = True
                S["turn"] = None
                S["message"] = "%s胜 —— %s单步超时（限 %d 秒）。" % (
                    name_of(opponent(loser)), name_of(loser), move_cap)
                S["result"] = "%s胜 —— %s单步超时" % (
                    name_of(opponent(loser)), name_of(loser))
                if loser == AI_SIDE:
                    mark_entry_done(opponent(loser))
                    beep("win")
                else:
                    beep("lose")

        # ---- 事件 ----
        # ---- 事件（窗口缩放时把鼠标坐标换算回逻辑画布坐标） ----
        events = pygame.event.get()
        if (win_w, win_h) != (SCREEN_W, SCREEN_H):
            for ev in events:
                if "pos" in ev.dict:
                    ev.dict["pos"] = to_logical(ev.dict["pos"])
        for event in events:
            # 切后台 / 回到前台：安卓的 Surface 可能已被系统回收，重建一次并立刻重画
            _wev = getattr(pygame, "WINDOWEVENT", None)
            if _wev is not None and event.type == _wev:
                _wake = tuple(getattr(pygame, _n, -1) for _n in (
                    "WINDOWEVENT_FOCUS_GAINED", "WINDOWEVENT_SHOWN",
                    "WINDOWEVENT_RESTORED", "WINDOWEVENT_EXPOSED"))
                if IS_ANDROID and getattr(event, "event", None) in _wake:
                    try:
                        _sz = pygame.display.get_window_size()
                    except (pygame.error, AttributeError):
                        _sz = (win_w, win_h)
                    if _sz[0] > 0 and _sz[1] > 0 and tuple(_sz) != (win_w, win_h):
                        win_w, win_h = _sz
                        draw_w, draw_h, off_x, off_y = fit_layout(win_w, win_h)
                        screen = pygame.Surface((SCREEN_W, SCREEN_H))
                    try:
                        pygame.display.flip()
                    except pygame.error:
                        pass
                continue
            if (IS_ANDROID and event.type == pygame.KEYDOWN
                    and event.key == getattr(pygame, "K_AC_BACK", -999)):
                # 安卓物理返回键：与关窗口同一套退让逻辑（浮层先关、对局先回主页、主页才退出）
                if S["home_overlay"]:
                    close_overlay()
                elif S["screen"] != "home":
                    if S["editing"]:
                        leave_edit(True)
                    esc_back_home()
                else:
                    running = False
                continue

            if event.type == pygame.QUIT:
                # 关窗口不直接退出：浮层先关，对局/摆棋先回主页，只有主页可退出
                if S["home_overlay"]:
                    close_overlay()
                elif S["screen"] != "home":
                    if S["editing"]:
                        leave_edit(True)
                    esc_back_home()
                else:
                    running = False
                continue

            if event.type == pygame.TEXTINPUT and S["naming"]:
                if S.get("name_fresh"):
                    S["name_buf"] = ""      # 改名时首次输入直接整行替换旧名
                    S["name_fresh"] = False
                S["name_buf"] = (S["name_buf"] + event.text)[:24]
                continue

            # 音量滑块拖动
            if (event.type == pygame.MOUSEMOTION and S["vol_drag"]
                    and S["home_overlay"] == "settings"):
                for rect, cat, _val in settings_hitboxes(S)[0]:
                    if cat == S["vol_drag"]:
                        set_volume_from_x(cat, rect, event.pos[0])
                        break
                continue
            if event.type == pygame.MOUSEBUTTONUP and S["vol_drag"]:
                S["vol_drag"] = None
                persist_settings()
                continue

            # 残局库搜索框
            if event.type == pygame.TEXTINPUT and S["lib_open"] and S["lib_focus"]:
                S["lib_query"] = (S["lib_query"] + event.text)[:20]
                S["lib_off"] = 0
                S["edit_msg"] = ""        # 换了筛选条件，上一条操作提示就不再挂着
                continue
            if event.type == pygame.KEYDOWN and S["lib_open"] and S["lib_focus"]:
                if event.key == pygame.K_BACKSPACE:
                    S["lib_query"] = S["lib_query"][:-1]
                    S["lib_off"] = 0
                    S["edit_msg"] = ""
                elif event.key == pygame.K_ESCAPE:
                    if S["lib_query"]:
                        S["lib_query"] = ""
                    S["lib_focus"] = False
                    S["edit_msg"] = ""
                    try:
                        pygame.key.stop_text_input()
                    except (AttributeError, pygame.error):
                        pass
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    S["lib_focus"] = False
                continue

            # 残局库：↑↓ 一行一行滚动，PgUp/PgDn 整屏，Home/End 到头
            if event.type == pygame.KEYDOWN and S["lib_open"] and not S["lib_focus"]:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP,
                                 pygame.K_PAGEDOWN, pygame.K_HOME, pygame.K_END):
                    _, _, _, total, _ = library_layout(
                        S["entries"], S.get("lib_off", 0), S["lib_category"],
                        S["lib_query"], S.get("lib_pieces", "全部"),
                        S.get("lib_level", "全部"))
                    off = int(S.get("lib_off", 0))
                    if event.key == pygame.K_UP:
                        off -= 1
                    elif event.key == pygame.K_DOWN:
                        off += 1
                    elif event.key == pygame.K_PAGEUP:
                        off -= LIB_PAGE_SIZE
                    elif event.key == pygame.K_PAGEDOWN:
                        off += LIB_PAGE_SIZE
                    elif event.key == pygame.K_HOME:
                        off = 0
                    else:
                        off = library_max_off(total)
                    S["lib_off"] = max(0, min(library_max_off(total), off))
                    S["edit_msg"] = ""
                    persist_lib_page()
                    beep("select")
                    continue

            # 主页（含浮层）输入优先：处理完后跳过对局逻辑
            if S["screen"] == "home":
                home_event(event)
                continue

            # 复盘模式下独占输入
            if S["replay"] and not S["naming"]:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        S["replay"] = False
                    elif event.key == pygame.K_LEFT:
                        S["replay_index"] = max(0, S["replay_index"] - 1)
                    elif event.key == pygame.K_RIGHT:
                        S["replay_index"] = min(len(S["history"]), S["replay_index"] + 1)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        S["replay_auto"] = not S["replay_auto"]
                        S["replay_last"] = time.perf_counter()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, key in replay_button_rects():
                        if rect.collidepoint(event.pos):
                            if key == "prev":
                                S["replay_index"] = max(0, S["replay_index"] - 1)
                            elif key == "next":
                                S["replay_index"] = min(len(S["history"]), S["replay_index"] + 1)
                            elif key == "auto":
                                S["replay_auto"] = not S["replay_auto"]
                                S["replay_last"] = time.perf_counter()
                            elif key == "quit":
                                S["replay"] = False
                            beep("select")
                            break
                continue

            if event.type == pygame.KEYDOWN:
                # 提和弹窗是模态：期间只认 Esc（继续下）和回车（同意），
                # 别的快捷键一律不理，免得一边看说明一边把棋走出来
                if S["cpu_offer"] and not S["naming"]:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        accept_offer()
                    elif event.key == pygame.K_ESCAPE:
                        decline_offer()
                    continue
                if S["naming"]:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        close_naming(True)
                        beep("select")
                    elif event.key == pygame.K_ESCAPE:
                        close_naming(False)
                    elif event.key == pygame.K_BACKSPACE:
                        S["name_fresh"] = False
                        S["name_buf"] = S["name_buf"][:-1]
                    elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                        S["name_fresh"] = False
                        S["name_buf"] = (S["name_buf"] + paste_clipboard())[:24]
                    continue

                if event.key == pygame.K_ESCAPE:
                    if S["cpu_offer"]:
                        decline_offer()      # 弹窗开着：Esc 等于「继续下」
                    elif S["lib_open"]:
                        S["lib_open"] = False
                        S["lib_focus"] = False
                        S["lib_query"] = ""
                        S["edit_msg"] = ""
                    elif S["replay"]:
                        S["replay"] = False
                    elif S["editing"]:
                        leave_edit(True)
                        S["message"] = "已取消摆棋，恢复原局面。"
                    else:
                        esc_back_home()
                elif event.key == pygame.K_e:
                    if S["lib_open"]:
                        S["lib_open"] = False
                        S["edit_msg"] = ""
                    elif S["editing"]:
                        leave_edit(True)
                    else:
                        enter_edit()
                elif S["editing"] or S["lib_open"]:
                    continue
                elif event.key == pygame.K_r:
                    reset_position(S["position"])
                elif event.key == pygame.K_1:
                    reset_position("残局示例")
                elif event.key == pygame.K_2:
                    reset_position("标准开局")
                elif event.key == pygame.K_s:
                    S["sound_on"] = not S["sound_on"]
                    beep("select")
                    S["message"] = "音效已%s。" % ("开启" if S["sound_on"] else "关闭")
                elif event.key == pygame.K_m:
                    toggle_bgm()
                elif event.key == pygame.K_l:
                    S["entries"] = load_library()
                    S["lib_open"] = True
                    S["lib_del_pending"] = None
                    S["lib_query"] = ""
                    S["lib_focus"] = False
                    S["edit_msg"] = ""
                    S["lib_off"] = max(0, min(library_max_off(len(S["entries"])),
                                              int(S.get("lib_off", 0))))
                    beep("select")
                elif event.key == pygame.K_g:
                    ok, info = export_record(S)
                    S["message"] = ("棋谱已导出：%s" % info) if ok else info
                    beep("select" if ok else "illegal")
                elif event.key == pygame.K_h:
                    give_hint()
                elif event.key == pygame.K_u:
                    undo()
                elif event.key == pygame.K_p:
                    enter_replay()
                continue

            # 残局库滚动条：滚轮 / 拖动 / 释放
            if event.type == pygame.MOUSEWHEEL and S["lib_open"]:
                _, _, _, total, _ = library_layout(
                    S["entries"], S.get("lib_off", 0), S["lib_category"],
                    S["lib_query"], S.get("lib_pieces", "全部"),
                        S.get("lib_level", "全部"))
                S["lib_off"] = max(0, min(library_max_off(total),
                                          S.get("lib_off", 0) - event.y * 3))
                S["edit_msg"] = ""
                persist_lib_page()
                continue
            if event.type == pygame.MOUSEMOTION and S["scroll_drag"]:
                _, _, _, total, scroll = library_layout(
                    S["entries"], S.get("lib_off", 0), S["lib_category"],
                    S["lib_query"], S.get("lib_pieces", "全部"),
                        S.get("lib_level", "全部"))
                if scroll:
                    S["lib_off"] = library_scroll_off(
                        scroll, total, event.pos[1], S["scroll_grab"])
                continue
            if (event.type == pygame.MOUSEBUTTONUP and event.button == 1
                    and S["scroll_drag"]):
                S["scroll_drag"] = False
                persist_lib_page()      # 拖动结束记录定位
                continue

            # ---- 拖着棋子走：按住拖、松开落；不想拖就照旧点两下 ----
            if S["drag"] is not None:
                drag = S["drag"]
                if event.type == pygame.MOUSEMOTION:
                    drag["pos"] = event.pos
                    if not drag["moved"]:
                        sx, sy = board_to_pixel(drag["fr"], drag["fc"])
                        if abs(event.pos[0] - sx) > 5 or abs(event.pos[1] - sy) > 5:
                            drag["moved"] = True
                    continue
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    S["drag"] = None
                    if not drag["moved"]:
                        continue                    # 只是点了一下，交给点击逻辑
                    target = pixel_to_board_snap(*event.pos)
                    sr, sc = drag["fr"], drag["fc"]
                    if not target or target == (sr, sc):
                        S["message"] = "棋子放回原处（松开时不在交叉点上）。"
                        continue
                    r, c = target
                    all_moves = legal_moves(S["board"], S["turn"])
                    if (sr, sc, r, c) in all_moves:
                        bad = banned_repeats(S["board"], S["turn"], S["rep_counts"],
                                             all_moves)
                        if (sr, sc, r, c) in bad:
                            S["message"] = ("不得重复走子：这一着会让同一局面第 %d 次出现，"
                                            "请换一着。" % REPEAT_BLOCK)
                            S["selected"] = (sr, sc)
                            S["move_hints"] = hint_moves(S["board"], S["turn"],
                                                         S["rep_counts"], (sr, sc))
                            beep("illegal")
                        else:
                            perform_move(sr, sc, r, c, HUMAN_SIDE)
                        continue
                    why = move_reason(S["board"], sr, sc, r, c)
                    S["message"] = why or "这一着走不通。"
                    S["selected"] = (sr, sc)
                    S["move_hints"] = hint_moves(S["board"], S["turn"],
                                                 S["rep_counts"], (sr, sc))
                    beep("illegal")
                    continue

            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            pos = event.pos
            # 电脑提和弹窗最优先：同意 / 继续下，两个按钮都好按；别处点了不算
            if S["cpu_offer"]:
                if event.button == 1:
                    for rect, kind in draw_offer_rects():
                        if rect.collidepoint(pos):
                            if kind == "accept":
                                accept_offer()
                            else:
                                decline_offer()
                            break
                continue
            if S["naming"]:
                # 改名浮层里可点「先行」切换红先 / 黑先
                if (event.button == 1 and S.get("naming_mode") == "rename"
                        and naming_turn_rect().collidepoint(pos)):
                    S["rename_turn"] = opponent(S.get("rename_turn", RED))
                    beep("select")
                continue

            # 残局库浮层优先
            if S["lib_open"]:
                if event.button == 1:
                    panel, rows, off, total, scroll = library_layout(
                        S["entries"], S.get("lib_off", 0), S["lib_category"],
                        S["lib_query"], S.get("lib_pieces", "全部"),
                        S.get("lib_level", "全部"))
                    sfield = library_search_rect(panel)
                    ex_rect, im_rect, rs_rect = library_io_rects(panel)
                    if sfield.collidepoint(pos):
                        S["lib_focus"] = True
                        try:
                            pygame.key.start_text_input()
                        except (AttributeError, pygame.error):
                            pass
                        beep("select")
                        continue
                    S["lib_focus"] = False
                    if ex_rect.collidepoint(pos):
                        export_library()
                        continue
                    if im_rect.collidepoint(pos):
                        import_library()
                        continue
                    if rs_rect.collidepoint(pos):
                        # 恢复是有破坏性的动作：先提示，4 秒内再点一次才真覆盖
                        now_t = time.perf_counter()
                        if now_t - float(S.get("lib_restore_t", -99)) <= 4.0:
                            S["lib_restore_t"] = -99
                            entries, msg = restore_library_backup()
                            S["edit_msg"] = msg
                            if entries:
                                S["entries"] = entries
                                clear_deleted_keys()
                                S["lib_off"] = 0
                                beep("select")
                            else:
                                beep("illegal")
                        else:
                            S["lib_restore_t"] = now_t
                            S["edit_msg"] = (
                                "要用最近一份备份覆盖当前库：4 秒内再点一次「恢复」即可。"
                                "当前库会先另存一份，恢复错了还能再退回来。")
                            beep("select")
                        continue
                    if library_piece_rect(panel).collidepoint(pos):
                        cur = S.get("lib_pieces", "全部")
                        try:
                            band_i = LIB_PIECE_BANDS.index(cur)
                        except ValueError:
                            band_i = 0
                        S["lib_pieces"] = LIB_PIECE_BANDS[
                            (band_i + 1) % len(LIB_PIECE_BANDS)]
                        S["lib_off"] = 0
                        S["edit_msg"] = ""
                        beep("select")
                        continue
                    if library_level_rect(panel).collidepoint(pos):
                        cur = S.get("lib_level", "全部")
                        try:
                            lv_i = LIB_LEVELS.index(cur)
                        except ValueError:
                            lv_i = 0
                        S["lib_level"] = LIB_LEVELS[(lv_i + 1) % len(LIB_LEVELS)]
                        S["lib_off"] = 0
                        S["edit_msg"] = ""
                        beep("select")
                        continue
                    # 分类标签切换
                    for trect, cat in library_category_rects(panel, LIB_CATEGORIES):
                        if trect.collidepoint(pos):
                            S["lib_category"] = cat
                            S["lib_off"] = 0
                            S["edit_msg"] = ""      # 换分类即清掉上一条提示
                            beep("select")
                            break
                    else:
                        if scroll:
                            track, thumb = scroll
                            if thumb.collidepoint(pos):
                                S["scroll_drag"] = True
                                S["scroll_grab"] = pos[1] - thumb.y
                            elif track.collidepoint(pos) and not thumb.collidepoint(pos):
                                step = LIB_PAGE_SIZE if pos[1] > thumb.centery else -LIB_PAGE_SIZE
                                S["lib_off"] = max(0, min(library_max_off(total), off + step))
                                S["edit_msg"] = ""
                                persist_lib_page()
                                beep("select")
                        prev_rect, next_rect = library_page_rects(panel, total)
                        if prev_rect and prev_rect.collidepoint(pos):
                            S["lib_off"] = max(0, off - LIB_PAGE_SIZE)
                            S["edit_msg"] = ""
                            persist_lib_page()
                            beep("select")
                        elif next_rect and next_rect.collidepoint(pos):
                            S["lib_off"] = min(library_max_off(total), off + LIB_PAGE_SIZE)
                            S["edit_msg"] = ""
                            persist_lib_page()
                            beep("select")
                        else:
                            done = False
                            for rect, idx in rows:
                                if library_star_rect(rect).collidepoint(pos):
                                    entry = S["entries"][idx]
                                    entry["fav"] = not entry.get("fav")
                                    S["lib_del_pending"] = None
                                    try:
                                        save_library(S["entries"])
                                    except OSError:
                                        pass
                                    S["edit_msg"] = ("已收藏「%s」。" if entry["fav"]
                                                     else "已取消收藏「%s」。") % entry.get(
                                        "name", "未命名")
                                    beep("select")
                                    done = True
                                    break
                                if library_delete_rect(rect).collidepoint(pos):
                                    name = S["entries"][idx].get("name", "未命名")
                                    # 删除需二次确认：第一次点亮「确认」，再次点击才删除
                                    if S["lib_del_pending"] == idx:
                                        gone = S["entries"][idx]
                                        remember_deleted(gone)   # 记一笔，升级补库时不再加回来
                                        del S["entries"][idx]
                                        try:
                                            save_library(S["entries"])
                                        except OSError:
                                            pass
                                        S["lib_del_pending"] = None
                                        S["edit_msg"] = "已删除「%s」。" % name
                                        beep("illegal")
                                    else:
                                        S["lib_del_pending"] = idx
                                        S["edit_msg"] = (
                                            "再点一次「确认」即可删除「%s」。"
                                            % name)
                                        beep("select")
                                    done = True
                                    break
                                if rect.collidepoint(pos):
                                    S["lib_del_pending"] = None
                                    load_entry(idx)
                                    done = True
                                    break
                            if not done:
                                S["lib_del_pending"] = None
                                if not panel.collidepoint(pos):
                                    S["lib_open"] = False
                continue

            # 顶部设置栏
            if event.button == 1:
                handled = False
                for rect, kind in control_hitboxes():
                    if not rect.collidepoint(pos):
                        continue
                    if kind[0] == "diff":
                        S["difficulty"] = kind[1]
                        S["message"] = "难度已切换为「%s」（AI 最多搜 %d 层）。" % (
                            kind[1], DIFFICULTY_DEPTH[kind[1]])
                        beep("select")
                    elif kind[0] == "diff_cycle":
                        names = [lab for lab, _d in DIFFICULTY_LEVELS]
                        try:
                            idx = names.index(S["difficulty"])
                        except ValueError:
                            idx = 0
                        S["difficulty"] = names[(idx + 1) % len(names)]
                        S["message"] = "难度已切换为「%s」（再点一下换下一档）。" % (
                            S["difficulty"],)
                        beep("select")
                    elif kind[0] == "music":
                        toggle_bgm()
                    elif kind[0] == "sound":
                        S["sound_on"] = not S["sound_on"]
                        beep("select")
                        S["message"] = "音效已%s。" % ("开启" if S["sound_on"] else "关闭")
                    elif kind[0] == "move":
                        cur = int(S.get("move_limit", 0))
                        try:
                            idx = MOVE_TIME_OPTIONS.index(cur)
                        except ValueError:
                            idx = 0
                        S["move_limit"] = MOVE_TIME_OPTIONS[
                            (idx + 1) % len(MOVE_TIME_OPTIONS)]
                        persist_settings()
                        beep("select")
                        S["message"] = ("单步限时已改为「%s」：圆表走完这一手就判超时负。"
                                        % move_limit_label(S["move_limit"])
                                        if S["move_limit"] else
                                        "单步限时已关闭（不限时），圆表只显示这一手用了多久。")
                    elif kind[0] == "edit":
                        if S["editing"]:
                            leave_edit(True)
                            S["message"] = "已退出摆棋，恢复原局面。"
                        else:
                            enter_edit()
                    elif kind[0] == "lib":
                        S["entries"] = load_library()
                        S["lib_open"] = True
                        S["lib_del_pending"] = None
                        S["edit_msg"] = ""
                        # 恢复上次定位（并夹到合法范围）
                        S["lib_off"] = max(0, min(library_max_off(len(S["entries"])),
                                                  int(S.get("lib_off", 0))))
                        beep("select")
                    elif kind[0] == "save":
                        save_current()
                    handled = True
                    break
                if handled:
                    continue

            # 摆棋模式
            if S["editing"]:
                if event.button == 3:
                    target = pixel_to_board(*pos)
                    if target and target in S["board"]:
                        del S["board"][target]
                        beep("illegal")
                    continue
                if event.button != 1:
                    continue

                acted = False
                for rect, piece, avail in palette_rects(S["board"]):
                    if not rect.collidepoint(pos):
                        continue
                    pc, pt = piece
                    if not avail:
                        S["edit_msg"] = "%s「%s」已全部摆上（%d/%d），要再放请先擦除一枚。" % (
                            name_of(pc), CHINESE_PIECES[piece],
                            PIECE_MAX.get(pt, 1), PIECE_MAX.get(pt, 1))
                        S["message"] = S["edit_msg"]
                        beep("illegal")
                    else:
                        S["edit_piece"] = piece
                        S["edit_msg"] = "已选%s「%s」，点击棋盘放置（底板还剩 %d 枚）。" % (
                            name_of(pc), CHINESE_PIECES[piece],
                            palette_remaining(S["board"], piece))
                        beep("select")
                    acted = True
                    break
                if acted:
                    continue

                for rect, (key, label) in edit_action_rects():
                    if not rect.collidepoint(pos):
                        continue
                    if key == "erase":
                        S["edit_piece"] = "erase"
                        S["edit_msg"] = "擦除模式：点击棋子即可移除。"
                    elif key == "clear":
                        S["board"] = {}
                        S["edit_msg"] = "棋盘已清空，请先摆上双方将帅。"
                    elif key == "name":
                        open_naming("edit")
                    elif key == "save":
                        okp, whyp = validate_position(S["board"])
                        if not okp:                    # 不符合要求：先拦下，不问名字
                            S["edit_msg"] = "不符合摆棋要求（%s），未存盘。" % whyp
                            S["message"] = S["edit_msg"]
                            beep("illegal")
                        elif not (S["custom_name"] or "").strip():
                            open_naming("save")        # 先让用户输入存盘名称
                        else:
                            save_current()
                    elif key == "load":
                        S["entries"] = load_library()
                        S["lib_open"] = True
                        S["lib_off"] = max(0, min(library_max_off(len(S["entries"])),
                                                  int(S.get("lib_off", 0))))
                    elif key == "done":
                        finish_edit()
                    elif key == "cancel":
                        leave_edit(True)
                        S["message"] = "已取消摆棋，恢复原局面。"
                    acted = True
                    break
                if acted:
                    continue

                target = pixel_to_board(*pos)
                if target:
                    if S["edit_piece"] == "erase":
                        S["board"].pop(target, None)
                        beep("move")
                    else:
                        ok, msg = placement_check(S["board"], S["edit_piece"], target)
                        S["edit_msg"] = msg
                        S["message"] = msg
                        if not ok:
                            beep("illegal")
                            continue
                        S["board"][target] = S["edit_piece"]
                        beep("move")
                continue

            # 底部按钮栏：悔棋 / 复盘 / 提示 / 存局 / 音乐 / 认输 / 提和 / 棋谱 / 重开
            if event.button == 1:
                handled = False
                for rect, key in bottom_button_rects():
                    if not rect.collidepoint(pos):
                        continue
                    if key == "undo":
                        undo()
                    elif key == "replay":
                        enter_replay()
                    elif key == "hint":
                        give_hint()
                    elif key == "save":
                        save_from_battle()
                    elif key == "music":
                        toggle_bgm()
                    elif key == "surrender":
                        if S["over"]:
                            S["message"] = "对局已结束。"
                            beep("illegal")
                        elif S["surrender_pending"]:
                            S["surrender_pending"] = False
                            S["over"] = True
                            S["turn"] = None
                            S["message"] = "%s胜 —— %s认输。" % (
                                name_of(AI_SIDE), name_of(HUMAN_SIDE))
                            S["result"] = "%s胜 —— %s认输" % (
                                name_of(AI_SIDE), name_of(HUMAN_SIDE))
                            beep("lose")
                        else:
                            S["surrender_pending"] = True
                            S["message"] = "再点一次「认输」即判负；点别处可取消。"
                            beep("select")
                    elif key == "draw":
                        offer_draw()
                    elif key == "export":
                        ok, info = export_record(S)
                        S["message"] = ("棋谱已导出：%s" % info) if ok else info
                        beep("select" if ok else "illegal")
                    elif key == "restart":
                        reset_position(S["position"])
                    elif key == "home":
                        # 手机没有 Esc：底部「主页」按钮替代它，摆棋先收摊再回主页
                        if S["editing"]:
                            leave_edit(True)
                        esc_back_home()
                    handled = True
                    break
                if handled:
                    continue

            # 正常对局点击
            if event.button != 1 or S["over"] or S["turn"] != HUMAN_SIDE:
                continue
            target = pixel_to_board(*pos)
            if not target:
                S["selected"] = None
                continue
            r, c = target
            piece = piece_at(S["board"], r, c)

            if S["selected"] and S["selected"] != (r, c):
                sr, sc = S["selected"]
                all_moves = legal_moves(S["board"], S["turn"])
                if (sr, sc, r, c) in all_moves:
                    bad = banned_repeats(S["board"], S["turn"], S["rep_counts"], all_moves)
                    if (sr, sc, r, c) in bad:
                        S["message"] = ("不得重复走子：这一着会让同一局面第 %d 次出现，"
                                        "请换一着（绿点已把这步排除）。" % REPEAT_BLOCK)
                        S["hint"] = None
                        S["move_hints"] = hint_moves(S["board"], S["turn"],
                                                     S["rep_counts"], (sr, sc))
                        beep("illegal")
                        continue
                    perform_move(sr, sc, r, c, HUMAN_SIDE)
                    continue
                why = move_reason(S["board"], sr, sc, r, c)
                if why:                       # 落点不合法：说明原因，不落子
                    S["message"] = why
                    if piece and piece[0] == S["turn"]:
                        S["selected"] = (r, c)
                        S["move_hints"] = hint_moves(S["board"], S["turn"],
                                                     S["rep_counts"], (r, c))
                        beep("select")
                    else:
                        S["selected"] = None
                        S["move_hints"] = []
                        beep("illegal")
                    continue

            if piece and piece[0] == S["turn"]:
                S["selected"] = (r, c)
                S["move_hints"] = hint_moves(S["board"], S["turn"], S["rep_counts"], (r, c))
                S["hint"] = None
                S["surrender_pending"] = False
                # 按下就记下这枚棋子：拖动够 5px 就变成「拖着走」，直接松手即落子
                S["drag"] = {"fr": r, "fc": c, "piece": piece,
                             "pos": pos, "moved": False}
                beep("select")
            else:
                if S["selected"]:
                    beep("illegal")
                S["selected"] = None
                S["move_hints"] = []

        # ---- 复盘自动播放 ----
        if S["replay"] and S["replay_auto"]:
            total = len(S["history"])
            if S["replay_index"] >= total:
                S["replay_auto"] = False
            elif time.perf_counter() - S["replay_last"] >= 1.2:
                S["replay_index"] = min(total, S["replay_index"] + 1)
                S["replay_last"] = time.perf_counter()

        # ---- 提示：后台线程算，算完再标；主循环期间照常画界面，不会假死 ----
        hjob = S.get("hint_job")
        if hjob is not None:
            stale = (S["screen"] != "battle" or S["over"] or S["replay"]
                     or S["editing"] or S["turn"] != HUMAN_SIDE)
            if stale:
                cancel_hint()
            elif hjob.done:
                S["hint_job"] = None
                move = hjob.result
                if hjob.error is not None or not move:
                    S["message"] = "这一手没算出好着法，换个局面再试试。"
                    beep("illegal")
                else:
                    S["hint"] = move
                    S["selected"] = (move[0], move[1])
                    S["move_hints"] = []
                    text = move_notation(S["board"], move[0], move[1],
                                         move[2], move[3], HUMAN_SIDE)
                    S["message"] = "建议走：%s（棋盘上已用绿点标出落点）。" % text
                    beep("select")

        # ---- AI 走棋：后台线程算，主循环继续以 60 帧绘制（箭头、计时不停）----
        ai_turn = (S["screen"] == "battle" and not S["editing"] and not S["over"]
                   and not S["replay"] and not S["cpu_offer"]
                   and S["turn"] == AI_SIDE)
        if S.get("ai_job") is not None and not ai_turn:
            cancel_ai()                     # 局面被换掉 / 已终局：丢弃这次计算
        if ai_turn:
            job = S.get("ai_job")
            if job is None:
                ai_moves = legal_moves(S["board"], AI_SIDE)
                avoid = banned_repeats(S["board"], AI_SIDE, S["rep_counts"], ai_moves,
                                       ban_check_repeat=True)   # 电脑不主动长将
                job = AiJob(S["board"], AI_SIDE,
                            DIFFICULTY_DEPTH[S["difficulty"]], banned=avoid)
                S["ai_job"] = job
                job.start()
            elif job.done and time.perf_counter() - job.started >= AI_MIN_THINK:
                # 至少「想」这么久再落子：开局库是瞬回的，太快会看不清自己的走子动画
                S["ai_job"] = None
                move = job.result
                if job.error is not None:
                    S["message"] = "%s思考出错（%s），本局已重开。" % (ai_label(), job.error)
                    beep("illegal")
                    reset_position(S["position"])
                elif move is None:
                    S["over"] = True
                    S["turn"] = None
                    S["message"] = "%s胜 —— %s无子可动。" % (
                        name_of(HUMAN_SIDE), name_of(AI_SIDE))
                    S["result"] = S["message"]
                    mark_entry_done(HUMAN_SIDE)
                    beep("win")
                else:
                    # 落子前再验一遍：这一手会不会把自己走成长将判负（有别的着法就换）
                    guarded = avoid_self_long_check(S["board"], AI_SIDE, S["rep_counts"],
                                                    S["pos_log"], move)
                    if guarded is not None:
                        move = guarded
                    perform_move(move[0], move[1], move[2], move[3], AI_SIDE)
                    if not S["over"] and _last_depth >= 2:
                        S["message"] += "（%s算到第 %d 层）" % (ai_label(), _last_depth)
                    if not S["over"]:
                        maybe_cpu_offer()     # 电脑觉得和定了就主动开口

        # ---- 渲染 ----
        # 提和弹窗开着时冻结本手计时：用户在看说明、做决定，不该扣他的时间
        if S["cpu_offer"]:
            S["turn_start"] = time.perf_counter() - S["offer_elapsed"]
        bgm_tick()
        if S["screen"] == "home":
            try:
                home_hover = to_logical(pygame.mouse.get_pos())
            except (pygame.error, AttributeError):
                home_hover = None
            draw_home(screen, S["bgm"], hover=home_hover)
            if S["home_overlay"] == "settings":
                draw_settings_overlay(screen, S)
            elif S["home_overlay"] == "instructions":
                try:
                    hover = to_logical(pygame.mouse.get_pos())
                except (pygame.error, AttributeError):
                    hover = None
                draw_instructions_overlay(screen, S.get("help_page", 0), hover=hover)
            elif S["home_overlay"] == "import":
                draw_import_overlay(screen, S)
            present()
            fps.tick(60)
            continue
        hint_list = [S["hint"]] if S["hint"] else list(S["move_hints"])
        if S["editing"]:
            draw_edit_scene(screen, S["board"], S["edit_piece"], S["edit_msg"],
                            S["difficulty"], S["sound_on"], S["move_limit"],
                            music_on=S["bgm_on"])
        elif S["replay"]:
            total = len(S["history"])
            display_board = rebuild_board(S["replay_index"])
            last = None
            if S["replay_index"] > 0:
                h = S["history"][S["replay_index"] - 1]
                mover = RED if h["side"] == "红方" else BLACK
                last = (h["fr"], h["fc"], h["tr"], h["tc"], mover)
            draw_scene(screen, display_board, None, S["turn"], S["remain"],
                       S["turn_start"], S["counts"], S["message"], True,
                       S["difficulty"], S["sound_on"], last_move=last,
                       caption=(("复盘模式：第 %d / %d 手" if IS_ANDROID else
                                 "复盘模式：第 %d / %d 手（←/→ 步进，空格自动，Esc 退出）")
                                % (S["replay_index"], total)),
                       replay_info=(S["replay_index"], total, S["replay_auto"]),
                       music_on=S["bgm_on"], move_limit=S["move_limit"])
        else:
            draw_scene(screen, S["board"], S["selected"], S["turn"], S["remain"],
                       S["turn_start"], S["counts"], S["message"], S["over"],
                       S["difficulty"], S["sound_on"], last_move=S["last_move"],
                       hints=hint_list, result_text=S["result"],
                       music_on=S["bgm_on"], move_limit=S["move_limit"],
                       anim=S["anim"], drag=S["drag"], ripple=S["ripple"])
        if S["lib_open"]:
            draw_library_overlay(screen, S["entries"], S["edit_msg"], S.get("lib_off", 0),
                                 category=S["lib_category"],
                                 del_pending=S["lib_del_pending"],
                                 query=S["lib_query"], search_focus=S["lib_focus"],
                                 caret_on=(pygame.time.get_ticks() // 500) % 2 == 0,
                                 io_msg=S.get("edit_msg", ""),
                                 pieces=S.get("lib_pieces", "全部"),
                                 level=S.get("lib_level", "全部"))
        if S["cpu_offer"]:
            draw_draw_offer_overlay(screen, S["cpu_offer"])
        if S["naming"]:
            mode = S.get("naming_mode", "save")
            draw_naming_overlay(screen, S["name_buf"],
                                (pygame.time.get_ticks() // 500) % 2 == 0,
                                mode=mode,
                                turn=S.get("rename_turn", RED),
                                detail=rename_detail(S.get("rename_idx")))
        present()
        fps.tick(60)

    finish_app()
    pygame.quit()
    sys.exit()


def run_guard():
    """正式入口：万一崩溃，把错误写进 崩溃日志.txt，并弹窗告诉用户日志在哪，
    而不是窗口一闪就没了、什么线索都没有。"""
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        log_path = os.path.join(_BASE_DIR, "崩溃日志.txt")
        try:
            with open(log_path, "a", encoding="utf-8") as fp:
                fp.write("=" * 54 + "\n")
                fp.write("%s  版本 v%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), VERSION))
                fp.write(traceback.format_exc() + "\n")
        except OSError:
            log_path = "（日志写入失败）"
        try:
            pygame.quit()
        except Exception:
            pass
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showerror(
                "中国象棋",
                "程序遇到意外错误，已记录到：\n%s\n\n把这份日志发给我就能定位问题。" % log_path)
            root.destroy()
        except Exception:
            pass
        raise


if __name__ == "__main__":
    run_guard()
