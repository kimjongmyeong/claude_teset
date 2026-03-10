# 주식 가격 조회 프로그램

한국(KRX/NXT) 및 미국 주식의 실시간 가격과 차트를 조회하는 Python GUI 프로그램입니다.

## 실행 방법

```bash
# GUI 모드
python main.py

# CLI 모드
python main.py AAPL
python main.py 005930
```

## 주요 기능

- **종목 검색**: 한글 이름, 영문 이름, 종목 코드 모두 지원
- **자동완성**: KRX 전체 종목(2,700개+) 타이핑 추천
- **실시간 가격**: 장 중 KRX 실시간가 / 장 마감 후 NXT 시간외 가격 표시
- **가격 차트**: 라인 / 캔들스틱 전환 가능
- **이동평균선**: MA20 / MA40 / MA60
- **기간 선택**: 1M / 3M / 6M / 1Y

## 설치

```bash
pip install finance-datareader yahooquery beautifulsoup4 requests matplotlib pandas
```

## 파일 구조

```
├── main.py         # GUI / CLI 진입점
└── stock_price.py  # 주식 데이터 조회 핵심 로직
```
