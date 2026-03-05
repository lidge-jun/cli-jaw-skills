# 01. 기존(Traditional) STT 원리

## 아키텍처

전통적 STT는 **오디오 → 텍스트** 단방향 파이프라인이다.

```
Audio Waveform
  ↓ Feature Extraction (Mel Spectrogram)
  ↓ Acoustic Model (음향 → 음소)
  ↓ Language Model (음소 → 단어)
  ↓ Decoder (빔 서치)
  → Text
```

### 세대별 변화

| 세대 | 방식 | 대표 모델 |
|------|------|----------|
| 1세대 | GMM-HMM | Kaldi, CMU Sphinx |
| 2세대 | DNN-HMM | DeepSpeech |
| 3세대 | End-to-End (CTC/Attention) | Wav2Vec 2.0, Conformer |
| 4세대 | Encoder-Decoder Transformer | **Whisper**, Chirp, USM |

## Whisper (OpenAI)

- 680,000시간 웹 오디오로 학습한 범용 STT
- Encoder-Decoder Transformer 구조
- 다국어 (99개 언어) + 번역 지원
- 모델 크기: tiny(39M) ~ large-v3(1.5B)

### 동작 원리
1. 오디오 → 30초 단위 청크로 분할
2. 각 청크 → 80채널 Mel Spectrogram 변환
3. Encoder가 오디오 특징 추출
4. Decoder가 autoregressively 텍스트 생성
5. 특수 토큰으로 언어/타임스탬프/작업 제어

### 한국어 성능
- CER(Character Error Rate): **11.13%** (KsponSpeech 벤치마크)
- 영어 WER: 3.91% → 한국어는 약 3배 나쁨
- 원인: 학습 데이터에서 한국어 비중 낮음 + 띄어쓰기 불일치

### 변형 모델
| 이름 | 특징 |
|------|------|
| **mlx-whisper** | Apple Silicon 최적화, Metal GPU 활용, 2x 빠름 |
| **faster-whisper** | CTranslate2 기반, CPU에서도 4x 빠름 |
| **whisper.cpp** | C++ 포팅, 저사양 디바이스용 |
| **EZWhisper (에너자이)** | 한국어 fine-tune, 13MB로 large-v3 능가 |

## Google Chirp / USM

- Universal Speech Model (USM) 기반
- 1,200만 시간 + 300개 언어로 학습
- Cloud Speech-to-Text V2 API로 제공
- **가격: $16/1000분** (비쌈)

## 전용 STT의 한계

1. **프롬프트 불가** — 도메인 용어 힌트를 줄 수 없음
2. **출력 포맷 고정** — 줄바꿈, 숫자 표기 등 커스텀 불가
3. **문맥 이해 없음** — "수정원"과 "수종원"을 구별 못함
4. **후처리 필요** — 문단 분리, 화자 추정 등 별도 파이프라인

## 전용 STT의 강점 (LLM STT 대비)

1. **필러/비언어 정보 보존** — (uh), (pause), 기침 등 그대로 기록
2. **타임스탬프 정밀도** — 단어/음절 단위 시간 정보 제공
3. **화자분리(Diarization)** — 전문 모듈 (pyannote, NeMo 등) 연계 가능
4. **오프라인 가능** — 네트워크 없이도 동작 (Whisper, whisper.cpp)
5. **결정적 출력** — 같은 입력 → 같은 출력 (LLM은 비결정적)

→ **용도 요약**: 날것의 verbatim 전사가 필요하면 전용 STT,
  구조화된 노트가 필요하면 LLM STT가 적합.
