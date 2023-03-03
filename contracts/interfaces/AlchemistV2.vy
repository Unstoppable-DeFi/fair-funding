# @version 0.3.7

interface IAlchemist:
    def depositUnderlying(
        _yield_token: address,
        _amount: uint256,
        _recipient: address,
        _min_amount_out: uint256
    ) -> uint256: nonpayable
    # function depositUnderlying(
    #     address yieldToken,
    #     uint256 amount,
    #     address recipient,
    #     uint256 minimumAmountOut
    # ) external returns (uint256 sharesIssued);

    def mint(
        _amount: uint256,
        _recipient: address
    ): nonpayable
    # function mint(uint256 amount, address recipient) external;

    def withdrawUnderlying(
        _yield_token: address,
        _shares: uint256,
        _recipient: address,
        _min_amount_out: uint256
    ) -> uint256: nonpayable
    # function withdrawUnderlying(
    #     address yieldToken,
    #     uint256 shares,
    #     address recipient,
    #     uint256 minimumAmountOut
    # ) external returns (uint256 amountWithdrawn);


    def liquidate(
        _yield_token: address,
        _shares: uint256,
        _min_amount_out: uint256
    ) -> uint256: nonpayable
    # function liquidate(
    #     address yieldToken,
    #     uint256 shares,
    #     uint256 minimumAmountOut
    # ) external returns (uint256 sharesLiquidated);


    def getUnderlyingTokensPerShare(
        _yield_token: address
    ) -> uint256: nonpayable
    # function getUnderlyingTokensPerShare(address yieldToken) external view override returns (uint256)