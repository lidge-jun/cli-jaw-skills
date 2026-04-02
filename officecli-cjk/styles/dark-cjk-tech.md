# Dark CJK Tech — Multi-Language Tech Presentations

## Style Overview

A developer-focused dark style supporting Korean, Japanese, and Chinese in a single deck. Designed for tech talks, architecture reviews, and engineering presentations that mix CJK text with code snippets. Cyan and purple accents echo modern IDE themes.

- **Scenario**: Tech talks, architecture reviews, engineering demos, developer conferences
- **Mood**: Technical, modern, developer-native
- **Tone**: GitHub Dark with cyan and purple accents
- **Language**: Multi-CJK (한국어 / 日本語 / 中文) + English

## Color Palette

| Name           | Hex       | Usage                                   |
| -------------- | --------- | --------------------------------------- |
| Background     | `#0D1117` | GitHub dark, main background            |
| Surface        | `#161B22` | Slightly lighter, card/code blocks      |
| Primary Text   | `#E6EDF3` | Off-white, body text                    |
| Secondary Text | `#8B949E` | Gray, comments, metadata                |
| Cyan Accent    | `#00BCD4` | Primary accent, links, key terms        |
| Purple Accent  | `#7C4DFF` | Secondary accent, highlights, badges    |
| Green          | `#3FB950` | Success, passing tests, positive        |
| Red            | `#F85149` | Errors, failing tests, negative         |
| Yellow         | `#D29922` | Warnings, cautions                      |
| Border         | `#30363D` | Borders, separators                     |
| Code BG        | `#1B2028` | Code block backgrounds                  |

## Typography

| Element            | Font                | Weight    | Size   |
| ------------------ | ------------------- | --------- | ------ |
| Title (any CJK)    | System CJK font     | Bold      | 32pt   |
| Title (Latin)      | Inter                | Bold 700  | 32pt   |
| Body (Korean)      | Malgun Gothic        | Regular   | 15pt   |
| Body (Japanese)    | Yu Gothic            | Regular   | 15pt   |
| Body (Chinese)     | Microsoft YaHei      | Regular   | 15pt   |
| Body (Latin)       | Inter                | Regular   | 15pt   |
| Code               | JetBrains Mono       | Regular   | 13pt   |
| Code (CJK fallback)| D2Coding / Sarasa Mono | Regular | 13pt   |
| Caption            | Inter                | Regular   | 10pt   |

### Per-Language Font Selection

| Language | Heading Font         | Body Font            | Code Font          |
| -------- | -------------------- | -------------------- | ------------------ |
| Korean   | Pretendard Bold      | Malgun Gothic        | D2Coding           |
| Japanese | Yu Gothic Bold       | Yu Gothic            | Sarasa Mono J      |
| Chinese  | Microsoft YaHei Bold | Microsoft YaHei      | Sarasa Mono SC     |

### Font Fallback Chains (Multi-CJK)

| Platform | CJK Chain                                                        |
| -------- | ---------------------------------------------------------------- |
| Windows  | Malgun Gothic → Yu Gothic → Microsoft YaHei → SimSun            |
| macOS    | Apple SD Gothic Neo → Hiragino Sans → PingFang SC               |
| Linux    | Noto Sans CJK KR → Noto Sans CJK JP → Noto Sans CJK SC         |

## Typography Scale

```
Title:     32pt / 42pt line-height (1.31)
Subtitle:  20pt / 28pt line-height (1.40)
Body:      15pt / 26pt line-height (1.73)
Code:      13pt / 22pt line-height (1.69)
Caption:   10pt / 16pt line-height (1.60)
```

## OfficeCLI Commands

### Create tech deck

```bash
officecli create tech-talk.pptx
officecli add tech-talk.pptx / --type slide --prop title="System Architecture"
officecli set tech-talk.pptx /slide[1] --prop background=0D1117
```

### Multi-language title (Korean example)

```bash
officecli set tech-talk.pptx /slide[1]/shape[1] --prop \
  text="마이크로서비스 아키텍처 설계" \
  font="Pretendard" \
  font.size=32 \
  font.color=E6EDF3 \
  bold=true
```

### Japanese title variant

```bash
officecli set tech-talk.pptx /slide[1]/shape[1] --prop \
  text="マイクロサービスアーキテクチャ設計" \
  font="Yu Gothic" \
  font.size=32 \
  font.color=E6EDF3 \
  bold=true
```

### Chinese title variant

```bash
officecli set tech-talk.pptx /slide[1]/shape[1] --prop \
  text="微服务架构设计" \
  font="Microsoft YaHei" \
  font.size=32 \
  font.color=E6EDF3 \
  bold=true
```

### Add code block

```bash
officecli add tech-talk.pptx /slide[1] --type shape --prop \
  text="// 서비스 간 통신 (gRPC)\nfunc (s *OrderService) CreateOrder(ctx context.Context, req *pb.OrderRequest) (*pb.OrderResponse, error) {\n    // 재고 확인\n    stock, err := s.inventoryClient.CheckStock(ctx, req.ItemId)\n    return &pb.OrderResponse{OrderId: uuid.New()}, nil\n}" \
  font="JetBrains Mono" \
  font.size=13 \
  font.color=E6EDF3 \
  fill=1B2028 \
  x=40 y=180 w=640 h=160
```

### Add architecture metric

```bash
officecli add tech-talk.pptx /slide[1] --type shape --prop \
  text="99.99%" \
  font="Inter" \
  font.size=48 \
  font.color=00BCD4 \
  bold=true \
  x=50 y=360 w=200 h=70

officecli add tech-talk.pptx /slide[1] --type shape --prop \
  text="서비스 가용성 (SLA)" \
  font="Malgun Gothic" \
  font.size=14 \
  font.color=8B949E \
  x=50 y=430 w=200 h=30
```

## CJK Auto-Detection

OfficeCLI's CjkHelper automatically detects the dominant CJK script in text and applies appropriate fonts:

```bash
# CjkHelper will detect Korean and apply Malgun Gothic for CJK runs
officecli add tech-talk.pptx /slide[1] --type shape --prop \
  text="이 API는 gRPC를 사용하여 서비스 간 통신을 처리합니다."
# Mixed text → CJK segments get CJK font, Latin segments get Latin font
```

The `BuildSegmentedRuns()` method in `PowerPointHandler.Cjk.cs` splits mixed text into CJK and non-CJK runs, applying the correct font to each segment.

## Example Content (Multi-Language)

```
Korean:  마이크로서비스 아키텍처에서 서비스 메시의 역할
Japanese: マイクロサービスにおけるサービスメッシュの役割
Chinese: 微服务架构中服务网格的作用
English: The Role of Service Mesh in Microservice Architecture
```

## Design Notes

- Tech presentations often mix CJK and Latin text heavily — ensure font fallback is robust
- Code blocks should always use a monospace font with CJK support (JetBrains Mono + D2Coding)
- Color-code terminal output: green (#3FB950) for success, red (#F85149) for errors
- GitHub dark (#0D1117) is familiar to developers — leverages existing visual associations
- Use cyan (#00BCD4) for interactive elements and purple (#7C4DFF) for highlights/badges
- When mixing CJK scripts in one deck, explicitly set fonts per shape — don't rely on auto-detection alone
