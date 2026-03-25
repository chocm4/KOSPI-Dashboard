# KOSPI 분석 대시보드

피보나치 되돌림 + 강세/약세장 판단 모형을 자동으로 업데이트하는 웹 대시보드입니다.  
**yfinance → GitHub Actions → GitHub Pages** 파이프라인으로 타 PC에서도 URL 하나로 접근 가능합니다.

---

## 📁 파일 구조

```
your-repo/
├── docs/
│   ├── index.html          ← 대시보드 (GitHub Pages 서빙)
│   └── kospi_data.json     ← yfinance가 생성하는 데이터 (자동 생성)
├── .github/
│   └── workflows/
│       └── update_kospi.yml ← 매일 자동 실행 스케줄
├── update_data.py           ← 데이터 수집 스크립트
└── README.md
```

---

## 🚀 배포 방법 (5단계)

### Step 1. GitHub 저장소 생성
1. [github.com](https://github.com) → **New repository**
2. 이름 예: `kospi-dashboard`
3. **Public** 으로 설정 (GitHub Pages 무료 사용)

### Step 2. 파일 업로드
위 파일들을 저장소에 올립니다.

```bash
git clone https://github.com/YOUR_USERNAME/kospi-dashboard.git
cd kospi-dashboard

# 파일 복사 후
git add .
git commit -m "init: KOSPI 대시보드 초기 셋업"
git push
```

### Step 3. GitHub Pages 활성화
1. 저장소 → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / Folder: `/docs`
4. **Save** 클릭
5. 잠시 후 `https://YOUR_USERNAME.github.io/kospi-dashboard/` URL 생성됨

### Step 4. 첫 데이터 생성 (수동 트리거)
1. 저장소 → **Actions** 탭
2. **KOSPI 데이터 자동 업데이트** 워크플로우 클릭
3. **Run workflow** 버튼 클릭
4. 약 1~2분 후 `docs/kospi_data.json` 자동 생성 + 커밋됨

### Step 5. 접속 확인
```
https://YOUR_USERNAME.github.io/kospi-dashboard/
```
이 URL 하나로 어디서든 최신 KOSPI 데이터 대시보드 확인 가능!

---

## ⏰ 자동 업데이트 스케줄

| 항목 | 내용 |
|---|---|
| 실행 시간 | 평일(월~금) 오후 4시 30분 KST |
| 수집 기간 | 과거 약 4년치 (1500일) |
| 데이터 소스 | Yahoo Finance (`^KS11`) |
| 커밋 여부 | 데이터 변경 시에만 자동 커밋 |

> 수동 실행: Actions → Run workflow 버튼

---

## 🛠 로컬 실행 방법

```bash
# 의존성 설치
pip install yfinance pandas

# 데이터 수집 (docs/kospi_data.json 생성)
python update_data.py

# 로컬 서버 실행 (파일:// 방식은 fetch 차단될 수 있으므로)
cd docs
python -m http.server 8080
# 브라우저에서 http://localhost:8080 접속
```

---

## 📊 대시보드 기능

### 피보나치 되돌림
- 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100% 레벨
- 되돌림(고→저 반등) / 확장(저→고 연장) 선택
- 고점/저점: 자동·최근52주·수동 지정
- 현재 구간(지지/저항) 자동 판별

### 강세/약세장 종합 판단 (7개 지표)
| 지표 | 설명 | 가중치 |
|---|---|---|
| 20% 룰 | 고점 대비 낙폭 | ×1 |
| 현재가 vs MA20 | 단기 추세 | ×1 |
| 현재가 vs MA60 | 중기 추세 | ×1 |
| 현재가 vs MA200 | 장기 추세 | **×2** |
| MA20 vs MA60 | 단·중기 배열 | ×1 |
| MA60 vs MA200 | 골든/데드크로스 | ×1 |
| RSI(14) | 모멘텀 | ×1 |

- **≥65%** → 강세장 🐂
- **≤35%** → 약세장 🐻
- 그 외 → 중립/전환 구간 ⚖️

---

## ❓ FAQ

**Q. kospi_data.json이 없을 때는?**  
A. 내장 샘플 데이터로 자동 표시됩니다. GitHub Actions를 한 번 실행하면 실제 데이터로 전환됩니다.

**Q. 데이터 수집 기간을 바꾸고 싶어요.**  
A. `update_data.py`의 `PERIOD_DAYS` 값을 수정하거나,  
Actions → Run workflow → `period_days` 입력란에 원하는 일수를 넣어 실행하세요.

**Q. 비공개(Private) 저장소로 운영하고 싶어요.**  
A. GitHub Pro 또는 조직 계정이 있다면 Private 저장소에서도 Pages 사용 가능합니다.  
무료 계정은 Public 저장소만 지원합니다.
