from typing import Optional

def divide(a: float, b: float) -> Optional[float]:
    try:
        return a / b
    except: 
        return None

ans = divide(2.0, 1.0)

print(ans)