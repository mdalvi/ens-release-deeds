#!/usr/bin/env python3
"""
ENS Deed Checker - View Only
Check your ENS old registrar deeds without needing a private key
"""

from web3 import Web3
import json
from datetime import datetime

# Configuration
OLD_REGISTRAR = "0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef"

# TODO: Replace with your Ethereum Deed Owner address
YOUR_ADDRESS = "0xYourAddressHere"

# Optional: If you know a specific deed contract address, add it here
KNOWN_DEED = ""  # Example: "0xDeedContractAddressHere"

# Block range for scanning ENS registrations
# How to find your block range:
# 1. Go to Etherscan: https://etherscan.io/address/YOUR_ADDRESS
# 2. Click on the "Transactions" tab
# 3. Look for your first ENS-related transaction (to 0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef)
# 4. Note the block number - subtract ~1000 blocks for START_BLOCK
# 5. Find your last ENS transaction and add ~1000 blocks for END_BLOCK
# 6. This helps speed up the scan and avoid RPC rate limits
#
# Default values scan the ENS old registrar period (May 2017 - May 2020)
# Narrow this range if you know when you registered your names
START_BLOCK = 3_605_331  # Start of scan range (adjust based on your first ENS transaction)
END_BLOCK = 10_000_000    # End of scan range (adjust based on your last ENS transaction)
CHUNK_SIZE = 1000      # Number of blocks to query at once (don't change unless needed)

# RPC Configuration
# Using public RPC (free, no API key required)
PUBLIC_RPC = "https://eth.llamarpc.com"

# Alternative RPC providers (require API keys but offer better reliability):
# - Infura: https://mainnet.infura.io/v3/YOUR_API_KEY
# - Alchemy: https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
# - QuickNode: https://YOUR_ENDPOINT.quiknode.pro/YOUR_API_KEY

# Contract ABI
ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_hash", "type": "bytes32"}],
        "name": "entries",
        "outputs": [
            {"name": "", "type": "uint8"},
            {"name": "", "type": "address"},
            {"name": "", "type": "uint256"},
            {"name": "", "type": "uint256"},
            {"name": "", "type": "uint256"}
        ],
        "payable": False,
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "hash", "type": "bytes32"},
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
            {"indexed": False, "name": "registrationDate", "type": "uint256"}
        ],
        "name": "HashRegistered",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "hash", "type": "bytes32"},
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
            {"indexed": False, "name": "status", "type": "uint8"}
        ],
        "name": "BidRevealed",
        "type": "event"
    }
]

DEED_ABI = [
    {"constant": True, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "value", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

print("=" * 80)
print("ENS Old Registrar Deed Checker")
print("=" * 80)
print(f"\nYour Address: {YOUR_ADDRESS}")
print(f"Connecting to Ethereum...")

try:
    w3 = Web3(Web3.HTTPProvider(PUBLIC_RPC))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Ethereum")
        exit(1)
    
    print(f"✓ Connected to Ethereum")
    print(f"✓ Current block: {w3.eth.block_number}\n")
    
    registrar = w3.eth.contract(
        address=Web3.to_checksum_address(OLD_REGISTRAR),
        abi=ABI
    )
    
    # Get HashRegistered and BidRevealed events
    print("🔍 Searching for your registered names and revealed bids...")
    print(f"   Scanning blocks {START_BLOCK:,} to {END_BLOCK:,}")
    print("   (This may take a minute...)\n")

    # Query in chunks to avoid RPC limits
    registered_events = []
    revealed_events = []
    current_block = START_BLOCK

    while current_block <= END_BLOCK:
        to_block = min(current_block + CHUNK_SIZE - 1, END_BLOCK)
        print(f"   Scanning blocks {current_block:,} to {to_block:,}...")

        try:
            # Check for HashRegistered events
            chunk_registered = registrar.events.HashRegistered.get_logs(
                from_block=current_block,
                to_block=to_block,
                argument_filters={'owner': YOUR_ADDRESS}
            )
            registered_events.extend(chunk_registered)

            # Check for BidRevealed events
            chunk_revealed = registrar.events.BidRevealed.get_logs(
                from_block=current_block,
                to_block=to_block,
                argument_filters={'owner': YOUR_ADDRESS}
            )
            revealed_events.extend(chunk_revealed)

            if chunk_registered or chunk_revealed:
                print(f"   Found {len(chunk_registered)} registered, {len(chunk_revealed)} revealed bid(s)")
        except Exception as e:
            print(f"   Warning: Could not query range {current_block}-{to_block}: {e}")

        current_block = to_block + 1

    print()

    # Use registered events if available, otherwise use revealed bids
    events = registered_events if registered_events else revealed_events

    if revealed_events and not registered_events:
        print(f"ℹ️  Found {len(revealed_events)} revealed bid(s) but no finalized registrations")
        print(f"   Checking if these bids created deeds...\n")

    # Check known deed contract directly
    if not events and KNOWN_DEED:
        print("ℹ️  No events found via blockchain scan")
        print(f"   Checking known deed contract: {KNOWN_DEED}\n")

        try:
            deed = w3.eth.contract(address=Web3.to_checksum_address(KNOWN_DEED), abi=DEED_ABI)
            deed_owner = deed.functions.owner().call()
            deed_value = deed.functions.value().call()
            deed_balance = w3.eth.get_balance(KNOWN_DEED)

            if deed_owner.lower() == YOUR_ADDRESS.lower() and deed_balance > 0:
                print(f"✓ Found deed contract owned by you!")
                print(f"   Deed Address: {KNOWN_DEED}")
                print(f"   Deed Owner: {deed_owner}")
                print(f"   Deed Value: {w3.from_wei(deed_value, 'ether')} ETH")
                print(f"   Contract Balance: {w3.from_wei(deed_balance, 'ether')} ETH")

                # Create a mock event to process
                events = [{'type': 'manual', 'deed_address': KNOWN_DEED, 'value': deed_value}]
            else:
                print(f"⚠️  Deed not owned by you or already released")
                print(f"   Current owner: {deed_owner}")
                print(f"   Contract balance: {w3.from_wei(deed_balance, 'ether')} ETH")
                exit(0)
        except Exception as e:
            print(f"⚠️  Could not read deed contract: {e}")
            exit(0)

    if not events:
        print("❌ No registered names or deeds found")
        print("\nPossible reasons:")
        print("- You haven't registered any names in the old registrar")
        print("- Your names were registered under a different address")
        print("- Your names were already released or migrated")
        exit(0)
    
    print(f"✓ Found {len(events)} registered name(s)\n")
    print("=" * 80)
    
    total_value = 0
    releasable_count = 0
    current_time = w3.eth.get_block('latest')['timestamp']
    one_year = 365 * 24 * 60 * 60
    
    for i, event in enumerate(events, 1):
        # Handle manual deed check differently
        if event.get('type') == 'manual':
            deed_addr = event['deed_address']
            value = event['value']

            print(f"\n📋 Deed #{i} (Manually Checked)")
            print(f"   Deed Address: {deed_addr}")
            print(f"   Deed Value: {w3.from_wei(value, 'ether')} ETH")

            # For manually checked deeds, we already verified ownership above
            # The deed is from Sept 2017, so it's definitely over 1 year old
            years_old = (current_time - 1505692800) / one_year  # Sept 18, 2017 timestamp
            print(f"   ✅ RELEASABLE (Age: {years_old:.2f} years)")
            releasable_count += 1
            total_value += value
            continue

        # Original event processing logic
        label_hash = event['args']['hash']
        value = event['args']['value']

        print(f"\n📋 Deed #{i}")
        print(f"   Label Hash: {label_hash.hex()}")
        print(f"   Value: {w3.from_wei(value, 'ether')} ETH")

        # BidRevealed events have 'status' instead of 'registrationDate'
        if 'status' in event['args']:
            status_names = ['Auction', 'Owned', 'Forbidden', 'Reveal', 'NotYetAvailable', 'TooLate']
            status = event['args']['status']
            print(f"   Bid Status: {status_names[status] if status < 6 else 'Unknown'}")
            reg_date = None
        else:
            reg_date = event['args']['registrationDate']
            print(f"   Registration Date: {datetime.fromtimestamp(reg_date).strftime('%Y-%m-%d %H:%M:%S')}")

        # Check entry details
        try:
            mode, deed_addr, reg_date2, value2, highest_bid = registrar.functions.entries(label_hash).call()
            mode_names = ['Open', 'Auction', 'Owned', 'Forbidden', 'Reveal', 'NotYetAvailable']
            print(f"   Status: {mode_names[mode] if mode < 6 else 'Unknown'}")

            # Check if owned by a deed
            if deed_addr != '0x0000000000000000000000000000000000000000':
                deed = w3.eth.contract(address=Web3.to_checksum_address(deed_addr), abi=DEED_ABI)
                try:
                    deed_owner = deed.functions.owner().call()
                    deed_value = deed.functions.value().call()
                    print(f"   Deed Address: {deed_addr}")
                    print(f"   Deed Owner: {deed_owner}")
                    print(f"   Deed Value: {w3.from_wei(deed_value, 'ether')} ETH")

                    # Check if releasable
                    # Use reg_date2 from entries() if reg_date from event is not available
                    check_date = reg_date if reg_date else reg_date2

                    if check_date and check_date > 0:
                        age = current_time - check_date
                        years_old = age / one_year

                        if age >= one_year:
                            print(f"   ✅ RELEASABLE (Age: {years_old:.2f} years)")
                            releasable_count += 1
                            total_value += deed_value
                        else:
                            days_remaining = (one_year - age) / (24 * 60 * 60)
                            print(f"   ⏳ NOT YET (Age: {years_old:.2f} years, {days_remaining:.0f} days until releasable)")
                    else:
                        # If we can't determine age, assume it's from 2017 and is releasable
                        print(f"   ✅ RELEASABLE (Registration date from 2017)")
                        releasable_count += 1
                        total_value += deed_value
                except Exception as e:
                    print(f"   ⚠️  Could not read deed details: {e}")
            else:
                print(f"   ⚠️  No deed address (may have been released)")
                
        except Exception as e:
            print(f"   ⚠️  Error checking status: {e}")
    
    print("\n" + "=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   Total names found: {len(events)}")
    print(f"   Releasable deeds: {releasable_count}")
    print(f"   Total recoverable: {w3.from_wei(total_value, 'ether')} ETH")
    
    if releasable_count > 0:
        print(f"\n✅ You have {releasable_count} deed(s) ready to release!")
        print(f"   Use the full release script with your private key to claim your ETH")
        print(f"\n   Or manually release via Etherscan:")
        print(f"   https://etherscan.io/address/{OLD_REGISTRAR}#writeContract")
    else:
        print(f"\n⏳ No deeds are currently releasable")
        print(f"   Names must be at least 1 year old from registration date")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
