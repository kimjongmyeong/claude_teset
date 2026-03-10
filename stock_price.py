import requests
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
from yahooquery import search
from datetime import datetime, timedelta
from io import StringIO
import pandas as pd

# KRX 종목 목록 캐시 (이름 → 코드)
_krx_map: dict[str, str] | None = None


def _load_krx_map() -> dict[str, str]:
    """kind.krx.co.kr에서 상장 종목 이름→코드 매핑 로드."""
    global _krx_map
    if _krx_map is not None:
        return _krx_map
    try:
        url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        text = res.content.decode('euc-kr')
        df = pd.read_html(StringIO(text))[0]
        # 0번: 회사명, 2번: 종목코드
        name_col = df.iloc[:, 0]
        code_col = df.iloc[:, 2]
        _krx_map = {
            str(name): str(code).zfill(6)
            for name, code in zip(name_col, code_col)
            if pd.notna(name) and pd.notna(code) and str(code).replace('0', '')
        }
    except Exception:
        _krx_map = {}
    return _krx_map


def get_stock_names() -> list[str]:
    """KRX 상장 종목 이름 목록 반환 (자동완성용)."""
    return list(_load_krx_map().keys())


def _search_krx(name: str) -> str | None:
    """KRX 목록에서 이름으로 코드 검색 (부분 일치)."""
    krx_map = _load_krx_map()
    # 정확히 일치
    if name in krx_map:
        return krx_map[name]
    # 부분 일치 (첫 번째 결과)
    for k, v in krx_map.items():
        if name in k:
            return v
    return None


def _search_naver_stock(name: str) -> str | None:
    """네이버 검색으로 종목 코드 추출."""
    try:
        url = f"https://search.naver.com/search.naver?query={name}+주식"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        tag = soup.select_one('em.t_nm + span.t_code') or soup.select_one('span.s_code')
        if tag:
            return tag.text.strip()
        link = soup.select_one('a[href*="item/main.naver?code="]')
        if link:
            return link['href'].split('code=')[-1]
    except Exception:
        pass
    return None


def _resolve_symbol(symbol_or_name: str) -> tuple[str, str]:
    """종목 이름 또는 코드를 실제 심볼과 시장으로 변환.

    Returns:
        (symbol, market): market은 'KRX' 또는 'US'
    """
    # 6자리 숫자: 한국 주식 코드 직접 사용
    if symbol_or_name.isdigit() and len(symbol_or_name) == 6:
        return symbol_or_name, 'KRX'

    # ASCII 대문자 5자 이하: 미국 티커 직접 사용
    if symbol_or_name.isascii() and symbol_or_name.isalpha() and symbol_or_name.isupper() and len(symbol_or_name) <= 5:
        return symbol_or_name, 'US'

    # KRX 목록에서 이름 검색 (가장 빠름)
    code = _search_krx(symbol_or_name)
    if code:
        return code, 'KRX'

    # 네이버 검색으로 시도
    code = _search_naver_stock(symbol_or_name)
    if code:
        return code, 'KRX'

    # 영문 이름: yahooquery로 검색
    if symbol_or_name.isascii():
        try:
            results = search(symbol_or_name)
            quotes = results.get('quotes', []) if isinstance(results, dict) else []
            if quotes:
                ks = [q for q in quotes if q.get('symbol', '').endswith('.KS')]
                chosen = ks[0] if ks else quotes[0]
                sym = chosen['symbol']
                if sym.endswith('.KS'):
                    return sym.replace('.KS', ''), 'KRX'
                return sym, 'US'
        except Exception:
            pass

    raise ValueError(f"'{symbol_or_name}'에 해당하는 종목을 찾을 수 없습니다. 종목 코드를 직접 입력하세요 (예: 005930, AAPL).")


def get_stock_price(symbol_or_name: str) -> tuple[float, str]:
    """종목 심볼 또는 이름으로 현재 가격을 반환.

    Args:
        symbol_or_name (str): 종목 심볼 또는 이름 (예: 'AAPL', '삼성전자', '005930').

    Returns:
        (price, symbol): 현재 가격과 실제 사용된 심볼.

    Raises:
        ValueError: 종목을 찾을 수 없거나 데이터 조회 실패 시.
    """
    symbol, _ = _resolve_symbol(symbol_or_name)

    start = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    end = datetime.today().strftime('%Y-%m-%d')

    data = fdr.DataReader(symbol, start, end)
    if data.empty:
        raise ValueError(f"'{symbol}' 데이터를 가져올 수 없습니다. 심볼을 확인하세요.")

    latest = float(data['Close'].iloc[-1])
    return latest, symbol


if __name__ == "__main__":
    symbol_or_name = input("주식 종목 심볼 또는 이름을 입력하세요 (예: AAPL, 삼성전자, 005930): ")
    try:
        price, symbol = get_stock_price(symbol_or_name)
        if symbol.isdigit():
            print(f"{symbol}의 현재 가격: {price:,.0f}원")
        else:
            print(f"{symbol}의 현재 가격: ${price:.2f}")
    except ValueError as e:
        print(e)
