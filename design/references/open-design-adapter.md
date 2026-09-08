# Open Design Adapter (optional, v2+)

Open Design daemon이 설치되어 있으면 adapter로 연결.

```bash
jaw design open-design status
jaw design open-design list
jaw design open-design import --project <od-project-id>
```

원칙:

- Open Design source는 vendor하지 않는다
- import는 복사. 원본 project를 live edit하지 않는다
- v1 core dependency가 아니다
- adapter panel은 설정 또는 experimental에서만 노출
