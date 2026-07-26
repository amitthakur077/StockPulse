from sqlalchemy.orm import Session
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.models import PortfolioTransaction
from src.stock_api import get_stock_info

def add_portfolio_transaction(db: Session, user_id: int, symbol: str, transaction_type: str, shares: float, price: float) -> tuple[bool, str]:
    """
    Log a stock buy or sell transaction to the database.
    """
    symbol = symbol.strip().upper()
    transaction_type = transaction_type.strip().upper()
    
    if not user_id or not symbol:
        return False, "Invalid user or ticker symbol."
    if transaction_type not in ["BUY", "SELL"]:
        return False, "Transaction type must be BUY or SELL."
    if shares <= 0 or price <= 0:
        return False, "Shares and price must be positive numbers."
        
    # If it is a sell transaction, check if the user has enough shares
    if transaction_type == "SELL":
        summary = calculate_portfolio_summary(db, user_id)
        current_shares = 0.0
        for holding in summary["holdings"]:
            if holding["symbol"] == symbol:
                current_shares = holding["shares"]
                break
        if current_shares < shares:
            return False, f"Insufficient shares to sell. You currently hold {current_shares:.4f} shares of {symbol}."
            
    try:
        new_transaction = PortfolioTransaction(
            user_id=user_id,
            symbol=symbol,
            transaction_type=transaction_type,
            shares=shares,
            price=price
        )
        db.add(new_transaction)
        db.commit()
        return True, f"Successfully logged {transaction_type} of {shares} shares of {symbol} at ${price:.2f}."
    except Exception as e:
        db.rollback()
        return False, f"Failed to record transaction: {str(e)}"

def get_user_transactions(db: Session, user_id: int) -> list:
    """
    Fetch all chronological transactions logged by the user.
    """
    if not user_id:
        return []
    return db.query(PortfolioTransaction).filter(PortfolioTransaction.user_id == user_id).order_by(PortfolioTransaction.transaction_date.desc()).all()

def calculate_portfolio_summary(db: Session, user_id: int) -> dict:
    """
    Calculate the active portfolio holdings, costs, current value, and profit/loss.
    """
    summary = {
        "total_invested": 0.0,
        "total_value": 0.0,
        "total_pnl": 0.0,
        "total_pnl_pct": 0.0,
        "holdings": [],
        "transactions": []
    }
    
    if not user_id:
        return summary
        
    # Get all transactions chronologically
    txs = db.query(PortfolioTransaction).filter(PortfolioTransaction.user_id == user_id).order_by(PortfolioTransaction.transaction_date.asc()).all()
    summary["transactions"] = txs
    
    # Calculate holdings dictionary
    holdings_dict = {}
    for tx in txs:
        symbol = tx.symbol
        if symbol not in holdings_dict:
            holdings_dict[symbol] = {"shares": 0.0, "total_cost": 0.0}
            
        if tx.transaction_type == "BUY":
            holdings_dict[symbol]["shares"] += tx.shares
            holdings_dict[symbol]["total_cost"] += tx.shares * tx.price
        elif tx.transaction_type == "SELL":
            if holdings_dict[symbol]["shares"] > 0:
                old_shares = holdings_dict[symbol]["shares"]
                new_shares = max(0.0, old_shares - tx.shares)
                if new_shares == 0:
                    holdings_dict[symbol]["shares"] = 0.0
                    holdings_dict[symbol]["total_cost"] = 0.0
                else:
                    # Average cost basis remains the same, total cost decreases proportionally
                    avg_cost = holdings_dict[symbol]["total_cost"] / old_shares
                    holdings_dict[symbol]["shares"] = new_shares
                    holdings_dict[symbol]["total_cost"] = new_shares * avg_cost

    # Fetch live price updates for active holdings
    total_invested = 0.0
    total_value = 0.0
    
    for symbol, data in holdings_dict.items():
        shares = data["shares"]
        if shares <= 0:
            continue
            
        cost = data["total_cost"]
        avg_price = cost / shares if shares > 0 else 0.0
        
        # Get live ticker info
        info = get_stock_info(symbol)
        current_price = info.get("current_price")
        
        # If live fetch fails, fallback to average cost
        if current_price is None:
            current_price = avg_price
            
        curr_val = shares * current_price
        pnl = curr_val - cost
        pnl_pct = (pnl / cost) * 100 if cost != 0 else 0.0
        
        total_invested += cost
        total_value += curr_val
        
        summary["holdings"].append({
            "symbol": symbol,
            "name": info.get("name", symbol),
            "sector": info.get("sector", "N/A"),
            "shares": shares,
            "avg_price": avg_price,
            "total_cost": cost,
            "current_price": current_price,
            "current_value": curr_val,
            "pnl": pnl,
            "pnl_pct": pnl_pct
        })
        
    # Calculate global totals
    summary["total_invested"] = total_invested
    summary["total_value"] = total_value
    summary["total_pnl"] = total_value - total_invested
    summary["total_pnl_pct"] = (summary["total_pnl"] / total_invested) * 100 if total_invested != 0 else 0.0
    
    return summary
