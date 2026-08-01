# 인수인계 — SULSUL 블로그 자동화

작성: 2026-08-02 · 대상: 다음 채팅 세션(사람 + AI)

---

## 0. 다음 세션에서 쓸 모델 (먼저 읽을 것)

**이번 작업을 한 모델은 Claude Opus 5 (Cursor)입니다. 다음 세션에서는 제외해 주세요.**

대표님 요청 사항이며, 이유는 아래 §4의 사고 두 건이 모두 이 모델의 판단 착오에서 나왔기 때문입니다.
같은 모델이 이어받으면 같은 맹점을 반복할 위험이 있어, 다른 모델이 한 번 검토하는 편이 낫습니다.

| 구분 | 모델 | 다음 세션 사용 |
|---|---|---|
| 이번 설계·구현을 한 채팅 모델 | **Claude Opus 5** | ❌ 제외 |
| 대안 (Cursor에서 선택 가능) | GPT-5.6 Sol / GPT-5.6 Terra / Claude Sonnet 5 / Claude Fable 5 / Grok 4.5 | ⭕ 이 중 하나 |
| 블로그 글을 실제로 쓰는 모델 (런타임, 별개) | **GPT-4o** (`SULSUL_BLOG_MODEL` 환경변수) | 유지 — 채팅 모델과 무관 |

> 헷갈리기 쉬운 부분: "블로그를 설계한 모델"과 "매일 블로그 글을 쓰는 모델"은 다릅니다.
> 앞의 것은 Cursor 채팅 모델(Opus 5), 뒤의 것은 OpenAI GPT-4o입니다. 위 표의 제외 대상은 앞의 것입니다.

새 채팅 첫 메시지 예시:

```
@docs/HQ_CHAT_RULES.md @AGENTS.md @HANDOFF.md
sulsul-blog 이어서 진행. HANDOFF.md의 §5 남은 일부터.
```

---

## 1. 이 프로젝트가 하는 일

`blog.sulsul.app` — SULSUL 앱으로 사람을 데려오는 영어 블로그입니다.
GitHub Actions가 매일 정해진 시각에 GPT-4o로 글을 쓰고, 검증을 통과한 것만 저장·발행합니다.

| 언제 | 무엇 | 몇 개 |
|---|---|---|
| 매일 오전 9시 | 트렌드 기반 글 | 2개 |
| 평일 오후 9시 | 교재 기반 글 | 3개 |

발행량을 이 수준으로 낮춘 이유는 구글의 "대량 생성 콘텐츠" 제재를 피하기 위해서입니다.
(월 900개 → 약 100개)

---

## 2. 지금 상태 — 끝난 것

- 블로그 기본 SEO 정비: 사이트맵, robots.txt, RSS, 구조화 데이터, OG 이미지 자동 생성
- AI 검색엔진 대응(GEO): `llms.txt`, `llms-full.txt`, `/what-is-sulsul` 브랜드 정의 페이지
- 글 생성 프롬프트 v2: 뉴스 요약이 아니라 롱테일 질문에 답하는 글
- 품질 게이트: 분량·중복·표·FAQ·양방향 대화 검사, 실패 시 최대 4회 자동 수정
- 한글 로마자 표기 자동 교정 (`tools/romanize.py`)
- **공개 문구 검사기 (`tools/check_public_copy.py`)** — §4 참고
- 도메인 연결 완료, GitHub 토큰 재발급 완료, Vercel 환경변수 설정 완료

---

## 3. 파일 지도

| 파일 | 역할 |
|---|---|
| `generate_seo_posts.py` | 글 생성기. 프롬프트, 품질 게이트, 자동 수정 루프 |
| `tools/check_public_copy.py` | 공개 문구 검사기. 발행 차단 장치 |
| `tools/romanize.py` | 한글 → 로마자 정확 변환 |
| `.github/workflows/trend_9am.yml` | 매일 오전 자동 발행 |
| `.github/workflows/textbook_9pm.yml` | 평일 저녁 자동 발행 |
| `src/app/what-is-sulsul/page.tsx` | 브랜드 정의 페이지 |
| `public/llms.txt`, `llms-full.txt` | AI 검색엔진용 브리핑 |
| `_posts/` | 발행된 글 · `_rejected/` 게이트 탈락 글 |

---

## 4. 사고 기록 — 반드시 읽을 것

### 사고 1: 내부 지시문이 고객 페이지에 그대로 발행됨

AI가 가짜 할인가를 지어내지 못하게 만든 **금지 규칙**을 고객이 읽는 페이지에 복사해 넣었습니다.

> 발행됐던 문장: "No fake strikethrough prices. No invented "original" $299 anchors."

아무도 의심하지 않은 걸 스스로 해명하는 문장이라 오히려 의심을 만듭니다.
경쟁사 이름 나열(Duolingo, TTMIK, 세종)도 내부 정리용인데 공개돼 있었습니다.

**근본 원인:** AI에게 주는 지시문과 사람이 읽는 글을 같은 저장소에 구분 없이 써둠.

### 사고 2: 사고 1을 고치면서 또 다른 변명을 넣음

> 넣었던 문장: "가격은 표시된 그대로입니다 (One price, shown as it is)."

역시 아무도 묻지 않은 것에 대한 해명입니다. 같은 실수를 반복한 것입니다.

### 그래서 만든 장치

`tools/check_public_copy.py` 가 아래를 잡아냅니다.

| 규칙 | 걸리는 예 |
|---|---|
| `price` | `$28.99`, `priceCurrency` |
| `denial` | "no fake", "no invented", "strikethrough" |
| `discount` | 환불 보장, % 할인, 무료 체험 |
| `competitor` | Duolingo, TTMIK, Sejong, Babbel, Anki |
| `instruction` | "hard ban", "(facts only)", "system prompt" |
| `slop` | "delve", "dive into", "in conclusion" |
| `overclaim` | "fluent in 30 days", Netflix 제휴 주장 |

**세 지점에서 실행됩니다.** 하나를 뚫어도 다음에서 막힙니다.

1. 생성기가 글을 저장하기 직전 (`validate_post`) → 걸리면 AI에게 수정 지시를 되돌려 보냄
2. 자동 발행이 GitHub에 올리기 직전 (워크플로 스텝)
3. 사이트를 빌드하기 직전 (`npm run build` → `prebuild`)

수동 확인:

```bash
python3 tools/check_public_copy.py
```

예외를 허용해야 하면 스크립트 안의 `ALLOW` 목록에 **이유와 함께** 추가합니다.
(현재 유일한 예외: 개인 과외 시세 `$30–50` — SULSUL 가격이 아니라 비교 대상이라서)

### 가격 정책 (2026-08-02 변경)

**블로그에는 가격 숫자를 쓰지 않습니다.** 가격은 `sulsul.app` 한 곳에만 있습니다.

- 허용되는 표현: "개인 과외 1회($30–50)보다 적은 돈으로 매일 말하기 훈련"
- 그 다음 랜딩페이지로 링크
- 이유: 두 곳에 가격이 있으면 어긋나고, 낡은 가격을 AI가 물어다 퍼뜨림

---

## 5. 남은 일

### 우선순위 높음

1. **자동 발행 품질 검수**
   검사기는 "사고"를 막을 뿐 "재미없는 글"은 못 막습니다.
   자동 발행을 켜둔 채로 첫 2주는 올라온 글을 사람이 읽어봐야 합니다.

2. **승인제 전환 검토 (대표님 결정 필요)**
   지금은 AI가 쓴 글이 바로 발행됩니다.
   초안만 쌓아두고 대표님이 승인한 것만 올리는 방식으로 바꿀 수 있습니다.
   → 대표님 의사 확인 후 진행

3. **첫 실제 발행 후 게이트 통과율 확인**
   너무 빡빡하면 글이 안 나오고, 너무 느슨하면 품질이 떨어집니다.
   `_rejected/` 에 쌓이는 양을 보고 조정합니다.

### 우선순위 낮음

4. 프로필 사진 구도 선택 (A/B/C 중 — 현재 B 적용 중, 대표님 미확인)
5. 토픽 클러스터 전략 (관련 글끼리 묶어 내부 링크)

---

## 6. 다음 세션이 지켜야 할 것

- **`.cursor/rules/ai-directives.mdc` 와 `docs/CEO_COMMUNICATION.md` 를 먼저 읽을 것.**
  특히: 대표님 보고는 쉬운 말로, URL은 반드시 하이퍼링크로, 대표님 일정·컨디션 참견 금지.
- **공개 문구를 손대면 반드시 `python3 tools/check_public_copy.py` 를 돌릴 것.**
- **고객이 읽는 글에 "우리는 ~하지 않습니다" 식 해명을 쓰지 말 것.**
  술술이 무엇인지만 쓰고, 무엇으로 오해받지 않으려는지는 쓰지 않습니다.
- 결제·인증·DB 스키마 변경은 대표님 승인 후에만.

---

## 7. 확인 방법 (대표님용)

폰에서 아래를 열어 확인하실 수 있습니다.

- [블로그 홈](https://blog.sulsul.app)
- [소개 페이지](https://blog.sulsul.app/what-is-sulsul) — 가격 숫자가 없고, 앱으로 가는 링크만 있으면 정상
- [자동 발행 기록](https://github.com/sulsulkorean/sulsul/actions) — 매일 돌아간 결과
