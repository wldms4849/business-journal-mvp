@echo off
echo ========================================
echo 사업일기 MVP - GitHub 자동 업로드 도구
echo ========================================
echo.

REM 사용자 정보 입력
set /p GITHUB_USER="GitHub 아이디를 입력하세요: "
set /p GITHUB_EMAIL="GitHub 이메일을 입력하세요: "

echo.
echo 설정 중...

REM Git 설정
git config --global user.name "%GITHUB_USER%"
git config --global user.email "%GITHUB_EMAIL%"

REM Git 초기화 (이미 있으면 무시됨)
git init

REM 모든 파일 추가
echo.
echo 파일 추가 중...
git add .

REM 커밋
echo.
echo 커밋 생성 중...
git commit -m "Initial commit: 사업일기 MVP 완성"

REM 원격 저장소 연결
echo.
echo GitHub 저장소 연결 중...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/business-journal-mvp.git

REM 업로드
echo.
echo 업로드 중...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo 완료! 
echo https://github.com/%GITHUB_USER%/business-journal-mvp
echo 위 주소에서 확인하세요!
echo ========================================
pause
