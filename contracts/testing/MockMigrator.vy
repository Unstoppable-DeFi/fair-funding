
from vyper.interfaces import ERC20

WETH: constant(address) = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2

@external
def migrate():
    ERC20(WETH).approve(0x0000000000000000000000000000000000000666, 666)