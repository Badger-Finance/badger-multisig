// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

interface ICurveLP {
  function transfer ( address _to, uint256 _value ) external returns ( bool );
  function transferFrom ( address _from, address _to, uint256 _value ) external returns ( bool );
  function approve ( address _spender, uint256 _value ) external returns ( bool );
  function permit ( address _owner, address _spender, uint256 _value, uint256 _deadline, uint8 _v, bytes32 _r, bytes32 _s ) external returns ( bool );
  function increaseAllowance ( address _spender, uint256 _added_value ) external returns ( bool );
  function decreaseAllowance ( address _spender, uint256 _subtracted_value ) external returns ( bool );
  function mint ( address _to, uint256 _value ) external returns ( bool );
  function mint_relative ( address _to, uint256 frac ) external returns ( uint256 );
  function burnFrom ( address _to, uint256 _value ) external returns ( bool );
  function decimals (  ) external view returns ( uint8 );
  function version (  ) external view returns ( string calldata );
  function initialize ( string calldata _name, string calldata _symbol, address _pool ) external;
  function name (  ) external view returns ( string calldata );
  function symbol (  ) external view returns ( string calldata );
  function DOMAIN_SEPARATOR (  ) external view returns ( bytes32 );
  function balanceOf ( address arg0 ) external view returns ( uint256 );
  function allowance ( address arg0, address arg1 ) external view returns ( uint256 );
  function totalSupply (  ) external view returns ( uint256 );
  function minter (  ) external view returns ( address );
  function nonces ( address arg0 ) external view returns ( uint256 );
}
