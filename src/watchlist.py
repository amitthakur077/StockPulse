from sqlalchemy.orm import Session
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.models import Watchlist

def get_user_watchlist(db: Session, user_id: int) -> list[str]:
    """
    Get all stock ticker symbols on a user's watchlist.
    """
    if not user_id:
        return []
    
    items = db.query(Watchlist).filter(Watchlist.user_id == user_id).order_by(Watchlist.added_at.desc()).all()
    return [item.symbol for item in items]

def add_to_watchlist(db: Session, user_id: int, symbol: str) -> tuple[bool, str]:
    """
    Add a stock symbol to a user's watchlist.
    """
    symbol = symbol.strip().upper()
    if not user_id or not symbol:
        return False, "Invalid user or ticker symbol."
        
    # Check if already in watchlist
    exists = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.symbol == symbol
    ).first()
    
    if exists:
        return False, f"{symbol} is already in your watchlist."
        
    try:
        new_item = Watchlist(user_id=user_id, symbol=symbol)
        db.add(new_item)
        db.commit()
        return True, f"Successfully added {symbol} to watchlist."
    except Exception as e:
        db.rollback()
        return False, f"Failed to add to watchlist: {str(e)}"

def remove_from_watchlist(db: Session, user_id: int, symbol: str) -> tuple[bool, str]:
    """
    Remove a stock symbol from a user's watchlist.
    """
    symbol = symbol.strip().upper()
    if not user_id or not symbol:
        return False, "Invalid user or ticker symbol."
        
    item = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.symbol == symbol
    ).first()
    
    if not item:
        return False, f"{symbol} was not found in your watchlist."
        
    try:
        db.delete(item)
        db.commit()
        return True, f"Successfully removed {symbol} from watchlist."
    except Exception as e:
        db.rollback()
        return False, f"Failed to remove from watchlist: {str(e)}"

def is_in_watchlist(db: Session, user_id: int, symbol: str) -> bool:
    """
    Check if a stock symbol is already on a user's watchlist.
    """
    symbol = symbol.strip().upper()
    if not user_id or not symbol:
        return False
        
    exists = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.symbol == symbol
    ).first()
    
    return exists is not None
