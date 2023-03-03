# @version 0.3.7

du_yield_token: public(address)
du_amount: public(uint256)
du_recipient: public(address)
du_min_amount_out: public(uint256)

@external
def depositUnderlying(
    _yield_token: address,
    _amount: uint256,
    _recipient: address,
    _min_amount_out: uint256
) -> uint256:
    self.du_yield_token = _yield_token
    self.du_amount = _amount
    self.du_recipient = _recipient
    self.du_min_amount_out = _min_amount_out
    # return _min_amount_out
    return _amount


mint_amount: public(uint256)
mint_recipient: public(address)
@external
def mint(
    _amount: uint256,
    _recipient: address
):
    self.mint_amount = _amount
    self.mint_recipient = _recipient


wu_yield_token: public(address)
wu_shares: public(uint256)
wu_recipient: public(address)
wu_min_amount_out: public(uint256)

@external
def withdrawUnderlying(
        _yield_token: address,
        _shares: uint256,
        _recipient: address,
        _min_amount_out: uint256
    ) -> uint256:
    self.wu_yield_token = _yield_token
    self.wu_shares = _shares
    self.wu_recipient = _recipient
    self.wu_min_amount_out = _min_amount_out
    return _min_amount_out



liquidate_yield_token: public(address)
liquidate_shares: public(uint256)
liquidate_min_amount_out: public(uint256)

@external
def liquidate(
    _yield_token: address,
    _shares: uint256,
    _min_amount_out: uint256
) -> uint256:
    self.liquidate_yield_token = _yield_token
    self.liquidate_shares = _shares
    self.liquidate_min_amount_out = _min_amount_out
    return _shares


@external
def getUnderlyingTokensPerShare(_addr: address) -> uint256:
    return 1*10**18


@external
@view
def convertSharesToUnderlyingTokens(_yield_token: address, _shares: uint256) -> uint256:
    return _shares

@external
def normalizeUnderlyingTokensToDebt(_underlying_token: address, _amount: uint256) -> uint256:
    return _amount


total_value: public(uint256)
@external
def totalValue(_owner: address) -> uint256: 
    return self.total_value


@external
def minimumCollateralization() -> uint256:
    return 2000000000000000000


debt: public(int256)
@external
def accounts(_owner: address) -> (int256, DynArray[address, 8]): 
    return (self.debt, [])


shares: public(uint256)
@external
def positions(_owner: address, _yield_token: address) -> (uint256, uint256):
    return self.shares, 1