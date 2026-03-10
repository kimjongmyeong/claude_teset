# 주식 가격 조회 프로그램 개발 과정

## 개요
이 프로그램은 사용자가 주식 종목의 심볼 또는 이름을 입력하면 현재 가격을 조회하는 Python 스크립트입니다. yfinance와 yahooquery 라이브러리를 사용합니다.

## 개발 단계

### 1. 초기 버전 (yfinance만 사용)
- 기능: 심볼 입력 시 가격 출력 (미국 주식 중심).
- 코드: `get_stock_price(symbol)` 함수 정의.
- 문제: main 블록 없음 → 실행 시 반응 없음.

### 2. main 블록 추가
- 수정: `if __name__ == "__main__":` 블록 추가로 사용자 입력 받음.
- 결과: 심볼 입력 시 가격 출력 가능.

### 3. 한국 주식 지원
- 수정: 심볼이 6자리 숫자면 `.KS` 추가.
- 결과: "005930" 입력 시 삼성전자 가격 출력.

### 4. 종목 이름 입력 지원 (STOCK_MAPPING)
- 추가: 딕셔너리로 이름 ↔ 심볼 매핑 (예: "삼성전자" → "005930.KS").
- 결과: 이름 입력 시 가격 출력.

### 5. 모든 주식 검색 가능 (yahooquery)
- 변경: STOCK_MAPPING 제거, yahooquery로 이름 검색.
- 기능: 이름 입력 시 자동 심볼 검색 (한국 주식 .KS 우선).
- 결과: "삼성전자" 또는 "한화" 입력 시 가격 출력.

### 6. 통화 표시 개선
- 수정: 한국 주식(.KS)은 ₩, 미국 주식은 $로 표시.
- 결과: 정확한 통화 출력.

### 7. 오류 처리 강화
- 추가: 검색 실패 시 심볼 입력 유도.
- 결과: 안정적인 실행.

## 최종 코드 (stock_price.py)
```python
import yfinance as yf
from yahooquery import search

def get_stock_price(symbol_or_name: str) -> float:
    # ... (전체 코드 생략, 파일 참조)
```

## 사용 방법
1. 라이브러리 설치: `pip install yfinance yahooquery`
2. 실행: `python stock_price.py`
3. 입력: 심볼 또는 이름 (예: "AAPL", "삼성전자")
4. 출력: 현재 가격 (통화 표시)

## 향후 개선
- 더 정확한 검색 (영어 변환).
- GUI 추가 (Tkinter).
- 실시간 데이터 지원.
```
