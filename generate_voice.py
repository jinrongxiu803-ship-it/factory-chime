#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고음질 베트남어 음성 생성 스크립트
Tạo file giọng nói tiếng Việt chất lượng cao

★ 인터넷 연결된 PC에서 딱 한 번만 실행하세요 ★
★ Chỉ chạy MỘT LẦN trên máy có kết nối Internet ★

실행하면 stretching.py 의 나레이션 14단계를 읽어
voices/ 폴더에 step_01.mp3 ~ step_14.mp3 를 만듭니다.
(Microsoft Edge 신경망 음성 HoaiMy - 베트남어 여성, 무료)

사용법:
    pip install edge-tts
    python generate_voice.py

생성 후에는 인터넷 없이도 차임 프로그램이 이 음성을 재생합니다.
"""

import os
import sys
import ast
import asyncio

APP_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(APP_DIR, "voices")

# ── 음성 설정 ──────────────────────────────────────────────
# HoaiMy = 베트남어 여성(차분), 다른 선택: vi-VN-NamMinhNeural(남성)
VOICE = "vi-VN-HoaiMyNeural"
# 말하는 속도: 아주 천천히 = -25% (정중하고 또렷하게) — 현재 voices 와 동일
RATE = "-25%"
# 음높이: 기본
PITCH = "+0Hz"
# ──────────────────────────────────────────────────────────


def load_steps():
    """stretching.py 에서 STEPS 의 베트남어 문장을 읽어온다."""
    path = os.path.join(APP_DIR, "stretching.py")
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if getattr(t, "id", None) == "STEPS":
                    return ast.literal_eval(node.value)
    raise RuntimeError("STEPS 를 찾을 수 없습니다 / Không tìm thấy STEPS")


async def make_one(text, out_path):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(out_path)


async def main():
    try:
        import edge_tts  # noqa
    except ImportError:
        print("먼저 설치하세요 / Hãy cài đặt trước:  pip install edge-tts")
        sys.exit(1)

    os.makedirs(VOICE_DIR, exist_ok=True)
    steps = load_steps()
    print("총 %d 개 음성 생성 시작 / Bắt đầu tạo %d file giọng nói\n" % (len(steps), len(steps)))

    for i, step in enumerate(steps, 1):
        out = os.path.join(VOICE_DIR, "step_%02d.mp3" % i)
        text = step["vi"]
        try:
            await make_one(text, out)
            size = os.path.getsize(out)
            print("  [%2d/%d] OK  step_%02d.mp3  (%d KB)" % (i, len(steps), i, size // 1024))
        except Exception as e:
            print("  [%2d/%d] 실패 / Lỗi:" % (i, len(steps)), e)

    print("\n완료! voices/ 폴더를 확인하세요.")
    print("Hoàn tất! Kiểm tra thư mục voices/")
    print("이제 인터넷 없이도 chime.py 가 이 음성을 재생합니다.")


if __name__ == "__main__":
    asyncio.run(main())
