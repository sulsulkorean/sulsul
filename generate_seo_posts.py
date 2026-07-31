import os
import glob
import time
from openai import OpenAI
from datetime import datetime

# --- 설정 ---
# OpenAI API 키는 환경 변수 OPENAI_API_KEY 에 설정되어 있어야 합니다.
client = OpenAI() 
MODEL = "gpt-4o-mini"

# 경로 설정 (추후 대표님이 알려주실 Obsidian 경로로 업데이트 예정)
OBSIDIAN_VAULT_PATH = "/Users/yona/Documents/Obsidian Vault"
LIBRARY_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "3.Library")
VOICE_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "2.Voice")

# Next.js 블로그의 포스트 폴더 (현재는 sulsul-blog/_posts)
# 이 폴더를 Obsidian의 Repurposed 폴더로 사용할 것입니다.
BLOG_POSTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_posts")

def read_markdown_files(directory):
    """지정된 디렉토리의 모든 마크다운 파일 내용을 읽어옵니다."""
    content = ""
    if not os.path.exists(directory):
        return content
    
    for filepath in glob.glob(os.path.join(directory, "*.md")):
        with open(filepath, 'r', encoding='utf-8') as f:
            content += f"\n\n--- Source: {os.path.basename(filepath)} ---\n"
            content += f.read()
    return content

def generate_keywords(library_content):
    """교재 내용을 기반으로 타겟팅할 SEO 키워드 10개를 뽑습니다."""
    print("🤖 1단계: 검색량이 많은 한국어 학습 SEO 키워드 10개 추출 중...")
    
    prompt = f"""
너는 SULSUL 앱의 전문 SEO 콘텐츠 마케터야. 
아래 [SULSUL 교재 원문]을 분석해서, 구글에서 외국인들이 '한국어 학습 고민'과 관련하여 자주 검색할 만한 SEO 최적화 롱테일 키워드 10개를 영문으로 뽑아줘.

[SULSUL 교재 원문 요약/발췌]:
{library_content[:15000]} # 토큰 제한 방지용 일부 자르기

결과는 부가 설명 없이 1. 2. 3. 번호가 매겨진 키워드 목록만 출력해줘.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    keywords_text = response.choices[0].message.content
    keywords = [line.split('. ', 1)[1].strip() for line in keywords_text.split('\n') if '. ' in line]
    return keywords

def generate_blog_post(keyword, library_content, voice_content):
    """특정 키워드에 대해 블로그 포스트(Markdown)를 생성합니다."""
    print(f"✍️ 2단계: '{keyword}' 키워드로 포스트 작성 중...")
    
    prompt = f"""
너는 SULSUL 앱의 콘텐츠 마케터야.
아래 [교재 데이터]와 [대표님 말투(Voice)]를 참고해서, 주어진 키워드에 대한 1,500자 이상의 유익한 SEO 최적화 블로그 글을 영어로 작성해 줘.

[타겟 키워드]: {keyword}

[대표님 말투(Voice) 예시]:
{voice_content}

[교재 데이터]:
{library_content[:15000]}

작성 가이드:
1. 글의 톤앤매너는 [대표님 말투]와 완벽하게 일치해야 해. 친근하고, 전문적이며, 자연스럽게.
2. 구글 SEO를 위해 제목(H1), 소제목(H2, H3), 불릿 포인트 등을 적절히 활용해.
3. 글의 마지막에는 자연스럽게 SULSUL 앱을 다운로드하거나 30일 Premium 체험을 유도하는 문구와 링크(sulsul.app)를 넣어줘.
4. 출력은 완벽한 Markdown 포맷이어야 하며, Next.js 블로그 템플릿용 Frontmatter(title, excerpt, coverImage, date, author 등)를 최상단에 포함해야 해.
coverImage는 "/assets/blog/dynamic-routing/cover.jpg" 로 임의 지정하고, author name은 "Yona", picture는 "/assets/blog/authors/jj.jpeg" 로 통일해.

Frontmatter 예시:
---
title: "The Ultimate Guide to: {keyword}"
excerpt: "A brief 2 sentence summary here."
coverImage: "/assets/blog/dynamic-routing/cover.jpg"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
author:
  name: Yona
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

여기서부터 마크다운 본문을 시작해.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    
    return response.choices[0].message.content

def main():
    print("🚀 Programmatic SEO 콘텐츠 공장 가동 시작...\n")
    
    if not OBSIDIAN_VAULT_PATH:
         print("❌ 에러: OBSIDIAN_VAULT_PATH가 설정되지 않았습니다. 스크립트 상단의 경로를 수정해주세요.")
         return

    os.makedirs(BLOG_POSTS_DIR, exist_ok=True)
    
    library_content = read_markdown_files(LIBRARY_DIR)
    voice_content = read_markdown_files(VOICE_DIR)
    
    if not library_content:
        print(f"⚠️ 경고: {LIBRARY_DIR} 에 마크다운 파일이 없습니다.")
    if not voice_content:
        print(f"⚠️ 경고: {VOICE_DIR} 에 마크다운 파일이 없습니다.")
        
    keywords = generate_keywords(library_content)
    print("\n🎯 타겟 키워드 10개 추출 완료:")
    for i, kw in enumerate(keywords, 1):
        print(f"{i}. {kw}")
    print("\n")
    
    for kw in keywords:
        post_content = generate_blog_post(kw, library_content, voice_content)
        
        # 파일명 생성 (공백을 하이픈으로, 소문자로)
        safe_filename = kw.lower().replace(" ", "-").replace("?", "").replace("!", "")
        safe_filename = "".join(c for c in safe_filename if c.isalnum() or c == '-')
        
        filepath = os.path.join(BLOG_POSTS_DIR, f"{safe_filename}.md")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(post_content)
            
        print(f"✅ 생성 완료: {filepath}")
        
    print("\n🎉 모든 SEO 블로그 포스트 생성이 완료되었습니다! Vercel 배포를 위해 push_to_blog.sh 를 실행하세요.")

if __name__ == "__main__":
    main()
