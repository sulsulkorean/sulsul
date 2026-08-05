# 인수인계 — SULSUL 블로그 자동화

작성: 2026-08-02 · 대상: 다음 채팅 세션(사람 + AI)

---

## 0. 다음 세션에서 쓸 모델 (먼저 읽을 것)

**이번 작업을 한 모델은 Claude Opus 5 (Cursor)입니다. 다음 세션에서는 제외해 주세요.**

대표님 요청 사항이며, 이유는 아래 §4의 사고 두 건이 모두 이 모델의 판단 착오에서 나왔기 때문입니다.
같은 모델이 이어받으면 같은 맹점을 반복할 위험이 있어, 다른 모델이 한 번 검토하는 편이 낫습니다.

> ⚠️ **Auto 모드로는 모델을 제외할 수 없습니다.** 2026-08-02 세션에서 대표님이 Auto로 설정하셨는데
> Cursor가 또 Opus 5를 골랐습니다. Auto는 요청마다 Cursor가 알아서 고르는 기능이고,
> "이 모델은 빼줘"라는 설정이 아닙니다. 확실히 제외하려면 **채팅 입력창 아래 모델 이름을 눌러
> 직접 지정**해야 합니다.

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

### 발행 모드 (2026-08-05 현재)

**하루 4편 자동 발행 ON** (대표님 승인 2026-08-05).

| 스케줄 (KST) | 무엇 | 몇 개 | 발행 |
|---|---|---|---|
| 매일 오전 9시 | K-컬처 / 트렌드 (k-pop·k-drama·idol·music·food) | 2 | 게이트 통과 → **main 직푸시** → Vercel |
| 매일 오후 9시 | 교재 기반 생존 한국어 | 2 | 동일 |

**표지 이미지:** `_posts`에 이미 쓰인 커버를 피해서 `public/assets/blog/scenes/` 미사용 파일을 먼저 씀. 남는 장면이 없을 때만 OpenAI DALL·E로 1장 생성해 같은 폴더에 저장. 뉴스·아이돌·드라마 스틸은 쓰지 않음.

**비용:** OpenAI 글 생성(매일 최대 4편) + 표지 생성은 풀이 빌 때만. secrets `OPENAI` 필요.

수동 1회 테스트: GitHub Actions에서 해당 워크플로 → **Run workflow**.

일시 중지가 필요하면 워크플로 YAML의 `schedule`을 다시 주석 처리하고 푸시.

---

## 2. 지금 상태 — 끝난 것

- 블로그 기본 SEO 정비: 사이트맵, robots.txt, RSS, 구조화 데이터, OG 이미지 자동 생성
- AI 검색엔진 대응(GEO): `llms.txt`, `llms-full.txt`, `/what-is-sulsul` 브랜드 정의 페이지
- 글 생성 프롬프트 v2: 뉴스 요약이 아니라 롱테일 질문에 답하는 글
- 품질 게이트: 분량·중복·표·FAQ·양방향 대화 검사, 실패 시 최대 4회 자동 수정
- 한글 로마자 표기 자동 교정 (`tools/romanize.py`)
- **공개 문구 검사기 (`tools/check_public_copy.py`)** — §4 참고
- 도메인 연결 완료, GitHub 토큰 재발급 완료, Vercel 환경변수 설정 완료
- **트렌드 글감 수집 수정 (2026-08-02)** — §4 사고 3 참고
- **게이트 통과율이 실행 기록에 남음** — GitHub Actions 실행 페이지 Summary
- **검수 완료 글 일괄 공개 + 표지 중복 해소 (2026-08-03~05)**
- **하루 2+2 자동발행 재개 + 직배포 (2026-08-05)** — PR 승인제 해제, 표지 풀 우선·부족 시 생성
- **본문 이미지 의무화** — 글마다 상황 이미지 + 말하기 연습 이미지, 모바일 스타일 적용
- **품질검사 보강** — 이미지 수·경로, 근거 없는 할인율·문화 일반화, 가짜 출처 추가 검사
- **`/what-is-sulsul` 서비스 소개 페이지 전면 개편 (2026-08-03)**

---

## 3. 파일 지도

| 파일 | 역할 |
|---|---|
| `generate_seo_posts.py` | 글 생성기. 프롬프트, 품질 게이트, 자동 수정 루프 |
| `tools/check_public_copy.py` | 공개 문구 검사기. 발행 차단 장치 |
| `tools/romanize.py` | 한글 → 로마자 정확 변환 |
| `.github/workflows/trend_9am.yml` | 매일 09:00 KST — K-컬처 2편 → main 직배포 |
| `.github/workflows/textbook_9pm.yml` | 매일 21:00 KST — 교재 2편 → main 직배포 |
| `src/app/what-is-sulsul/page.tsx` | 브랜드 정의 페이지 |
| `public/llms.txt`, `llms-full.txt` | AI 검색엔진용 브리핑 |
| `_posts/` | 공개된 글 |
| `_rejected/`, `_preview/` | 로컬 검토용. GitHub에 올리지 않음 |

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

### 사고 3: 엉뚱한 글 20개의 진짜 원인은 지시문이 아니라 글감이었다 (2026-08-02 발견·수정)

지웠던 글 20개의 파일 이름이 남아 있어서 확인해보니 이랬습니다.

> `왜 코가 늘 막히나 — 메이요 클리닉` · `알파벳 K 노래 — ABCmouse` · `유타주 속보 — KSL` · `K — 나무위키`

당시엔 "글 쓰는 지시문이 문제"로 보고 지시문을 고쳤지만, 원인은 **글감을 가져오는 검색**이었습니다.
`K-Pop OR K-Drama OR BTS` 로 웹 전체를 검색하면 뉴스가 아니라 사이트 첫 화면과 사전 항목이 나옵니다.
2026-08-02에 같은 검색을 다시 돌려보니 `K Car 중고차`, `K — 나무위키`, `Google` 이 그대로 나왔습니다.
**즉 이 고장은 그때 고쳐지지 않았고, 5개월 뒤에도 살아 있었습니다.**

**교훈:** 결과물(글)만 보고 원인을 지목하면 안 됩니다. 입력(글감)까지 거슬러 올라가 확인해야 합니다.

**수정한 것:**

| 무엇 | 어떻게 |
|---|---|
| 웹 전체 검색 → 뉴스 전용 검색 | 실제 기사만 잡힙니다. 검색어는 날짜에 따라 5개 중 하나로 돌아감 |
| 한국·한류와 무관한 글감 자동 배제 | `trend_seed_ok()` — 과거 사고 사례 10건 전부 차단 확인, 실제 K-pop 뉴스 4건은 통과 확인 |
| 쓸 만한 글감이 없으면 0편 | 억지로 채우지 않습니다. 검색이 막혀도(자주 막힘) 조용히 0편 |

### 사고 4: “배포합니다”라고 해놓고 커밋만 하고 끝냄 (2026-08-05)

표지 이미지 중복을 고친 뒤 AI가 **「커밋·배포합니다」**라고 보고했지만, 실제로는:

1. 로컬 커밋만 됨 (`0b8245e`)
2. `git push origin main`이 승인/중단으로 **실패·미완료**
3. 푸시 성공·라이브 확인을 다시 하지 않음
4. 대표님은 배포된 줄 알고 넘겼는데, 다음날까지 라이브에는 예전 이미지가 그대로였음

**교훈:** 커밋 ≠ 배포. Vercel은 `main`에 **푸시된 뒤에만** 반영된다.

**배포 완료라고 말해도 되는 조건 (전부 충족):**

1. `git push origin main` **성공** (`Your branch is up to date with 'origin/main'`)
2. 라이브 URL에서 변경이 보이는지 확인  
   - 예: [blog.sulsul.app](https://blog.sulsul.app)  
   - 새 이미지면 `https://blog.sulsul.app/assets/blog/scenes/....jpg` 가 **200**
3. 그다음에야 「배포 완료」라고 보고

푸시가 막히거나 중단되면 **「배포 안 됨. 푸시 남음」**이라고 분명히 말할 것.  
「배포합니다」로 끝내지 말 것.

### 가격 정책 (2026-08-02 변경)

**블로그에는 가격 숫자를 쓰지 않습니다.** 가격은 `sulsul.app` 한 곳에만 있습니다.

- 허용되는 표현: "개인 과외 1회($30–50)보다 적은 돈으로 매일 말하기 훈련"
- 그 다음 랜딩페이지로 링크
- 이유: 두 곳에 가격이 있으면 어긋나고, 낡은 가격을 AI가 물어다 퍼뜨림

---

## 5. 남은 일 (2026-08-05 갱신)

### 지금 상태

- 자동발행: **ON** — 매일 교재 2 + K-컬처 2, main 직배포
- 표지: 장면 풀 우선, 부족 시 DALL·E 생성
- 공개 글: 런칭·검수 글 + 이후 자동/수동 발행분 (홈에서 확인)

### 우선순위 높음

1. **자동 스케줄 첫 실행 확인**
   - [Trend K-Culture](https://github.com/sulsulkorean/sulsul_blog/actions/workflows/trend_9am.yml) / [Textbook](https://github.com/sulsulkorean/sulsul_blog/actions/workflows/textbook_9pm.yml)
   - 원하면 **Run workflow**로 수동 1회 스모크 테스트
   - 통과 0편(검색 실패·게이트)도 정상일 수 있음 — Summary 확인
   - push 후 [blog.sulsul.app](https://blog.sulsul.app)에서 새 글·표지 확인 (§4 사고 4)

2. **게이트 통과율 보고 기준 조정** (데이터 본 뒤, 한 번에 하나씩)

3. **Actions → main write 권한**  
   Settings → Actions → General → Workflow permissions → **Read and write**  
   (직배포에 필요. PR 생성 허용은 더 이상 필수는 아님)

### 우선순위 낮음

4. 프로필 사진 구도 선택 (A/B/C 중 — 현재 B 적용 중, 대표님 미확인)
5. 토픽 클러스터 전략 (관련 글끼리 묶어 내부 링크)
6. `duckduckgo-search` → 언젠가 `ddgs` 로 이전 (끊기면 트렌드 0편 = 안전한 실패)

---

## 6. 다음 세션이 지켜야 할 것

- **`.cursor/rules/ai-directives.mdc` 와 `docs/CEO_COMMUNICATION.md` 를 먼저 읽을 것.**
  특히: 대표님 보고는 쉬운 말로, URL은 반드시 하이퍼링크로, 대표님 일정·컨디션 참견 금지.
- **「배포 완료」는 §4 사고 4 조건을 전부 충족한 뒤에만.**  
  커밋만 하고 푸시·라이브 확인을 빼먹으면 안 된다. 푸시가 안 됐으면 「배포 안 됨」이라고 말할 것.
- **공개 문구를 손대면 반드시 `python3 tools/check_public_copy.py` 를 돌릴 것.**
- **예약 글을 손대면 `generate_seo_posts.validate_post`와 `npm run build`도 통과시킬 것.**
- **본문 이미지 2장을 유지할 것.** 상황 이미지와 말하기 연습 이미지를 서로 떨어진 섹션에 배치합니다.
- **글마다 표지 이미지는 주제와 맞고, 다른 글과 중복되지 않게.** 뉴스·아이돌·드라마 스틸은 무단 사용 금지(자체 장면 이미지·라이선스만).
- **고객이 읽는 글에 "우리는 ~하지 않습니다" 식 해명을 쓰지 말 것.**
  술술이 무엇인지만 쓰고, 무엇으로 오해받지 않으려는지는 쓰지 않습니다.
- **결과물이 이상하면 입력까지 거슬러 올라가 볼 것.** (§4 사고 3)
  글이 엉뚱하면 지시문만 보지 말고, 글감이 어디서 오는지 실제로 한 번 돌려서 눈으로 확인합니다.
- 결제·인증·DB 스키마 변경은 대표님 승인 후에만.

---

## 7. 확인 방법 (대표님용)

폰에서 아래를 열어 확인하실 수 있습니다.

- [블로그 홈](https://blog.sulsul.app)
- [소개 페이지](https://blog.sulsul.app/what-is-sulsul) — 가격 숫자가 없고, 앱으로 가는 링크만 있으면 정상
- [자동 발행 기록](https://github.com/sulsulkorean/sulsul_blog/actions) — 매일 돌아간 결과. Summary에 통과 n / 전체 m
- 옛 초안 PR이 남아 있으면 Close만 (이미 main에 있으면 Merge 금지)
