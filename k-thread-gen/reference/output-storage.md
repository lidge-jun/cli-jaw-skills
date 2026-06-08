# K-Thread Output Storage

각 쓰레드는 **개별 폴더**로 저장한다. 글 + 사진/동영상을 한 폴더에 모은다.

```text
_thread/
├── YYMMDD/
│   ├── N_제목/              ← 쓰레드 폴더
│   │   ├── post.md          ← 본문 + 댓글 텍스트
│   │   ├── cover.jpg        ← 본문 첨부 이미지
│   │   ├── screenshot_1.png ← 추가 이미지
│   │   └── demo.mp4         ← 동영상 (있으면)
│   ├── N_제목/
│   │   ├── post.md
│   │   └── cover.jpg
│   └── ...
├── _legacy/                 ← 다 쓴 쓰레드 보관
└── ...
```

## 규칙

- 쓰레드 하나 = 폴더 하나
- 텍스트 파일명: `post.md` (고정)
- 미디어 파일: 폴더 안에 함께 저장
- `post.md` 안에 미디어 참조: `(첨부: cover.jpg)` 형태로 표기
- 기존 단일 .md 파일 방식은 더 이상 사용하지 않음
