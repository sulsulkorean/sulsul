#!/bin/bash
# 이 스크립트는 SULSUL 블로그 레포지토리의 변경사항(새로 생성된 글 등)을 GitHub로 푸시합니다.

cd "$(dirname "$0")"

echo "🚀 GitHub로 SULSUL 블로그 업데이트를 시작합니다..."

# 변경사항이 있는지 확인
if [[ -z $(git status -s) ]]; then
  echo "✅ 추가되거나 변경된 파일이 없습니다."
  exit 0
fi

# 모든 변경사항 추가
git add .

# 현재 날짜 및 시간으로 커밋 메시지 생성
COMMIT_MSG="Add new programmatic seo posts - $(date +'%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# 메인 브랜치로 푸시 (원격 저장소 이름이 origin 이고 브랜치가 main 이라고 가정)
git push origin main

echo "🎉 성공적으로 GitHub에 푸시되었습니다! Vercel에서 자동으로 배포를 시작합니다."
