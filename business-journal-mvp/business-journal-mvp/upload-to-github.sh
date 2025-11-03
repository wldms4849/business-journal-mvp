#!/bin/bash

echo "========================================"
echo "사업일기 MVP - GitHub 자동 업로드 도구"
echo "========================================"
echo ""

# 사용자 정보 입력
read -p "GitHub 아이디를 입력하세요: " GITHUB_USER
read -p "GitHub 이메일을 입력하세요: " GITHUB_EMAIL

echo ""
echo "설정 중..."

# Git 설정
git config --global user.name "$GITHUB_USER"
git config --global user.email "$GITHUB_EMAIL"

# Git 초기화 (이미 있으면 무시됨)
git init

# 모든 파일 추가
echo ""
echo "파일 추가 중..."
git add .

# 커밋
echo ""
echo "커밋 생성 중..."
git commit -m "Initial commit: 사업일기 MVP 완성"

# 원격 저장소 연결
echo ""
echo "GitHub 저장소 연결 중..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$GITHUB_USER/business-journal-mvp.git"

# 업로드
echo ""
echo "업로드 중..."
git branch -M main
git push -u origin main

echo ""
echo "========================================"
echo "완료!"
echo "https://github.com/$GITHUB_USER/business-journal-mvp"
echo "위 주소에서 확인하세요!"
echo "========================================"
