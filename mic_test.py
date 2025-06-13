#!/usr/bin/env python3
"""
마이크 및 음성 인식 테스트 스크립트
"""

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import time
import threading
from collections import deque

# 전역 변수
volume_queue = deque(maxlen=10)
is_listening = False

def test_microphone_devices():
    """사용 가능한 마이크 장치 목록을 출력합니다."""
    print("=" * 50)
    print("🎤 사용 가능한 오디오 장치 목록:")
    print("=" * 50)
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:  # 입력 장치만
            print(f"[{i}] {device['name']} - {device['max_input_channels']}채널 (입력)")
    
    print("=" * 50)
    print(f"기본 입력 장치: {sd.default.device[0]}")
    print("=" * 50)

def test_volume_detection():
    """실시간 볼륨 감지 테스트"""
    print("\n🔊 볼륨 감지 테스트 시작 (10초간)")
    print("마이크에 대고 말해보세요...")
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"오디오 상태 오류: {status}")
        
        volume_norm = np.linalg.norm(indata) ** 3
        volume_percentage = min(volume_norm, 100)
        volume_queue.append(volume_percentage)
    
    try:
        with sd.InputStream(callback=audio_callback, samplerate=16000, channels=1):
            start_time = time.time()
            while time.time() - start_time < 10:  # 10초간 테스트
                if len(volume_queue) > 0:
                    avg_volume = sum(volume_queue) / len(volume_queue)
                    # 볼륨 바 시각화
                    bar_length = int(avg_volume / 5)  # 20단계로 표시
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    print(f"\r볼륨: [{bar}] {avg_volume:.1f}%", end="", flush=True)
                
                time.sleep(0.1)
        
        print("\n✅ 볼륨 감지 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 볼륨 감지 오류: {e}")
        return False
    
    return True

def test_speech_recognition():
    """음성 인식 테스트"""
    print("\n🎙️ 음성 인식 테스트")
    print("아무 말이나 해보세요 (최대 5초)...")
    
    recognizer = sr.Recognizer()
    
    # 마이크 설정 최적화
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0
    
    try:
        with sr.Microphone(sample_rate=16000) as source:
            print("🔧 주변 소음 조정 중...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ 조정 완료! 이제 말해보세요...")
            
            # 음성 듣기
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("🔄 음성 인식 처리 중...")
            
            # Google Speech Recognition
            try:
                text = recognizer.recognize_google(audio, language="ko-KR")
                print(f"✅ 인식 결과: '{text}'")
                return True
                
            except sr.UnknownValueError:
                print("❌ 음성을 이해하지 못했습니다.")
                return False
                
            except sr.RequestError as e:
                print(f"❌ Google Speech Recognition 오류: {e}")
                return False
                
    except sr.WaitTimeoutError:
        print("❌ 음성 입력 시간 초과")
        return False
        
    except Exception as e:
        print(f"❌ 마이크 오류: {e}")
        return False

def continuous_speech_test():
    """연속 음성 인식 테스트 (옛날 코드와 동일한 방식)"""
    print("\n🔄 연속 음성 인식 테스트 (30초간)")
    print("계속 말해보세요. 'quit' 또는 '종료'라고 말하면 중단됩니다.")
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    
    def recognize_speech():
        with sr.Microphone(sample_rate=16000) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎤 음성 인식 대기 중...")
            
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                text = recognizer.recognize_google(audio, language="ko-KR")
                return text
            except sr.UnknownValueError:
                return "음성을 이해하지 못했습니다."
            except sr.RequestError as e:
                return f"STT 서비스 오류: {e}"
            except Exception as e:
                return f"오류: {e}"
    
    start_time = time.time()
    
    while time.time() - start_time < 30:  # 30초간 테스트
        try:
            text = recognize_speech()
            if text:
                print(f"📝 인식됨: {text}")
                
                # 종료 조건
                if any(word in text.lower() for word in ['quit', '종료', '끝', 'stop']):
                    print("🛑 음성 인식 중단됨")
                    break
                    
        except Exception as e:
            print(f"❌ 연속 인식 오류: {e}")
            
        time.sleep(0.1)
    
    print("✅ 연속 음성 인식 테스트 완료!")

def main():
    """메인 테스트 함수"""
    print("🤖 마이크 및 음성 인식 테스트 시작!")
    print("=" * 60)
    
    # 1. 장치 목록 확인
    test_microphone_devices()
    
    input("\n아무 키나 눌러서 계속하세요...")
    
    # 2. 볼륨 감지 테스트
    if not test_volume_detection():
        print("❌ 볼륨 감지에 실패했습니다. 마이크를 확인해주세요.")
        return
    
    input("\n아무 키나 눌러서 계속하세요...")
    
    # 3. 기본 음성 인식 테스트
    if not test_speech_recognition():
        print("❌ 기본 음성 인식에 실패했습니다.")
        return
    
    input("\n아무 키나 눌러서 연속 음성 인식 테스트를 시작하세요...")
    
    # 4. 연속 음성 인식 테스트
    continuous_speech_test()
    
    print("\n🎉 모든 테스트 완료!")
    print("이제 웹 애플리케이션에서 음성 인식이 작동할 것입니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        print("라이브러리 설치를 확인해주세요:")
        print("pip install sounddevice SpeechRecognition numpy pyaudio")