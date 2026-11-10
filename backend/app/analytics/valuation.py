"""Simple valuation helpers. Outputs are estimates, not advice."""
import math


def graham_number(eps: float, bvps: float) -> float:
    return math.sqrt(22.5 * eps * bvps) if eps > 0 and bvps > 0 else 0.0


def pe_fair_value(eps: float, target_pe: float) -> float:
    return eps * target_pe


def dcf(fcf: float, growth: float, discount: float, terminal_growth: float = 0.04,
        years: int = 10, shares: float = 1.0) -> float:
    if discount <= terminal_growth:
        raise ValueError("discount rate must exceed terminal growth")
    pv, cf = 0.0, fcf
    for t in range(1, years + 1):
        cf *= 1 + growth
        pv += cf / (1 + discount) ** t
    tv = cf * (1 + terminal_growth) / (discount - terminal_growth)
    return (pv + tv / (1 + discount) ** years) / shares


def ipo_fair_value(eps: float, peer_pe: float, ipo_discount: float = 0.15) -> float:
    """Peer-multiple value with a discount for the 'issue premium' buyers usually demand."""
    return eps * peer_pe * (1 - ipo_discount)
