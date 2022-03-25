from decimal import Decimal

from great_ape_safe import GreatApeSafe


def main(origin, token_addr, destination, mantissa):
    """
    send mantissa amount of token from origin to destination
    """

    safe = GreatApeSafe(origin)
    token = safe.contract(token_addr)

    safe.take_snapshot(tokens=[token.address])

    token.transfer(destination, Decimal(mantissa))

    safe.post_safe_tx(call_trace=True)
