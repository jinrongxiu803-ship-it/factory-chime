#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공장용 차임벨 프로그램 (Factory Chime) - 한국어/베트남어 공용
Chuông báo nhà máy - Song ngữ Hàn/Việt
"""

import os
import sys
import json
import threading
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# 스트레칭 안내 모듈 (같은 폴더의 stretching.py)
try:
    import stretching
except Exception as _e:
    stretching = None
    print("stretching 모듈 로드 실패:", _e)

# ---------------- 다국어 텍스트 ----------------
TEXTS = {
    "ko": {
        "title": "공장 차임벨",
        "lang_label": "언어 / Ngôn ngữ",
        "enabled": "차임 활성화",
        "sound_frame": "차임 소리 (.wav, 비우면 내장 학교 벨소리)",
        "browse": "찾기",
        "test": "테스트",
        "tab_weekday": "요일별 설정",
        "tab_date": "특정 날짜 설정",
        "select_weekday": "요일 선택:",
        "time_format_hint": "형식 HH:MM (24시간). 토요일은 토요일 항목에서 따로 설정.",
        "add": "추가",
        "delete": "삭제",
        "date_label": "날짜 (YYYY-MM-DD):",
        "load": "불러오기",
        "add_time": "시간 추가",
        "del_time": "시간 삭제",
        "set_holiday": "이 날짜 휴무로 저장 (시간 0개)",
        "date_priority_hint": "특정 날짜 설정은 해당 요일 설정보다 우선합니다.",
        "save": "설정 저장",
        "waiting": "대기 중",
        "saved": "저장 완료 ✓",
        "err": "오류",
        "err_time": "HH:MM 형식으로 입력하세요. 예: 08:30",
        "err_date": "YYYY-MM-DD 형식으로 입력하세요.",
        "done": "완료",
        "holiday_done": "은(는) 휴무(차임 없음)로 설정되었습니다.",
        "weekdays": ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"],
        "weekdays_short": ["월", "화", "수", "목", "금", "토", "일"],
        "stretch_frame": "스트레칭 안내 (베트남어 음성)",
        "stretch_enabled": "스트레칭 안내 사용",
        "stretch_time_label": "스트레칭 시간:",
        "stretch_test": "지금 테스트",
        "stretch_hint": "추가한 시간마다 차분한 여성 베트남어 음성+음악으로 약 6~7분 스트레칭 안내.",
    },
    "vi": {
        "title": "Chuông báo nhà máy",
        "lang_label": "Ngôn ngữ / 언어",
        "enabled": "Bật chuông",
        "sound_frame": "Âm chuông (.wav, để trống = chuông trường có sẵn)",
        "browse": "Chọn",
        "test": "Thử",
        "tab_weekday": "Cài theo thứ",
        "tab_date": "Cài theo ngày",
        "select_weekday": "Chọn thứ:",
        "time_format_hint": "Định dạng HH:MM (24 giờ). Thứ Bảy cài riêng ở mục Thứ Bảy.",
        "add": "Thêm",
        "delete": "Xóa",
        "date_label": "Ngày (YYYY-MM-DD):",
        "load": "Tải",
        "add_time": "Thêm giờ",
        "del_time": "Xóa giờ",
        "set_holiday": "Lưu ngày này là ngày nghỉ (0 giờ)",
        "date_priority_hint": "Cài đặt theo ngày ưu tiên hơn cài đặt theo thứ.",
        "save": "Lưu cài đặt",
        "waiting": "Đang chờ",
        "saved": "Đã lưu ✓",
        "err": "Lỗi",
        "err_time": "Nhập theo định dạng HH:MM. Ví dụ: 08:30",
        "err_date": "Nhập theo định dạng YYYY-MM-DD.",
        "done": "Hoàn tất",
        "holiday_done": "đã được đặt là ngày nghỉ (không có chuông).",
        "weekdays": ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"],
        "weekdays_short": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
        "stretch_frame": "Hướng dẫn giãn cơ (giọng tiếng Việt)",
        "stretch_enabled": "Bật hướng dẫn giãn cơ",
        "stretch_time_label": "Giờ giãn cơ:",
        "stretch_test": "Thử ngay",
        "stretch_hint": "Mỗi giờ đã thêm sẽ hướng dẫn giãn cơ ~6-7 phút bằng giọng nữ nhẹ nhàng + nhạc.",
    },
}

def _base_dirs():
    """리소스를 찾을 폴더 목록 (exe 옆 → 번들 내부)."""
    dirs = []
    if getattr(sys, "frozen", False):
        dirs.append(os.path.dirname(sys.executable))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(meipass)
    else:
        dirs.append(os.path.dirname(os.path.abspath(__file__)))
    return dirs


def _find_resource(name):
    for d in _base_dirs():
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return os.path.join(_base_dirs()[0], name)


# 설정 파일은 항상 exe(또는 스크립트) 옆에 저장 → 사용자 설정 유지
APP_DIR = _base_dirs()[0]
DEFAULT_SOUND = _find_resource("school_bell.wav")
# 주요 종(시업·퇴근 등 특정 시각)에 쓰는 특별 벨소리
SPECIAL_SOUND = _find_resource("singapore_bell.wav")


def _resolve_sound(path):
    """사용자가 지정한 소리가 있으면 그것, 없으면 내장 학교 벨소리."""
    if path and os.path.exists(path):
        return path
    if os.path.exists(DEFAULT_SOUND):
        return DEFAULT_SOUND
    return None


def _play_sound(path):
    snd = _resolve_sound(path)
    try:
        if sys.platform.startswith("win"):
            import winsound
            if snd:
                # SND_ASYNC 로 비동기 재생, wav 전체(2초) 끝까지 재생됨
                winsound.PlaySound(snd, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                # 최후의 대체: 시끄러운 비프 연타
                for _ in range(8):
                    winsound.Beep(880, 110)
                    winsound.Beep(1320, 110)
        else:
            if snd:
                if sys.platform == "darwin":
                    os.system('afplay "%s" &' % snd)
                else:
                    os.system('aplay "%s" 2>/dev/null &' % snd)
            else:
                print("\a")
    except Exception as e:
        print("sound error:", e)
def _config_dir():
    """설정 저장 폴더 — 쓰기 권한 안전한 사용자 폴더(APPDATA).
    exe 를 Program Files 등 권한 폴더에 둬도 설정이 저장되도록."""
    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "FactoryChime")
    else:
        d = os.path.join(os.path.expanduser("~"), ".factorychime")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        d = APP_DIR  # 폴백: exe 옆
    return d


CONFIG_PATH = os.path.join(_config_dir(), "chime_config.json")

def default_config():
    return {
        "language": "ko",
        "enabled": True,
        "sound_file": "",
        "weekday_schedules": {
            # 월~금: 공통 + 18:00
            "0": ["07:25", "07:30", "12:00", "12:55", "13:00", "18:00"],
            "1": ["07:25", "07:30", "12:00", "12:55", "13:00", "18:00"],
            "2": ["07:25", "07:30", "12:00", "12:55", "13:00", "18:00"],
            "3": ["07:25", "07:30", "12:00", "12:55", "13:00", "18:00"],
            "4": ["07:25", "07:30", "12:00", "12:55", "13:00", "18:00"],
            # 토: 공통 + 17:00
            "5": ["07:25", "07:30", "12:00", "12:55", "13:00", "17:00"],
            # 일: 휴무
            "6": [],
        },
        "date_overrides": {},
        # 이 시각들엔 특별 벨소리(singapore_bell.wav)를 울림 — 시업·퇴근 등 주요 종
        # 나머지 시각은 일반 벨(sound_file 또는 내장 3초 벨)
        "special_times": ["07:30", "17:00", "18:00"],
        # 스트레칭 안내 / Hướng dẫn giãn cơ
        "stretch_enabled": True,
        "stretch_times": ["14:15"],  # 여러 개 설정 가능 / Có thể đặt nhiều giờ
        # 스트레칭을 실행할 요일 (0=월 ~ 6=일) / Các thứ chạy giãn cơ
        "stretch_weekdays": [0, 1, 2, 3, 4, 5],
    }

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            base = default_config()
            base.update(cfg)
            # 구버전 호환: stretch_time(단수) → stretch_times(복수)
            if "stretch_time" in cfg and not cfg.get("stretch_times"):
                base["stretch_times"] = [cfg["stretch_time"]]
            base.pop("stretch_time", None)
            if not base.get("stretch_times"):
                base["stretch_times"] = ["14:15"]
            return base
        except Exception:
            return default_config()
    return default_config()

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

class ChimeEngine:
    def __init__(self, get_config, on_stretch=None):
        self.get_config = get_config
        self.on_stretch = on_stretch
        self._stop = threading.Event()
        self._last_fired = None
        self._last_stretch = None
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()

    def today_schedule(self, cfg, now):
        date_key = now.strftime("%Y-%m-%d")
        if date_key in cfg.get("date_overrides", {}):
            return cfg["date_overrides"][date_key]
        wd = str(now.weekday())
        return cfg.get("weekday_schedules", {}).get(wd, [])

    def _run(self):
        while not self._stop.is_set():
            cfg = self.get_config()
            now = datetime.datetime.now()
            cur = now.strftime("%H:%M")
            tag = now.strftime("%Y-%m-%d %H:%M")
            # 일반 차임
            if cfg.get("enabled", True) and tag != self._last_fired:
                if cur in self.today_schedule(cfg, now):
                    self._last_fired = tag
                    if cur in cfg.get("special_times", []):
                        _play_sound(SPECIAL_SOUND)            # 시업·퇴근 주요 종(싱가포르 벨)
                    else:
                        _play_sound(cfg.get("sound_file", ""))  # 일반 벨(내장 3초 벨)
            # 스트레칭 안내 (여러 시간 중 하나와 일치 시)
            if (cfg.get("stretch_enabled", True) and tag != self._last_stretch
                    and cur in cfg.get("stretch_times", ["14:15"])
                    and now.weekday() in cfg.get("stretch_weekdays", [0,1,2,3,4,5])):
                self._last_stretch = tag
                if self.on_stretch:
                    self.on_stretch()
            sleep_for = 60 - now.second
            self._stop.wait(min(sleep_for, 5))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # PC 절전/잠자기 방지 (잠들면 그 시각 벨을 놓침) — Windows
        if os.name == "nt":
            try:
                import ctypes
                # ES_CONTINUOUS(0x80000000) | ES_SYSTEM_REQUIRED(0x1)
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
            except Exception:
                pass
        self.cfg = load_config()
        self.lang = self.cfg.get("language", "ko")
        self._lock = threading.Lock()
        self.geometry("580x640")
        self.engine = ChimeEngine(self.get_config, on_stretch=self._trigger_stretch)
        self.engine.start()
        self._build_ui()
        self._apply_language()
        self._refresh_clock()

    def _trigger_stretch(self):
        """엔진(다른 스레드)에서 호출 → 메인스레드에서 스트레칭 창 띄움."""
        if stretching is None:
            return
        self.after(0, lambda: stretching.start_stretching(self))

    def t(self, key):
        return TEXTS[self.lang][key]

    def get_config(self):
        with self._lock:
            return json.loads(json.dumps(self.cfg))

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}
        langbar = ttk.Frame(self)
        langbar.pack(fill="x", **pad)
        self.lbl_lang = ttk.Label(langbar)
        self.lbl_lang.pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang)
        ttk.Radiobutton(langbar, text="한국어", value="ko",
                        variable=self.lang_var, command=self._change_lang).pack(side="left", padx=4)
        ttk.Radiobutton(langbar, text="Tiếng Việt", value="vi",
                        variable=self.lang_var, command=self._change_lang).pack(side="left", padx=4)

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        self.clock_var = tk.StringVar()
        ttk.Label(top, textvariable=self.clock_var, font=("Consolas", 18)).pack(side="left")
        self.enabled_var = tk.BooleanVar(value=self.cfg["enabled"])
        self.chk_enabled = ttk.Checkbutton(top, variable=self.enabled_var, command=self._toggle_enabled)
        self.chk_enabled.pack(side="right")

        self.sf = ttk.LabelFrame(self)
        self.sf.pack(fill="x", **pad)
        self.sound_var = tk.StringVar(value=self.cfg["sound_file"])
        ttk.Entry(self.sf, textvariable=self.sound_var).pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.btn_browse = ttk.Button(self.sf, command=self._pick_sound)
        self.btn_browse.pack(side="left", padx=4)
        self.btn_test = ttk.Button(self.sf, command=lambda: _play_sound(self.sound_var.get()))
        self.btn_test.pack(side="left", padx=4)

        # 스트레칭 설정 프레임 (여러 시간 설정 가능)
        self.stf = ttk.LabelFrame(self)
        self.stf.pack(fill="x", **pad)
        self.stretch_enabled_var = tk.BooleanVar(value=self.cfg.get("stretch_enabled", True))
        self.chk_stretch = ttk.Checkbutton(self.stf, variable=self.stretch_enabled_var,
                                           command=self._toggle_stretch)
        self.chk_stretch.grid(row=0, column=0, columnspan=4, sticky="w", padx=6, pady=6)

        self.lbl_stretch_time = ttk.Label(self.stf)
        self.lbl_stretch_time.grid(row=1, column=0, sticky="w", padx=6)
        self.stretch_time_var = tk.StringVar(value="14:15")
        ttk.Entry(self.stf, textvariable=self.stretch_time_var, width=8).grid(row=1, column=1, padx=4, sticky="w")
        self.btn_stretch_add = ttk.Button(self.stf, command=self._stretch_add, width=8)
        self.btn_stretch_add.grid(row=1, column=2, padx=2)
        self.btn_stretch_del = ttk.Button(self.stf, command=self._stretch_del, width=8)
        self.btn_stretch_del.grid(row=1, column=3, padx=2)
        self.btn_stretch_test = ttk.Button(self.stf, command=self._trigger_stretch)
        self.btn_stretch_test.grid(row=1, column=4, padx=6)

        # 설정된 스트레칭 시간 목록
        self.stretch_list = tk.Listbox(self.stf, height=3)
        self.stretch_list.grid(row=2, column=0, columnspan=5, sticky="we", padx=6, pady=4)
        self.stf.grid_columnconfigure(4, weight=1)
        self._reload_stretch_times()

        self.lbl_stretch_hint = ttk.Label(self.stf, foreground="gray")
        self.lbl_stretch_hint.grid(row=3, column=0, columnspan=5, sticky="w", padx=6, pady=(0, 6))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, **pad)

        self.wf = ttk.Frame(self.nb)
        self.nb.add(self.wf, text="")
        self.lbl_select_wd = ttk.Label(self.wf)
        self.lbl_select_wd.grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.wd_combo = ttk.Combobox(self.wf, state="readonly")
        self.wd_combo.grid(row=0, column=1, sticky="w", padx=6)
        self.wd_combo.bind("<<ComboboxSelected>>", lambda e: self._load_weekday(self.wd_combo.current()))
        self.wd_var = tk.IntVar(value=0)

        self.wd_list = tk.Listbox(self.wf, height=12)
        self.wd_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        self.wf.grid_rowconfigure(1, weight=1)
        self.wf.grid_columnconfigure(1, weight=1)

        self.wd_time = ttk.Entry(self.wf, width=10)
        self.wd_time.insert(0, "08:00")
        self.wd_time.grid(row=2, column=0, sticky="w", padx=6, pady=4)
        bw = ttk.Frame(self.wf); bw.grid(row=2, column=1, sticky="e", padx=6)
        self.btn_wd_add = ttk.Button(bw, command=self._wd_add); self.btn_wd_add.pack(side="left", padx=2)
        self.btn_wd_del = ttk.Button(bw, command=self._wd_del); self.btn_wd_del.pack(side="left", padx=2)
        self.lbl_wd_hint = ttk.Label(self.wf, foreground="gray")
        self.lbl_wd_hint.grid(row=3, column=0, columnspan=2, sticky="w", padx=6)

        self.df = ttk.Frame(self.nb)
        self.nb.add(self.df, text="")
        self.lbl_date = ttk.Label(self.df)
        self.lbl_date.grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.date_entry = ttk.Entry(self.df, width=14)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, sticky="w", padx=6)
        self.btn_load = ttk.Button(self.df, command=self._load_date)
        self.btn_load.grid(row=0, column=2, padx=4)

        self.date_list = tk.Listbox(self.df, height=10)
        self.date_list.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=6, pady=6)
        self.df.grid_rowconfigure(1, weight=1)
        self.df.grid_columnconfigure(1, weight=1)

        self.date_time = ttk.Entry(self.df, width=10)
        self.date_time.insert(0, "08:00")
        self.date_time.grid(row=2, column=0, sticky="w", padx=6, pady=4)
        bd = ttk.Frame(self.df); bd.grid(row=2, column=1, columnspan=2, sticky="e", padx=6)
        self.btn_date_add = ttk.Button(bd, command=self._date_add); self.btn_date_add.pack(side="left", padx=2)
        self.btn_date_del = ttk.Button(bd, command=self._date_del); self.btn_date_del.pack(side="left", padx=2)
        self.btn_holiday = ttk.Button(self.df, command=self._date_holiday)
        self.btn_holiday.grid(row=3, column=0, columnspan=3, sticky="w", padx=6, pady=4)
        self.lbl_date_hint = ttk.Label(self.df, foreground="gray")
        self.lbl_date_hint.grid(row=4, column=0, columnspan=3, sticky="w", padx=6)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", **pad)
        self.btn_save = ttk.Button(bottom, command=self._save_all)
        self.btn_save.pack(side="right", padx=4)
        self.status_var = tk.StringVar()
        ttk.Label(bottom, textvariable=self.status_var, foreground="green").pack(side="left", padx=4)

    def _change_lang(self):
        self.lang = self.lang_var.get()
        with self._lock:
            self.cfg["language"] = self.lang
        self._apply_language()
        self._autosave()

    def _apply_language(self):
        self.title(self.t("title"))
        self.lbl_lang.config(text=self.t("lang_label"))
        self.chk_enabled.config(text=self.t("enabled"))
        self.sf.config(text=self.t("sound_frame"))
        self.btn_browse.config(text=self.t("browse"))
        self.btn_test.config(text=self.t("test"))
        self.nb.tab(0, text=self.t("tab_weekday"))
        self.nb.tab(1, text=self.t("tab_date"))
        self.lbl_select_wd.config(text=self.t("select_weekday"))
        self.lbl_wd_hint.config(text=self.t("time_format_hint"))
        self.btn_wd_add.config(text=self.t("add"))
        self.btn_wd_del.config(text=self.t("delete"))
        self.lbl_date.config(text=self.t("date_label"))
        self.btn_load.config(text=self.t("load"))
        self.btn_date_add.config(text=self.t("add_time"))
        self.btn_date_del.config(text=self.t("del_time"))
        self.btn_holiday.config(text=self.t("set_holiday"))
        self.lbl_date_hint.config(text=self.t("date_priority_hint"))
        self.btn_save.config(text=self.t("save"))
        self.status_var.set(self.t("waiting"))
        self.stf.config(text=self.t("stretch_frame"))
        self.chk_stretch.config(text=self.t("stretch_enabled"))
        self.lbl_stretch_time.config(text=self.t("stretch_time_label"))
        self.btn_stretch_add.config(text=self.t("add"))
        self.btn_stretch_del.config(text=self.t("delete"))
        self.btn_stretch_test.config(text=self.t("stretch_test"))
        self.lbl_stretch_hint.config(text=self.t("stretch_hint"))
        cur = self.wd_combo.current()
        if cur < 0:
            cur = 0
        self.wd_combo.config(values=["%d - %s" % (i, self.t('weekdays')[i]) for i in range(7)])
        self.wd_combo.current(cur)
        self._load_weekday(cur)

    def _refresh_clock(self):
        now = datetime.datetime.now()
        wd = self.t("weekdays_short")[now.weekday()]
        self.clock_var.set(now.strftime("%Y-%m-%d (" + wd + ") %H:%M:%S"))
        self.after(1000, self._refresh_clock)

    def _toggle_enabled(self):
        with self._lock:
            self.cfg["enabled"] = self.enabled_var.get()
        self._autosave()

    def _toggle_stretch(self):
        with self._lock:
            self.cfg["stretch_enabled"] = self.stretch_enabled_var.get()
        self._autosave()

    def _reload_stretch_times(self):
        self.stretch_list.delete(0, tk.END)
        for tt in sorted(self.cfg.get("stretch_times", [])):
            self.stretch_list.insert(tk.END, tt)

    def _stretch_add(self):
        tt = self.stretch_time_var.get().strip()
        try:
            datetime.datetime.strptime(tt, "%H:%M")
        except ValueError:
            messagebox.showerror(self.t("err"), self.t("err_time"))
            return
        times = set(self.cfg.get("stretch_times", []))
        times.add(tt)
        self.cfg["stretch_times"] = sorted(times)
        self._reload_stretch_times()
        self._autosave()

    def _stretch_del(self):
        sel = self.stretch_list.curselection()
        if not sel:
            return
        tt = self.stretch_list.get(sel[0])
        self.cfg["stretch_times"] = [x for x in self.cfg.get("stretch_times", []) if x != tt]
        self._reload_stretch_times()
        self._autosave()

    def _pick_sound(self):
        p = filedialog.askopenfilename(filetypes=[("WAV", "*.wav"), ("All", "*.*")])
        if p:
            self.sound_var.set(p)
            self._autosave()

    def _valid_time(self, s):
        try:
            datetime.datetime.strptime(s, "%H:%M")
            return True
        except ValueError:
            return False

    def _load_weekday(self, wd):
        if wd is None or wd < 0:
            wd = 0
        self.wd_var.set(wd)
        self.wd_list.delete(0, tk.END)
        for tt in sorted(self.cfg["weekday_schedules"].get(str(wd), [])):
            self.wd_list.insert(tk.END, tt)

    def _wd_add(self):
        tt = self.wd_time.get().strip()
        if not self._valid_time(tt):
            messagebox.showerror(self.t("err"), self.t("err_time"))
            return
        wd = str(self.wd_var.get())
        lst = set(self.cfg["weekday_schedules"].get(wd, []))
        lst.add(tt)
        self.cfg["weekday_schedules"][wd] = sorted(lst)
        self._load_weekday(self.wd_var.get())
        self._autosave()

    def _wd_del(self):
        sel = self.wd_list.curselection()
        if not sel:
            return
        tt = self.wd_list.get(sel[0])
        wd = str(self.wd_var.get())
        self.cfg["weekday_schedules"][wd] = [x for x in self.cfg["weekday_schedules"].get(wd, []) if x != tt]
        self._load_weekday(self.wd_var.get())
        self._autosave()

    def _load_date(self):
        d = self.date_entry.get().strip()
        try:
            datetime.datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(self.t("err"), self.t("err_date"))
            return
        self.date_list.delete(0, tk.END)
        for tt in sorted(self.cfg["date_overrides"].get(d, [])):
            self.date_list.insert(tk.END, tt)

    def _date_add(self):
        d = self.date_entry.get().strip()
        tt = self.date_time.get().strip()
        try:
            datetime.datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(self.t("err"), self.t("err_date"))
            return
        if not self._valid_time(tt):
            messagebox.showerror(self.t("err"), self.t("err_time"))
            return
        lst = set(self.cfg["date_overrides"].get(d, []))
        lst.add(tt)
        self.cfg["date_overrides"][d] = sorted(lst)
        self._load_date()
        self._autosave()

    def _date_del(self):
        sel = self.date_list.curselection()
        if not sel:
            return
        d = self.date_entry.get().strip()
        tt = self.date_list.get(sel[0])
        self.cfg["date_overrides"][d] = [x for x in self.cfg["date_overrides"].get(d, []) if x != tt]
        self._load_date()
        self._autosave()

    def _date_holiday(self):
        d = self.date_entry.get().strip()
        try:
            datetime.datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(self.t("err"), self.t("err_date"))
            return
        self.cfg["date_overrides"][d] = []
        self._load_date()
        self._autosave()
        messagebox.showinfo(self.t("done"), "%s %s" % (d, self.t('holiday_done')))

    def _autosave(self):
        """변경 즉시 자동 저장 (저장 버튼을 안 눌러도 설정 유지)."""
        try:
            self.cfg["enabled"] = self.enabled_var.get()
            self.cfg["sound_file"] = self.sound_var.get().strip()
            self.cfg["language"] = self.lang
            self.cfg["stretch_enabled"] = self.stretch_enabled_var.get()
            # weekday_schedules / date_overrides / stretch_times 는
            # 추가·삭제 시 이미 self.cfg 에 반영돼 있음
            save_config(self.cfg)
        except Exception:
            pass

    def _save_all(self):
        self._autosave()
        self.status_var.set(self.t("saved"))
        self.after(2000, lambda: self.status_var.set(self.t("waiting")))

    # ---------------- 트레이 상주 / 창 숨김 ----------------
    def hide_to_tray(self):
        """창을 닫아도 종료하지 않고 트레이로 숨김."""
        self.withdraw()

    def show_window(self):
        """트레이에서 창 다시 표시."""
        self.after(0, lambda: (self.deiconify(), self.lift(), self.focus_force()))

    def quit_app(self):
        try:
            self.engine.stop()
        except Exception:
            pass
        try:
            if getattr(self, "_tray", None):
                self._tray.stop()
        except Exception:
            pass
        self.after(0, self.destroy)

    def setup_tray(self):
        """시스템 트레이 아이콘 설정 (pystray). 없으면 조용히 패스."""
        try:
            import pystray
            from PIL import Image, ImageDraw
        except Exception as e:
            print("pystray/Pillow 없음 - 트레이 비활성화:", e)
            return False

        # 간단한 종 모양 아이콘 생성
        img = Image.new("RGB", (64, 64), "#0f2540")
        d = ImageDraw.Draw(img)
        d.ellipse((16, 12, 48, 40), fill="#ffd24a")
        d.rectangle((28, 8, 36, 16), fill="#ffd24a")
        d.rectangle((20, 40, 44, 46), fill="#ffd24a")
        d.ellipse((28, 46, 36, 54), fill="#ffd24a")

        menu = pystray.Menu(
            pystray.MenuItem("열기 / Mở cài đặt", lambda: self.show_window(), default=True),
            pystray.MenuItem("스트레칭 테스트 / Thử giãn cơ", lambda: self._trigger_stretch()),
            pystray.MenuItem("종료 / Thoát", lambda: self.quit_app()),
        )
        self._tray = pystray.Icon("FactoryChime", img, "공장 차임벨 / Chuông nhà máy", menu)
        threading.Thread(target=self._tray.run, daemon=True).start()
        return True

def _app_exe_path():
    """실행 파일 경로 — PyInstaller exe면 exe 자신, 아니면 스크립트."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(__file__)


def _register_autostart():
    """부팅 시 백그라운드 자동시작 등록 (HKCU Run, 멱등). Windows 전용."""
    if os.name != "nt":
        return
    import winreg
    exe = _app_exe_path()
    cmd = f'"{exe}"' if getattr(sys, "frozen", False) else f'"{sys.executable}" "{exe}"'
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run")
    try:
        winreg.SetValueEx(key, "FactoryChime", 0, winreg.REG_SZ, cmd)
    finally:
        winreg.CloseKey(key)


def _ensure_desktop_shortcut():
    """바탕화면에 '공장 차임벨 설정' 바로가기(--show) 생성 (없으면). Windows 전용."""
    if os.name != "nt":
        return
    import tempfile, subprocess
    exe = _app_exe_path()
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(desktop):
        return
    lnk = os.path.join(desktop, "공장 차임벨 설정.lnk")
    if os.path.exists(lnk):
        return
    if getattr(sys, "frozen", False):
        target, args = exe, "--show"
    else:
        target, args = sys.executable, f'"{exe}" --show'
    workdir = os.path.dirname(exe)
    ps = (
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}')\n"
        f"$s.TargetPath='{target}'\n"
        f"$s.Arguments='{args}'\n"
        f"$s.WorkingDirectory='{workdir}'\n"
        f"$s.Description='공장 차임벨 설정'\n"
        f"$s.Save()\n"
    )
    ps1 = os.path.join(tempfile.gettempdir(), "_factorychime_lnk.ps1")
    with open(ps1, "w", encoding="utf-8-sig") as f:  # BOM → powershell 한글 인식
        f.write(ps)
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", ps1], creationflags=0x08000000)  # CREATE_NO_WINDOW
    except Exception as e:
        print("바탕화면 바로가기 생성 경고:", e)


if __name__ == "__main__":
    # 실행 인자:
    #   (없음)   → 백그라운드 모드: 창 숨기고 트레이 상주 (자동 시작용)
    #   --show   → 설정 창을 띄운 채 시작 (사람이 직접 켤 때)
    import tempfile
    show = ("--show" in sys.argv) or ("-s" in sys.argv)
    _signal = os.path.join(tempfile.gettempdir(), "factorychime_show.flag")

    # ---- 중복 실행 방지 (Windows) ----
    # 이미 백그라운드로 떠 있으면, "설정창 열기" 신호만 남기고 종료한다.
    # (= 바탕화면 설정 아이콘을 더블클릭하면 떠 있던 본체의 설정창이 열림)
    _primary = True
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\FactoryChime_Mutex")
            if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                _primary = False
        except Exception:
            pass

    if not _primary:
        try:
            with open(_signal, "w") as f:
                f.write("show")
        except Exception:
            pass
        sys.exit(0)

    # ---- 첫(주) 인스턴스: 자동시작 + 바탕화면 설정 아이콘 등록 (멱등) ----
    if os.name == "nt":
        try:
            _register_autostart()
            _ensure_desktop_shortcut()
        except Exception as e:
            print("자동시작/바로가기 등록 경고:", e)

    app = App()
    tray_ok = app.setup_tray()

    # ---- 설정창 열기 신호 폴링 (바탕화면 아이콘 더블클릭 시) ----
    def _poll_show_signal():
        try:
            if os.path.exists(_signal):
                os.remove(_signal)
                app.show_window()
        except Exception:
            pass
        app.after(1000, _poll_show_signal)
    app.after(1000, _poll_show_signal)

    if tray_ok:
        # 트레이 있음: X 누르면 종료 대신 트레이로 숨김
        app.protocol("WM_DELETE_WINDOW", app.hide_to_tray)
        if not show:
            # 백그라운드 시작: 창 숨김 (트레이 아이콘으로만 존재)
            app.after(200, app.hide_to_tray)
    else:
        # 트레이 없음(pystray 미설치): 창을 띄워두고 X 누르면 종료
        app.protocol("WM_DELETE_WINDOW", app.quit_app)

    app.mainloop()
