#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from app.model.intent.core.EmotionAnalyzer import EmotionAnalyzer

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def test_emotion_analyzer():
    print("begin test_emotion_analyzer")
    try:
        analysis = EmotionAnalyzer()

        emotion_result = analysis.analyze("今天行情不错")
        print(emotion_result)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_emotion_analyzer()