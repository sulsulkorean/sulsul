#!/bin/bash
# 이 스크립트는 SULSUL 블로그 레포지토리의 변경사항(새로 생성된 글 등)을 GitHub로 푸시합니다.

cd "$(dirname "$0")"

echo "🚀 GitHub로 SULSUL 블로그 업데이트를 시작합니다..."

# 변경사항이 있는지 확인하여 커밋
if [[ -n $(git status -s) ]]; then
  git add .
  COMMIT_MSG="Add new programmatic seo posts - $(date +'%Y-%m-%d %H:%M:%S')"
  git commit -m "$COMMIT_MSG"
else
  echo "✅ 새로 추가된 파일은 없지만, 아직 전송되지 않은 내역이 있는지 확인 후 푸시합니다."
fi


# 메인 브랜치로 푸시 (원격 저장소 이름이 origin 이고 브랜치가 main 이라고 가정)
git push origin main

echo "🎉 성공적으로 GitHub에 푸시되었습니다! Vercel에서 자동으로 배포를 시작합니다."
