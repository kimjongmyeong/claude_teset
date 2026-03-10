# 프로젝트 개요: 주식 가격 조회 프로그램

## 프로젝트 구조

```
d:\Claude\
├── main.py                        # 진입점 (CLI / GUI 모드)
├── stock_price.py                 # 핵심 로직 (주식 가격 조회)
├── stock_price_development.md     # 개발 과정 문서
├── AI_MASTER_성능시험적용지표.docx  # 참고 문서
└── .venv/                         # Python 가상 환경
```

---

## 파일별 설명

### [main.py](main.py)

진입점 파일. 실행 인수 유무에 따라 CLI 또는 GUI 모드로 분기합니다.

**주요 함수:**

| 함수 | 설명 |
|------|------|
| `run_cli()` | argparse로 종목 심볼을 인수로 받아 가격 출력 |
| `run_gui()` | Tkinter로 입력창과 버튼을 제공하는 GUI 실행 |
| `main()` | `sys.argv` 길이로 CLI/GUI 분기 |

**실행 방법:**
```bash
# CLI 모드
python main.py AAPL

# GUI 모드 (인수 없이 실행)
python main.py
```

---

### [stock_price.py](stock_price.py)

주식 가격 조회 핵심 모듈.

**의존 라이브러리:**
- `FinanceDataReader` - 주식 가격 조회
- `beautifulsoup4` + `requests` - 네이버 검색 스크래핑으로 한글 종목 코드 조회
- `yahooquery` - 영문 이름으로 심볼 검색 (fallback)

**주요 함수:**

#### `_get_krx_listing()`

`fdr.StockListing('KRX')`를 세션 시작 시 한 번만 로드, 메모리에 유지합니다.

#### `_search_naver_stock(name: str) -> str | None`

`search.naver.com`을 스크래핑하여 한글/영문 이름으로 종목 코드를 조회합니다.

#### `_resolve_symbol(symbol_or_name: str) -> tuple[str, str]`

입력값을 실제 심볼과 시장으로 변환합니다.

| 입력 형태 | 처리 방식 |
|---|---|
| 6자리 숫자 (예: `005930`) | 한국 주식 코드로 직접 사용 |
| ASCII 대문자 5자 이하 (예: `AAPL`) | 미국 티커로 직접 사용 |
| 한글/영문 이름 (예: `삼성전자`, `samsung`) | 네이버 검색 스크래핑으로 코드 조회 |
| 영문 이름 (fallback) | `yahooquery.search()`로 검색 |

#### `get_stock_price(symbol_or_name: str) -> tuple[float, str]`

종목 심볼 또는 이름을 받아 현재 가격과 심볼을 반환합니다.

**로직 흐름:**
1. `_resolve_symbol()`로 심볼 확보
2. 최근 7일치 데이터 조회: `fdr.DataReader(symbol, start, end)`
3. `Close` 열 마지막 값 반환

**통화 표시:**
- 심볼이 숫자(한국 주식) → 원화(`₩`)
- 그 외 → 달러(`$`)

**오류 처리:**
- 종목 검색 실패 시 `ValueError` 발생
- 데이터 없을 시 `ValueError` 발생

**단독 실행 예시:**
```bash
python stock_price.py
# 입력: 삼성전자
# 출력: 005930의 현재 가격: ₩83,000
```

---

### [stock_price_development.md](stock_price_development.md)

개발 단계별 히스토리 문서.

| 단계 | 변경 내용 |
|------|----------|
| 1 | yfinance만 사용하는 초기 버전 |
| 2 | `__main__` 블록 추가 |
| 3 | 한국 주식 지원 (6자리 숫자 → `.KS` 추가) |
| 4 | 딕셔너리 기반 이름↔심볼 매핑 |
| 5 | yahooquery로 범용 이름 검색으로 전환 |
| 6 | 통화 표시 개선 (₩/$ 분기) |
| 7 | 오류 처리 강화 |

---

## 설치 및 환경

**필요 라이브러리:**
```bash
pip install finance-datareader
```

**가상 환경:** `.venv/` (Python 가상환경 디렉터리)

**주요 설치된 패키지 (`.venv` 기준):**
- `finance-datareader 0.9.102`
- `pandas 2.3.3`
- `numpy 2.2.6`
- `requests 2.32.5`
- `lxml 6.0.2`

---

## 향후 개선 과제

- 영어 이름으로도 한국 주식 검색 가능하도록 개선
- GUI 기능 확장 (검색 히스토리, 즐겨찾기 등)
- 실시간 데이터 스트리밍 지원
