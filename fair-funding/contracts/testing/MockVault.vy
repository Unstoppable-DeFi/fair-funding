# @version 0.3.7

amount: public(uint256)
token_id: public(uint256)


@external
def __init__():
    self.amount = max_value(uint256)
    self.token_id = max_value(uint256)


@external
def register_deposit(_token_id: uint256, _amount: uint256):
    self.amount = _amount
    self.token_id = _token_id
