import os
import glob
import time
import argparse
import subprocess
import sys
from datetime import datetime
from openai import OpenAI

# ---------------------------------------------------------
# 1. 자동 패키지 설치 로직 (duckduckgo-search)
# ---------------------------------------------------------
def install_package(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        print(f"📦 패키지 {package} 가 없습니다. 자동 설치를 진행합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package('duckduckgo-search')
from duckduckgo_search import DDGS

# ---------------------------------------------------------
# 2. 설정
# ---------------------------------------------------------
client = OpenAI() 
MODEL = "gpt-4o-mini"
# GitHub Actions 등 클라우드 환경을 위해 상대 경로 사용
OBSIDIAN_VAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "obsidian_data")
LIBRARY_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "3.Library")
VOICE_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "2.Voice")
BLOG_POSTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_posts")

# ---------------------------------------------------------
# 3. 헬퍼 함수 (읽기 및 재시도 로직)
# ---------------------------------------------------------
def read_markdown_files(directory):
    content = ""
    if not os.path.exists(directory):
        return content
    for filepath in glob.glob(os.path.join(directory, "*.md")):
        with open(filepath, 'r', encoding='utf-8') as f:
            content += f"\n\n--- Source: {os.path.basename(filepath)} ---\n"
            content += f.read()
    return content

def api_call_with_retry(messages, temperature=0.7, max_retries=5):
    """OpenAI API 통신 튕김 방지 (Exponential Backoff)"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            wait_time = (2 ** attempt) + 2
            print(f"⚠️ API 통신 지연 발생. {wait_time}초 후 재시도합니다... (에러: {e})")
            time.sleep(wait_time)
    raise Exception("API 통신이 여러 번 실패했습니다. 인터넷 연결을 확인해주세요.")

# ---------------------------------------------------------
# 4. 키워드 생성 (Trend vs Textbook)
# ---------------------------------------------------------
def fetch_trend_news(count):
    """최신 K-Pop, K-Drama 뉴스를 검색하여 키워드와 컨텍스트를 만듭니다."""
    print("🌍 실시간 최신 K-Trend 뉴스 검색 중...")
    # duckduckgo-search 라이브러리로 'k-pop', 'k-drama' 등 검색
    results = DDGS().text("K-Pop OR K-Drama OR BTS OR Netflix Korea", max_results=count)
    keywords = []
    for r in results:
        keywords.append({
            "title": r.get('title', ''),
            "snippet": r.get('body', ''),
            "link": r.get('href', '')
        })
    return keywords

def generate_keywords(library_content, count, mode):
    if mode == 'trend':
        return fetch_trend_news(count)
    
    # Textbook mode
    print(f"🤖 교재 기반 키워드 {count}개 추출 중...")
    prompt = f"""
너는 SULSUL 앱의 전문 SEO 콘텐츠 마케터야. 
아래 [SULSUL 교재 원문]을 분석해서, 구글에서 외국인들이 검색할 만한 SEO 최적화 롱테일 키워드 {count}개를 영문으로 뽑아줘.
[SULSUL 교재 원문 요약]: {library_content[:10000]}
결과는 부가 설명 없이 1. 2. 3. 번호가 매겨진 키워드 목록만 출력해줘.
"""
    keywords_text = api_call_with_retry([{"role": "user", "content": prompt}])
    keywords_list = [line.split('. ', 1)[1].strip() for line in keywords_text.split('\n') if '. ' in line]
    return keywords_list[:count]

# ---------------------------------------------------------
# 5. 블로그 포스트 생성
# ---------------------------------------------------------
def generate_blog_post(keyword_data, library_content, voice_content, mode):
    if mode == 'trend':
        news = keyword_data
        target_keyword = news['title']
        print(f"✍️ [트렌드] '{target_keyword}' 뉴스로 포스트 작성 중...")
        topic_context = f"최신 뉴스 기사:\n제목: {news['title']}\n내용: {news['snippet']}\n\n이 최신 글로벌 뉴스를 바탕으로, 자연스럽게 한국어 학습(문법, 회화, 단어 등)과 연결되는 유익한 블로그 글을 작성해줘."
    else:
        target_keyword = keyword_data
        print(f"✍️ [교재] '{target_keyword}' 키워드로 포스트 작성 중...")
        topic_context = f"[타겟 키워드]: {target_keyword}"

    prompt = f"""
너는 SULSUL 앱의 트렌디하고 세련된 콘텐츠 마케터야.
아래 컨텍스트와 [교재 데이터], [대표님 말투(Voice)]를 참고해서, 주어진 주제에 대한 1,500자 이상의 유익한 SEO 최적화 블로그 글을 영어로 작성해 줘.

{topic_context}

[대표님 말투(Voice) 예시]:
{voice_content}

[교재 데이터]:
{library_content[:10000]}

작성 가이드:
1. 글의 톤앤매너는 [대표님 말투]와 완벽하게 일치해야 해. 친절하지만 전문적인 톤을 유지할 것.
2. 구글 SEO를 위해 제목(H1), 소제목(H2, H3), 불릿 포인트 등을 적극 활용해 가독성을 높일 것.
3. **[필수]** 시각적 재미를 위해 글의 본문 중간(소제목과 소제목 사이)에 아래의 이미지 마크다운 코드를 반드시 1개 이상 분산 삽입해:
   - `![SULSUL Mascot](/assets/blog/mascot.png)`
   - `![SULSUL Book](/assets/blog/book_cover.png)`
4. **[필수]** 글의 맨 마지막 결론 부분에는 독자가 당장 앱을 설치하고 싶도록 강렬한 CTA(Call To Action) 멘트와 함께, 아래 마크다운을 통째로 복사해서 삽입해:
   ```markdown
   Ready to master Korean like a native? 
   Try the **SULSUL App** completely free for 30 days and unlock your full potential!
   
   [![SULSUL App](/assets/blog/app_landing.png)](https://sulsul.app)
   ```
5. 출력은 완벽한 Markdown 포맷이어야 하며, Next.js 블로그용 Frontmatter를 최상단에 포함해.

Frontmatter 예시:
---
title: "The Ultimate Guide to: {target_keyword.replace('"', '')}"
excerpt: "A brief 2 sentence summary of this post."
coverImage: "/assets/blog/app_landing.png"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
author:
  name: Yona
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/app_landing.png"
---

여기서부터 마크다운 본문을 시작해.
"""
    return api_call_with_retry([{"role": "user", "content": prompt}], temperature=0.8)

# ---------------------------------------------------------
# 6. 메인 실행 함수
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Programmatic SEO 콘텐츠 공장")
    parser.add_argument("--mode", choices=["textbook", "trend"], default="textbook", help="생성 모드 (textbook 또는 trend)")
    parser.add_argument("--count", type=int, default=20, help="생성할 포스트 개수 (권장: 20개)")
    args = parser.parse_args()

    print(f"🚀 Programmatic SEO 콘텐츠 공장 가동 시작... (모드: {args.mode}, 목표 개수: {args.count}개)\n")
    
    os.makedirs(BLOG_POSTS_DIR, exist_ok=True)
    
    library_content = read_markdown_files(LIBRARY_DIR)
    voice_content = read_markdown_files(VOICE_DIR)
    
    if not library_content:
        print(f"⚠️ 경고: {LIBRARY_DIR} 에 마크다운 파일이 없습니다.")
    if not voice_content:
        print(f"⚠️ 경고: {VOICE_DIR} 에 마크다운 파일이 없습니다.")
        
    keywords_or_news = generate_keywords(library_content, args.count, args.mode)
    
    print("\n🎯 작업 목록:")
    for i, item in enumerate(keywords_or_news, 1):
        if args.mode == 'trend':
            print(f"{i}. [뉴스] {item['title']}")
        else:
            print(f"{i}. [키워드] {item}")
    print("\n")
    
    for item in keywords_or_news:
        post_content = generate_blog_post(item, library_content, voice_content, args.mode)
        
        # 파일명 생성
        title_for_filename = item['title'] if args.mode == 'trend' else item
        safe_filename = title_for_filename.lower().replace(" ", "-").replace("?", "").replace("!", "")
        safe_filename = "".join(c for c in safe_filename if c.isalnum() or c == '-')
        
        # 이름이 너무 길면 자르기
        if len(safe_filename) > 50:
            safe_filename = safe_filename[:50].rstrip('-')
            
        filepath = os.path.join(BLOG_POSTS_DIR, f"{safe_filename}.md")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(post_content)
            
        print(f"✅ 생성 완료: {filepath}")
        
    print(f"\n🎉 총 {len(keywords_or_news)}개의 SEO 블로그 포스트 생성이 완료되었습니다!")
    print("💡 Vercel 배포를 위해 터미널에 './push_to_blog.sh' 를 실행하세요.")

if __name__ == "__main__":
    main()
