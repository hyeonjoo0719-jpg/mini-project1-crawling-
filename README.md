# 칵테일 통합 검색 Flask 프로젝트

TheCocktailDB API를 이용해 칵테일 이름과 재료를 검색하고,
검색 결과를 웹 화면에 출력하며 CSV로 저장하는 프로젝트입니다.

## 주요 기능

- 칵테일 이름 검색
- 재료 검색
- 이름 + 재료 통합 검색
- 한글 재료명 일부 지원
- 무알콜 검색
- 칵테일 이미지, 분류, 사용 잔, 재료, 제조법 출력
- 검색 결과 CSV 저장
- 전체 칵테일 데이터 CSV 저장

## 폴더 구성

```text
cocktail_search_project/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    └── style.css
```

## 실행 방법

### 1. 가상환경 생성

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. Flask 실행

```bash
python app.py
```

### 4. 브라우저 접속

```text
http://127.0.0.1:5000
```

## 검색 예시

- 보드카
- 진
- 레몬
- Margarita
- 무알콜

## 참고

- 데이터 제공: TheCocktailDB API
- 인터넷 연결이 필요합니다.
- 전체 CSV 저장은 A부터 Z까지 데이터를 수집하므로 몇 초 정도 걸릴 수 있습니다.
