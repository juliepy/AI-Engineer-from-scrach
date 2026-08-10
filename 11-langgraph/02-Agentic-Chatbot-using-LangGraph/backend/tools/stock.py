import requests
from langchain_core.tools import tool
from langgraph.types import interrupt

from backend.logger import get_logger

logger = get_logger(__name__)


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """
    logger.info("get_stock_price called | symbol=%s", symbol)
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey=9MZO2JUBR7IFNTOI"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        payload = response.json()
        logger.info("get_stock_price success | symbol=%s", symbol)
        return payload
    except Exception:
        logger.exception("get_stock_price failed | symbol=%s", symbol)
        return {"error": f"Failed to fetch stock price for {symbol}"}


@tool
def purchase_stock(symbol: str, quantity: int) -> dict:
    """
    Simulate purchasing a given quantity of a stock symbol.

    HUMAN-IN-THE-LOOP:
    Before confirming the purchase, this tool will interrupt
    and wait for a human decision ("yes" / anything else).
    """
    logger.info(
        "purchase_stock waiting for HITL | symbol=%s | quantity=%s",
        symbol,
        quantity,
    )
    decision = interrupt(f"Approve buying {quantity} shares of {symbol}? (yes/no)")
    logger.info(
        "purchase_stock resumed | symbol=%s | quantity=%s | decision=%s",
        symbol,
        quantity,
        decision,
    )

    if isinstance(decision, str) and decision.lower() == "yes":
        return {
            "status": "success",
            "message": f"Purchase order placed for {quantity} shares of {symbol}.",
            "symbol": symbol,
            "quantity": quantity,
        }

    return {
        "status": "cancelled",
        "message": f"Purchase of {quantity} shares of {symbol} was declined by human.",
        "symbol": symbol,
        "quantity": quantity,
    }
