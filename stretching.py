#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스트레칭 안내 모듈 (베트남어 나레이션)
Hướng dẫn giãn cơ - Lời dẫn tiếng Việt

- 14:15 자동 실행 / Tự động chạy lúc 14:15
- 베트남어 음성 안내 (Windows TTS) / Giọng nói tiếng Việt
- 긴장 완화 배경음악 / Nhạc thư giãn
- 화면 단계별 안내 (베/한 병기) / Hiển thị từng bước (Việt/Hàn)
약 3~4분 / Khoảng 3-4 phút
"""

import os
import sys
import time
import threading
import tkinter as tk


def _base_dirs():
    """리소스를 찾을 폴더 목록.
    1) exe/스크립트가 있는 실제 폴더 (사용자가 나중에 voices 생성 가능)
    2) PyInstaller 번들 임시폴더 (_MEIPASS) - exe에 포함된 파일
    """
    dirs = []
    if getattr(sys, "frozen", False):
        # PyInstaller exe 로 실행 중: exe 가 있는 폴더
        dirs.append(os.path.dirname(sys.executable))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(meipass)
    else:
        dirs.append(os.path.dirname(os.path.abspath(__file__)))
    return dirs


def _find_resource(name):
    """여러 후보 폴더에서 파일/폴더를 찾아 첫 번째 존재하는 경로 반환."""
    for d in _base_dirs():
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    # 못 찾으면 첫 번째 후보 경로 반환(존재하지 않더라도)
    return os.path.join(_base_dirs()[0], name)


APP_DIR = _base_dirs()[0]
RELAX_MUSIC = _find_resource("relax_music.wav")
VOICE_DIR = _find_resource("voices")  # 고음질 mp3 폴더 (exe 옆 우선, 없으면 번들 내부)


def _voice_file(idx):
    """단계 번호(1~)에 해당하는 고음질 음성 파일 경로. 없으면 None."""
    p = os.path.join(VOICE_DIR, "step_%02d.mp3" % idx)
    return p if os.path.exists(p) else None


def _play_audio_blocking(path):
    """오디오 파일을 끝까지 재생(블로킹). mp3/wav 지원."""
    try:
        if sys.platform.startswith("win"):
            # Windows: pygame 우선(mp3 지원), 없으면 winsound(wav만)
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                return True
            except Exception:
                if path.lower().endswith(".wav"):
                    import winsound
                    winsound.PlaySound(path, winsound.SND_FILENAME)  # 동기 재생
                    return True
                # mp3인데 pygame 없으면 기본 플레이어로
                os.startfile(path)
                time.sleep(1)
                return True
        elif sys.platform == "darwin":
            os.system('afplay "%s"' % path)
            return True
        else:
            os.system('ffplay -nodisp -autoexit "%s" 2>/dev/null' % path)
            return True
    except Exception as e:
        print("audio play error:", e)
        return False

# ----------------------------------------------------------------------
# 스트레칭 단계 데이터
# vi: 베트남어 음성으로 읽을 문장 (TTS)
# vi_short / ko_short: 화면 표시용
# sec: 해당 동작 유지 시간(초)
# ----------------------------------------------------------------------
STEPS = [
    {
        "vi": "Xin chào các bạn. Bây giờ là thời gian thư giãn buổi chiều. "
              "Nếu các bạn đang cảm thấy mệt mỏi hay buồn ngủ, "
              "đây là lúc để cơ thể tỉnh táo trở lại. "
              "Mời các bạn tạm dừng công việc. Hãy ngồi sâu vào ghế, "
              "đặt hai bàn chân phẳng trên sàn, rộng bằng vai. "
              "Giữ lưng thẳng, để hai tay buông nhẹ lên đùi. "
              "Chúng ta sẽ cùng nhau bắt đầu, thật chậm rãi.",
        "vi_short": "Ngồi sâu vào ghế, hai chân chạm sàn",
        "ko_short": "의자에 깊이 앉아 양발을 바닥에",
        "sec": 24,
    },
    {
        "vi": "Trước tiên, chúng ta hít thở để đánh thức cơ thể. "
              "Hãy từ từ hít vào bằng mũi, trong khi tôi đếm. "
              "Một... hai... ba... bốn. Cảm nhận lồng ngực nở ra. "
              "Giữ hơi lại một chút. "
              "Bây giờ thở ra thật chậm bằng miệng. "
              "Một... hai... ba... bốn... năm... sáu. "
              "Thả lỏng vai. Chúng ta hãy lặp lại thêm hai lần nữa, theo nhịp thở của riêng mình.",
        "vi_short": "Hít vào 4 nhịp, thở ra 6 nhịp",
        "ko_short": "4초 들이쉬고 6초 내쉬기",
        "sec": 30,
    },
    {
        "vi": "Bây giờ chúng ta thả lỏng cổ. "
              "Hãy từ từ cúi cằm xuống về phía ngực. "
              "Cảm nhận phần gáy phía sau cổ được kéo giãn. "
              "Giữ yên, và đếm thầm đến mười. "
              "Bây giờ từ từ nâng đầu lên, trở về vị trí thẳng. "
              "Đừng ngả đầu ra sau quá mạnh, chỉ cần về giữa là đủ. "
              "Hãy làm thật nhẹ nhàng.",
        "vi_short": "Cúi cằm xuống ngực, giữ 10 giây",
        "ko_short": "턱을 가슴으로 당겨 10초 유지",
        "sec": 26,
    },
    {
        "vi": "Tiếp theo, hãy nghiêng đầu sang bên phải, "
              "từ từ đưa tai phải về phía vai phải. "
              "Lưu ý, vai trái vẫn giữ yên, không nhấc lên. "
              "Bạn sẽ cảm thấy bên trái của cổ được kéo căng nhẹ. "
              "Giữ yên và đếm đến mười. "
              "Bây giờ từ từ đưa đầu trở về giữa. "
              "Rồi nghiêng sang bên trái, đưa tai trái về phía vai trái. "
              "Giữ và đếm đến mười. Trở về giữa.",
        "vi_short": "Nghiêng tai về vai, mỗi bên 10 giây",
        "ko_short": "귀를 어깨로 기울여 좌우 10초씩",
        "sec": 34,
    },
    {
        "vi": "Bây giờ đến phần vai, hãy làm theo từng bước. "
              "Đầu tiên, từ từ nâng cả hai vai lên cao về phía tai. "
              "Sau đó, kéo hai vai ra phía sau, ép hai bả vai lại gần nhau. "
              "Rồi hạ vai xuống thấp, và đưa vai trở về phía trước. "
              "Đó là một vòng tròn. Hãy xoay vai thật chậm như vậy, "
              "lên trên, ra sau, xuống dưới, ra trước. Làm năm vòng.",
        "vi_short": "Xoay vai: lên - ra sau - xuống - ra trước",
        "ko_short": "어깨를 위→뒤→아래→앞으로 천천히 5회",
        "sec": 30,
    },
    {
        "vi": "Bây giờ đổi chiều, xoay vai về phía trước. "
              "Nâng vai lên, đưa ra phía trước, hạ xuống, rồi ra sau. "
              "Làm thật chậm, năm vòng. "
              "Cảm nhận khớp vai và cơ vai đang được làm nóng, "
              "máu lưu thông tốt hơn, cơn buồn ngủ dần tan biến.",
        "vi_short": "Xoay vai ngược chiều, 5 vòng",
        "ko_short": "어깨를 반대 방향으로 5회 돌리기",
        "sec": 24,
    },
    {
        "vi": "Tiếp theo, chúng ta mở rộng lồng ngực. "
              "Hãy đưa hai tay ra phía sau lưng, "
              "đan mười ngón tay vào nhau phía sau. "
              "Từ từ duỗi thẳng hai cánh tay, kéo nhẹ xuống dưới, "
              "đồng thời ưỡn ngực ra phía trước và hơi ngẩng cằm lên. "
              "Bạn sẽ cảm thấy phần ngực và vai trước được mở ra. "
              "Hít một hơi sâu, và giữ trong mười giây.",
        "vi_short": "Đan tay sau lưng, ưỡn ngực, giữ 10 giây",
        "ko_short": "등 뒤로 깍지 끼고 가슴 펴 10초",
        "sec": 28,
    },
    {
        "vi": "Bây giờ ngược lại, chúng ta giãn phần lưng trên. "
              "Hãy đan hai bàn tay vào nhau phía trước, "
              "lật lòng bàn tay hướng ra ngoài, "
              "rồi đẩy thẳng hai tay về phía trước, ngang tầm ngực. "
              "Cúi nhẹ đầu xuống, cuộn tròn phần lưng trên, "
              "như thể bạn đang ôm một quả bóng lớn trước ngực. "
              "Cảm nhận khoảng giữa hai bả vai được kéo giãn. Giữ mười giây.",
        "vi_short": "Đẩy tay ra trước, cuộn tròn lưng trên",
        "ko_short": "팔을 앞으로 밀고 등을 둥글게 10초",
        "sec": 28,
    },
    {
        "vi": "Tiếp theo là giãn hai bên eo. "
              "Hãy đưa tay phải thẳng lên cao quá đầu, "
              "tay trái đặt nhẹ bên hông trái. "
              "Từ từ nghiêng người sang bên trái, "
              "đưa tay phải vươn dài theo hướng đó. "
              "Giữ cho mông không rời khỏi ghế. "
              "Cảm nhận bên hông phải được kéo dài. Giữ mười giây. "
              "Từ từ trở về giữa. Bây giờ đổi bên, "
              "tay trái lên cao và nghiêng sang phải. Giữ mười giây.",
        "vi_short": "Vươn tay nghiêng người, giãn eo 2 bên",
        "ko_short": "팔을 올려 옆구리 좌우로 늘이기",
        "sec": 36,
    },
    {
        "vi": "Bây giờ chúng ta xoay phần thân trên. "
              "Hãy đặt tay phải lên đầu gối trái, "
              "tay trái vịn vào thành ghế phía sau. "
              "Giữ lưng thẳng, từ từ xoay thân mình sang bên trái, "
              "quay đầu nhìn ra phía sau vai trái. "
              "Lưu ý, không gập eo, không ngả người ra sau. Giữ mười giây. "
              "Từ từ quay trở lại phía trước. Đổi bên: "
              "tay trái lên gối phải, xoay người sang bên phải. Giữ mười giây.",
        "vi_short": "Xoay thân trên, nhìn ra sau vai",
        "ko_short": "상체를 비틀어 어깨 너머 보기 (좌우)",
        "sec": 36,
    },
    {
        "vi": "Tiếp theo là phần chân, để máu lưu thông xuống dưới. "
              "Hãy duỗi thẳng chân phải ra phía trước, "
              "nhấc gót chân lên khỏi sàn. "
              "Bây giờ kéo các ngón chân hướng ngược về phía mình. "
              "Bạn sẽ cảm thấy bắp chân và mặt sau đùi căng nhẹ. Giữ mười giây. "
              "Hạ chân xuống. Bây giờ làm với chân trái: "
              "duỗi thẳng, kéo mũi chân về phía mình, giữ mười giây.",
        "vi_short": "Duỗi chân, kéo mũi chân về phía mình",
        "ko_short": "다리 뻗어 발끝 몸쪽으로 당기기",
        "sec": 32,
    },
    {
        "vi": "Bây giờ hãy xoay cổ chân. "
              "Nhấc chân phải lên một chút, "
              "vẽ những vòng tròn trong không khí bằng mũi bàn chân, "
              "năm vòng theo một chiều, rồi năm vòng ngược lại. "
              "Đổi sang chân trái, làm tương tự. "
              "Động tác này giúp đôi chân bớt nặng nề và tê mỏi.",
        "vi_short": "Xoay cổ chân, vẽ vòng tròn 2 bên",
        "ko_short": "발목으로 원 그리며 돌리기 (좌우)",
        "sec": 28,
    },
    {
        "vi": "Chúng ta sắp kết thúc. "
              "Hãy đặt hai tay nhẹ lên đùi, ngồi thẳng, thả lỏng vai. "
              "Nhắm mắt lại nếu bạn muốn. "
              "Hít vào thật sâu bằng mũi, cảm nhận cơ thể đã nhẹ nhõm hơn. "
              "Rồi thở ra thật chậm bằng miệng. "
              "Một lần nữa, hít vào... và thở ra. "
              "Lần cuối, hít vào... và thở ra thật chậm.",
        "vi_short": "Nhắm mắt, hít thở sâu 3 lần",
        "ko_short": "눈 감고 깊은 호흡 3회",
        "sec": 30,
    },
    {
        "vi": "Rất tốt. Chúng ta đã hoàn thành bài giãn cơ buổi chiều. "
              "Bây giờ cơ thể đã tỉnh táo và thoải mái hơn. "
              "Hãy từ từ mở mắt ra. "
              "Cảm ơn các bạn đã cùng tham gia. "
              "Chúc các bạn buổi chiều làm việc thật khỏe khoắn và an toàn. Xin cảm ơn.",
        "vi_short": "Hoàn thành! Chúc buổi chiều khỏe khoắn",
        "ko_short": "끝! 활기찬 오후 되세요",
        "sec": 18,
    },
]


# ----------------------------------------------------------------------
# 베트남어 TTS (Windows 우선)
# ----------------------------------------------------------------------
def _speak_vietnamese(text):
    """베트남어 여성 음성으로 아주 천천히, 차분하게 읽기. Windows SAPI 우선."""
    try:
        if sys.platform.startswith("win"):
            import win32com.client  # pywin32
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = speaker.GetVoices()
            chosen = None
            female = None
            # 1순위: 베트남어 여성 / 2순위: 베트남어 아무거나 / 3순위: 아무 여성
            for i in range(voices.Count):
                v = voices.Item(i)
                desc = v.GetDescription()
                is_vi = ("Vietnam" in desc or "Viet" in desc or "HoaiMy" in desc
                         or "An" in desc)
                # 베트남어 여성 음성: HoaiMy(여성), An은 남성
                if "HoaiMy" in desc:
                    chosen = v
                    break
                if is_vi and chosen is None:
                    chosen = v
                if ("Female" in desc or "Zira" in desc or "Hoai" in desc) and female is None:
                    female = v
            if chosen is None and female is not None:
                chosen = female
            if chosen is not None:
                speaker.Voice = chosen
            # 아주 천천히: Rate 범위 -10(가장 느림) ~ +10. -4 로 충분히 느리고 또렷하게.
            speaker.Rate = -4
            speaker.Volume = 100
            speaker.Speak(text)
            return True
    except Exception as e:
        print("TTS(win32com) 실패:", e)
    # pyttsx3 대체 (여성·느리게)
    try:
        import pyttsx3
        eng = pyttsx3.init()
        eng.setProperty("rate", 120)  # 느리게 (기본 200 대비 많이 낮춤)
        eng.setProperty("volume", 1.0)
        picked = None
        for v in eng.getProperty("voices"):
            name = (v.name + " " + v.id).lower()
            if "hoaimy" in name or ("viet" in name and "female" in name):
                picked = v.id; break
            if "viet" in name and picked is None:
                picked = v.id
            if "female" in name and picked is None:
                picked = v.id
        if picked:
            eng.setProperty("voice", picked)
        eng.say(text)
        eng.runAndWait()
        return True
    except Exception as e:
        print("TTS(pyttsx3) 실패:", e)
    # macOS 대체 (여성 베트남어 Linh, 느리게)
    if sys.platform == "darwin":
        os.system('say -v Linh -r 130 "%s" 2>/dev/null' % text.replace('"', ''))
        return True
    return False


# ----------------------------------------------------------------------
# 배경음악 (Windows: winsound 루프 / mac,linux: aplay)
# ----------------------------------------------------------------------
class _MusicPlayer:
    def __init__(self):
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if not os.path.exists(RELAX_MUSIC):
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        if sys.platform.startswith("win"):
            import winsound
            # 비동기 루프 재생 (안내 끝날 때까지 반복)
            winsound.PlaySound(
                RELAX_MUSIC,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
            self._stop.wait()
            winsound.PlaySound(None, winsound.SND_PURGE)  # 정지
        else:
            while not self._stop.is_set():
                if sys.platform == "darwin":
                    os.system('afplay "%s"' % RELAX_MUSIC)
                else:
                    os.system('aplay "%s" 2>/dev/null' % RELAX_MUSIC)
                if self._stop.is_set():
                    break

    def stop(self):
        self._stop.set()
        if sys.platform.startswith("win"):
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass


# ----------------------------------------------------------------------
# 스트레칭 안내 전체 화면 창
# ----------------------------------------------------------------------
class StretchingWindow:
    def __init__(self, parent=None):
        self.parent = parent
        self.music = _MusicPlayer()
        self._cancel = threading.Event()

    def run(self):
        """별도 스레드에서 호출 권장. 전체 안내 진행."""
        # Tk 창은 메인스레드에서 만들어야 안전하므로 parent.after로 띄움
        if self.parent is not None:
            self.parent.after(0, self._open_window)
        else:
            self._open_window()

    def _open_window(self):
        self.win = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.win.title("Giãn cơ / 스트레칭")
        self.win.configure(bg="#0f2540")
        self.win.attributes("-topmost", True)
        try:
            self.win.state("zoomed")  # Windows 전체화면
        except Exception:
            self.win.geometry("900x650")

        self.lbl_count = tk.Label(self.win, text="", font=("Arial", 22, "bold"),
                                  fg="#7fd1ff", bg="#0f2540")
        self.lbl_count.pack(pady=(40, 10))

        self.lbl_vi = tk.Label(self.win, text="", font=("Arial", 40, "bold"),
                               fg="#ffffff", bg="#0f2540", wraplength=1100, justify="center")
        self.lbl_vi.pack(pady=20, expand=True)

        self.lbl_ko = tk.Label(self.win, text="", font=("Malgun Gothic", 26),
                               fg="#cfe8ff", bg="#0f2540", wraplength=1100, justify="center")
        self.lbl_ko.pack(pady=10)

        self.lbl_timer = tk.Label(self.win, text="", font=("Consolas", 30, "bold"),
                                  fg="#9effa0", bg="#0f2540")
        self.lbl_timer.pack(pady=20)

        btn = tk.Button(self.win, text="✕ Đóng / 닫기", font=("Arial", 14),
                        command=self._close, bg="#2a4a6a", fg="white", relief="flat")
        btn.pack(pady=10)
        self.win.protocol("WM_DELETE_WINDOW", self._close)

        # 음악 시작
        self.music.start()
        # 진행 스레드 시작
        threading.Thread(target=self._sequence, daemon=True).start()

    def _sequence(self):
        total = len(STEPS)
        for idx, step in enumerate(STEPS, 1):
            if self._cancel.is_set():
                break
            # 화면 갱신 (메인스레드)
            self._ui(lambda i=idx, s=step:
                     self._update_labels(i, total, s))
            # 음성 안내: 미리 만든 고음질 mp3 우선, 없으면 내장 TTS
            vf = _voice_file(idx)
            if vf:
                _play_audio_blocking(vf)
            else:
                _speak_vietnamese(step["vi"])
            # 동작 유지 시간 카운트다운
            self._countdown(step["sec"])
        # 종료
        self.music.stop()
        self._ui(self._close)

    def _update_labels(self, idx, total, step):
        self.lbl_count.config(text="Bước %d / %d  ·  단계 %d / %d" % (idx, total, idx, total))
        self.lbl_vi.config(text=step["vi_short"])
        self.lbl_ko.config(text=step["ko_short"])

    def _countdown(self, sec):
        for remaining in range(sec, 0, -1):
            if self._cancel.is_set():
                return
            self._ui(lambda r=remaining: self.lbl_timer.config(text="%d" % r))
            time.sleep(1)

    def _ui(self, fn):
        try:
            self.win.after(0, fn)
        except Exception:
            pass

    def _close(self):
        self._cancel.set()
        self.music.stop()
        try:
            self.win.destroy()
        except Exception:
            pass


def start_stretching(parent=None):
    """외부에서 호출하는 진입점."""
    StretchingWindow(parent).run()


# 단독 테스트 실행
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    start_stretching(root)
    root.mainloop()
