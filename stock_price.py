import json
import FinanceDataReader as fdr
from yahooquery import search
from datetime import datetime, timedelta
from pathlib import Path

CACHE_FILE = Path(__file__).parent / "stock_cache.json"


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_symbol(symbol_or_name: str) -> tuple[str, str]:
    """종목 이름 또는 코드를 실제 심볼과 시장으로 변환.

    Returns:
        (symbol, market): market은 'KRX' 또는 'US'
    """
    # 6자리 숫자: 한국 주식 코드 직접 사용
    if symbol_or_name.isdigit():
        return symbol_or_name, 'KRX'

    # 캐시 확인
    key = symbol_or_name.lower().strip()
    cache = _load_cache()
    if key in cache:
        entry = cache[key]
        return entry["symbol"], entry["market"]

    # ASCII 대문자 알파벳 5자 이하: 미국 티커 직접 사용
    if symbol_or_name.isascii() and symbol_or_name.isalpha() and symbol_or_name.isupper() and len(symbol_or_name) <= 5:
        return symbol_or_name, 'US'

    # yahooquery로 검색
    try:
        results = search(symbol_or_name)
        quotes = results.get('quotes', []) if isinstance(results, dict) else []
        if quotes:
            # 한국 주식(.KS) 우선 선택
            ks = [q for q in quotes if q.get('symbol', '').endswith('.KS')]
            chosen = ks[0] if ks else quotes[0]
            sym = chosen['symbol']

            if sym.endswith('.KS'):
                code = sym.replace('.KS', '')
                cache[key] = {"symbol": code, "market": "KRX"}
                _save_cache(cache)
                return code, 'KRX'

            cache[key] = {"symbol": sym, "market": "US"}
            _save_cache(cache)
            return sym, 'US'
    except Exception:
        pass

    raise LookupError(symbol_or_name)


def register_name(name: str, code: str):
    """이름 → 코드 매핑을 캐시에 저장."""
    cache = _load_cache()
    market = 'KRX' if code.isdigit() else 'US'
    cache[name.lower().strip()] = {"symbol": code, "market": market}
    _save_cache(cache)


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
