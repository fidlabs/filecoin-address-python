#!/usr/bin/env python3
"""
Command-line tool to convert between Filecoin delegated addresses (f410f...) 
and Ethereum addresses (0x...).
"""

import sys

try:
    from filecoin_address import (
        delegated_from_eth_address,
        eth_address_from_delegated,
        validate_address_string,
    )
except ImportError:
    print("Error: filecoin-address module not found. Install it with: pip install filecoin-address")
    sys.exit(1)


def convert_address(address: str) -> str:
    """
    Convert address between Ethereum and Filecoin formats.
    
    Args:
        address: Either an Ethereum address (0x...) or Filecoin delegated address (f410f...)
        
    Returns:
        Converted address string
        
    Raises:
        ValueError: If address format is invalid or conversion fails
    """
    address = address.strip()
    
    if not address:
        raise ValueError("Address cannot be empty")
    
    # Try Ethereum -> Filecoin (if it starts with 0x)
    if address.startswith("0x"):
        try:
            result = delegated_from_eth_address(address)
            return result
        except ValueError as e:
            raise ValueError(f"Invalid Ethereum address: {e}")
        except Exception as e:
            raise ValueError(f"Failed to convert Ethereum address: {e}")
    
    # Try Filecoin -> Ethereum (if it starts with f or t and looks like a delegated address)
    if address.startswith("f410f") or address.startswith("t410f"):
        try:
            result = eth_address_from_delegated(address)
            return result
        except ValueError as e:
            raise ValueError(f"Invalid Filecoin delegated address: {e}")
        except Exception as e:
            raise ValueError(f"Failed to convert Filecoin address: {e}")
    
    # If it starts with f or t, it might be a different Filecoin address type
    if address.startswith("f") or address.startswith("t"):
        if validate_address_string(address):
            raise ValueError(f"Address is a valid Filecoin address but not a delegated address (f410f/t410f). "
                           f"Only delegated addresses can be converted to Ethereum addresses.")
        else:
            raise ValueError(f"Invalid Filecoin address format: {address}")
    
    # Unknown format
    raise ValueError(f"Unknown address format. Expected Ethereum address (0x...) or "
                   f"Filecoin delegated address (f410f... or t410f...), got: {address}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: convert_address.py <address>")
        print("\nExamples:")
        print("  convert_address.py 0x351F3A0FAfc8fF97d5359f793A0e5d5206D9BB0D")
        print("  convert_address.py f410fguptud5pzd7zpvjvt54tuds5kidntoyn3oivr6y")
        sys.exit(1)
    
    input_address = sys.argv[1]
    
    try:
        output_address = convert_address(input_address)
        print(output_address)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

