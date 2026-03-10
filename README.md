# 주식 가격 조회 프로그램

한국(KRX/NXT) 및 미국 주식의 실시간 가격과 차트를 조회하는 Python GUI 프로그램입니다.

## 실행 방법

```bash
# GUI 모드 (인수 없이 실행)
python main.py

# CLI 모드 (인수 있으면 자동으로 CLI)
python main.py 삼성전자
python main.py 005930
python main.py AAPL
```

## 주요 기능

### 종목 검색
- 한글 이름: `삼성전자`, `현대차`, `카카오` 등
- 종목 코드: `005930`, `000660` 등 6자리 숫자
- 미국 티커: `AAPL`, `TSLA`, `NVDA` 등 대문자 5자 이하
- 영문 이름: `samsung`, `kakao` 등 (yahooquery 검색)

### 종목명 자동완성
- 입력창에 글자를 입력하면 KRX 전체 상장 종목(약 2,700개)에서 이름이 포함된 종목을 드롭다운으로 최대 10개 표시
- `↓` 키로 목록 이동, `Enter` 또는 클릭으로 선택 및 즉시 검색
- 종목 목록은 실행 시 백그라운드에서 자동 로드 (`kind.krx.co.kr`)

### 가격 표시
- **장 중 (KRX OPEN)**: `₩187,900  +14,400 (+8.30%)  [KRX]`
- **장 마감 후**: `₩187,900  +14,400 (+8.30%)  [KRX 종가]`
- **NXT 시간외 거래 중**: KRX 가격 옆에 `NXT  ₩188,000  +14,500 (+8.36%)` 보라색으로 표시
- 미국 주식은 달러(`$`) 표시

### 차트
- **기간 선택**: `1M` / `3M` / `6M` / `1Y` 버튼 (기본값: 1M)
- **차트 유형**: `라인` / `캔들` 버튼으로 전환
  - 라인: 종가 기준, 상승(파랑)/하락(빨강) + 음영
  - 캔들: 양봉(초록)/음봉(빨강), 심지(고가-저가) 포함
- **이동평균선**: MA20(주황) / MA40(초록) / MA60(보라) 점선 표시
  - 데이터가 부족하면 해당 선만 자동 생략
- 기간 변경 시 자동 재조회, 차트 유형 전환은 재조회 없이 즉시 반영

## 종목 검색 로직 (우선순위)

1. 6자리 숫자 → 한국 종목 코드로 직접 사용
2. 대문자 5자 이하 ASCII → 미국 티커로 직접 사용
3. 한글/영문 이름 → KRX 상장 목록에서 검색 (정확 일치 → 부분 일치)
4. KRX에서 못 찾으면 → 네이버 검색 스크래핑 (`search.naver.com`)
5. 영문 이름 → yahooquery 검색 (한국 `.KS` 우선, 없으면 미국)

## 설치

```bash
pip install finance-datareader yahooquery beautifulsoup4 requests matplotlib pandas
```

> Python 3.10 이상 권장

## 파일 구조

```
├── main.py         # GUI / CLI 진입점, 차트 렌더링
└── stock_price.py  # 주식 데이터 조회 핵심 로직
```

### main.py
| 항목 | 설명 |
|------|------|
| `run_cli()` | argparse로 CLI 실행, 현재가 출력 |
| `run_gui()` | Tkinter GUI 실행 |
| `AutocompleteEntry` | 자동완성 드롭다운 입력창 위젯 |

### stock_price.py
| 함수 | 설명 |
|------|------|
| `get_stock_names()` | KRX 전체 종목명 목록 반환 (자동완성용) |
| `get_realtime_price(symbol)` | 네이버 polling API로 KRX + NXT 실시간 가격 반환 |
| `get_price_history(symbol, days)` | FinanceDataReader로 가격 히스토리 DataFrame 반환 |
| `get_stock_price(symbol)` | 현재가 단일값 반환 (CLI용) |
