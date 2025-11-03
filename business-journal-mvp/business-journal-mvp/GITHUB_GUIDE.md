# 🐱 GitHub에 프로젝트 올리기 - 초보자 가이드

이 가이드는 **개발을 전혀 모르는 분**도 따라할 수 있도록 작성되었습니다.
천천히 하나씩 따라오세요! 😊

---

## 📋 준비물

1. **컴퓨터** (Windows, Mac 모두 가능)
2. **인터넷 연결**
3. **이메일 주소**

---

## 1단계: GitHub 계정 만들기 (5분)

### 이미 GitHub 계정이 있다면 → 2단계로 바로 가세요!

1. 웹브라우저에서 https://github.com 접속
2. 우측 상단 **Sign up** (회원가입) 클릭
3. 이메일 입력 → 비밀번호 만들기 → 사용자명 입력
4. 이메일로 온 인증 코드 입력
5. 완료! ✅

---

## 2단계: 새 Repository(저장소) 만들기 (3분)

**Repository(리포지토리)**는 프로젝트를 보관하는 "폴더"라고 생각하시면 됩니다.

1. GitHub에 로그인
2. 우측 상단 **+** 버튼 클릭 → **New repository** 선택

3. 다음 정보 입력:
   ```
   Repository name: business-journal-mvp
   Description: 사업일기 - 로컬 사업자를 위한 투명한 실행-로그-학습 SaaS
   Public 또는 Private 선택 (Public = 누구나 볼 수 있음, Private = 나만 볼 수 있음)
   
   ✅ Add a README file 체크 안 함 (이미 우리가 만들었으니까)
   ✅ Add .gitignore 체크 안 함 (이미 있음)
   ✅ Choose a license: MIT License 선택 (선택사항)
   ```

4. **Create repository** 버튼 클릭
5. 완료! 이제 빈 저장소가 생겼습니다 ✅

---

## 3단계: Git 설치하기 (10분)

**Git**은 코드를 업로드하기 위한 "배달 트럭" 같은 프로그램입니다.

### Windows 사용자:
1. https://git-scm.com/download/win 접속
2. **Click here to download** 클릭
3. 다운로드된 파일 실행
4. 계속 **Next** 누르기 (기본 설정 그대로 OK)
5. **Finish** → 완료!

### Mac 사용자:
1. **Spotlight** (⌘ + Space) 열기
2. "Terminal" 입력 → Enter
3. 다음 명령어 입력하고 Enter:
   ```bash
   git --version
   ```
4. 이미 설치되어 있으면 버전이 나옵니다!
5. 없다면: https://git-scm.com/download/mac 에서 다운로드

---

## 4단계: 프로젝트 파일 준비하기 (5분)

1. 이 프로젝트 폴더(`business-journal-mvp`)를 **바탕화면**에 복사
   - 위치: `/mnt/user-data/outputs/business-journal-mvp`

2. 폴더 안에 다음 파일들이 있는지 확인:
   ```
   ✅ README.md
   ✅ backend/ 폴더
   ✅ frontend/ 폴더
   ✅ docs/ 폴더
   ✅ ops/ 폴더
   ```

---

## 5단계: Git으로 업로드하기 (15분)

### Windows 사용자:

1. 바탕화면의 `business-journal-mvp` 폴더에서 **마우스 우클릭**
2. **Git Bash Here** 선택 (검은 창이 열림)

### Mac 사용자:

1. **Terminal** 열기 (⌘ + Space → "Terminal")
2. 다음 명령어 입력:
   ```bash
   cd ~/Desktop/business-journal-mvp
   ```

### 모든 사용자 (이제부터 동일):

검은 창(Terminal 또는 Git Bash)에서 **하나씩** 입력하고 Enter:

```bash
# 1. Git 초기화
git init

# 2. 내 이름 설정 (한 번만 하면 됨)
git config --global user.name "당신의이름"
git config --global user.email "당신의이메일@example.com"

# 3. 모든 파일 추가
git add .

# 4. 커밋 (저장) 만들기
git commit -m "Initial commit: 사업일기 MVP 완성"

# 5. GitHub 저장소 연결
git remote add origin https://github.com/당신의깃허브아이디/business-journal-mvp.git

# 6. 업로드!
git branch -M main
git push -u origin main
```

### 🔑 중요!
5번 명령어에서 `당신의깃허브아이디`를 **실제 GitHub 아이디**로 바꾸세요!

예시:
```bash
# 만약 GitHub 아이디가 "hongildong" 이라면:
git remote add origin https://github.com/hongildong/business-journal-mvp.git
```

### 비밀번호 입력 창이 나오면:
- **Username**: GitHub 아이디
- **Password**: GitHub 비밀번호 (안 보여도 정상, 그냥 입력하고 Enter)

> 💡 **참고**: 최근 GitHub는 비밀번호 대신 **Personal Access Token**을 사용합니다.
> 비밀번호가 안 된다면 → 아래 "Personal Access Token 만들기" 섹션 참조

---

## 6단계: 확인하기 (1분)

1. 웹브라우저에서 https://github.com/당신의아이디/business-journal-mvp 접속
2. 모든 파일이 보이나요? 🎉
3. 성공입니다!

---

## 🔐 Personal Access Token 만들기 (선택사항)

비밀번호가 거부되면 이 방법을 사용하세요:

1. GitHub 로그인
2. 우측 상단 프로필 사진 클릭 → **Settings**
3. 왼쪽 메뉴 맨 아래 **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**
6. 다음 설정:
   - Note: `business-journal-upload`
   - Expiration: 90 days
   - ✅ repo 체크
7. **Generate token** 클릭
8. 나온 토큰(긴 영문+숫자) **복사** → **안전한 곳에 저장** (다시 안 보여줌!)
9. Git push 할 때 비밀번호 대신 이 토큰을 입력

---

## 🆘 문제 해결

### "git: command not found"
→ Git이 설치 안 됨. 3단계로 돌아가서 Git 설치

### "permission denied"
→ 비밀번호 틀림. Personal Access Token 사용해보기

### "repository not found"
→ 5번 명령어에서 GitHub 아이디 확인

### 그래도 안 되면?
→ 아래 "쉬운 방법: GitHub Desktop 사용" 참조

---

## 🎨 더 쉬운 방법: GitHub Desktop 사용

Git 명령어가 어려우면 **프로그램**으로 할 수 있습니다!

### 1. GitHub Desktop 설치
- https://desktop.github.com 에서 다운로드
- 설치 후 GitHub 계정으로 로그인

### 2. 프로젝트 추가
1. **File** → **Add local repository**
2. `business-journal-mvp` 폴더 선택
3. **Add repository**

### 3. 업로드
1. 왼쪽 하단에 모든 변경사항 보임
2. **Summary** 에 "Initial commit" 입력
3. **Commit to main** 클릭
4. 상단 **Publish repository** 클릭
5. 완료! ✅

---

## ✅ 체크리스트

업로드 전:
- [ ] GitHub 계정 있음
- [ ] Git 설치됨
- [ ] 프로젝트 폴더 준비됨

업로드 후:
- [ ] GitHub에서 파일 확인됨
- [ ] README.md가 잘 보임
- [ ] 폴더 구조가 올바름

---

## 🎉 축하합니다!

이제 여러분의 프로젝트가 GitHub에 올라갔습니다!

### 다른 사람과 공유하려면:
1. 브라우저 주소창의 URL 복사
2. 친구에게 보내기
   ```
   https://github.com/당신의아이디/business-journal-mvp
   ```

### 코드 수정하고 다시 올리려면:
```bash
git add .
git commit -m "업데이트 내용 설명"
git push
```

---

## 📞 더 도움이 필요하면?

- GitHub 공식 가이드: https://docs.github.com/ko
- Git 기초 튜토리얼: https://git-scm.com/book/ko/v2
- 또는 이 프로젝트의 Issues에 질문 남기기!

---

**만든 사람이 개발자가 아니어도 괜찮습니다!** 
천천히 따라하면 누구나 할 수 있어요 💪
