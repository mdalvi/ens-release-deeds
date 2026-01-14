#!/usr/bin/env python3
"""
ENS Old Registrar Deed Release Script
This script helps release deeds from the ENS old registrar (0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef)
and recover the locked ETH funds.

IMPORTANT: This script requires you to have:
1. A funded Ethereum wallet with ETH for gas fees (typically 0.00001-0.00003 ETH per deed)
2. Your private key or connection to a wallet provider
3. The names must be at least 1 year old from registration date
"""

from web3 import Web3
from eth_account import Account
import json
import time
from datetime import datetime

# Contract addresses
OLD_REGISTRAR_ADDRESS = "0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef"
ENS_REGISTRY_ADDRESS = "0x314159265dD8dbb310642f98f50C066173C1259b"

# TODO: Replace with your Ethereum address
YOUR_ADDRESS = "0xYourAddressHere"

# Optional: Pre-computed deed addresses and their corresponding label hashes
# You can add your own deed mappings here if you know them from blockchain scans
# Format: deed_address -> {label_hash, expected_value_eth}
#
# How to find your label_hash:
# Method 1: Run check_deeds.py - it will display the label hash for each deed found
# Method 2: Check Etherscan - Look at "HashRegistered" or "BidRevealed" events from
#           the old registrar (0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef) for your address
# Method 3: Calculate it - label_hash = keccak256("yourname") without the .eth suffix
#           Example: for "myname.eth", calculate keccak256("myname")
#
KNOWN_DEED_MAPPINGS = {
    # Example:
    # "0xDeedContractAddress": {
    #     "label_hash": "0xlabelhash...",
    #     "value_eth": 0.01
    # },
}

KNOWN_DEEDS = list(KNOWN_DEED_MAPPINGS.keys())

# Old Registrar ABI (relevant functions only)
OLD_REGISTRAR_ABI = [
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
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "_hash", "type": "bytes32"}],
        "name": "releaseDeed",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_hash", "type": "bytes32"}],
        "name": "state",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
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
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "HashReleased",
        "type": "event"
    }
]

# Deed contract ABI (to get owner and close deed)
DEED_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "owner",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "value",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [],
        "name": "closeDeed",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "registrar",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "creationDate",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]


class ENSDeedReleaser:
    def __init__(self, rpc_url, private_key=None):
        """
        Initialize the deed releaser

        Args:
            rpc_url: Ethereum node RPC URL (e.g., Infura, Alchemy)
            private_key: Your wallet private key (optional, for automated releases)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum node")

        print(f"✓ Connected to Ethereum node")
        print(f"✓ Current block: {self.w3.eth.block_number}")

        self.registrar = self.w3.eth.contract(
            address=Web3.to_checksum_address(OLD_REGISTRAR_ADDRESS),
            abi=OLD_REGISTRAR_ABI
        )

        if private_key:
            self.account = Account.from_key(private_key)
            print(f"✓ Wallet loaded: {self.account.address}")
        else:
            self.account = None
            print("! No private key provided - view-only mode")

    def get_label_hash_from_deed(self, deed_address):
        """
        Find the label hash for a given deed address by checking revealed bids

        Args:
            deed_address: The deed contract address

        Returns:
            The label hash (bytes32) or None if not found
        """
        # Get BidRevealed events where this deed was created
        # The deed address appears in the registrar's entries
        # We need to scan for BidRevealed events and match deed addresses

        # For now, we'll return None and rely on direct deed interaction
        # In production, you'd scan BidRevealed events or use a precomputed mapping
        return None
    
    def namehash(self, name):
        """Calculate the namehash of an ENS name"""
        node = b'\x00' * 32
        if name:
            labels = name.split('.')
            for label in reversed(labels):
                labelhash = self.w3.keccak(text=label)
                node = self.w3.keccak(node + labelhash)
        return node
    
    def get_label_hash(self, label):
        """Get the keccak256 hash of a label (the part before .eth)"""
        return self.w3.keccak(text=label)
    
    def get_registered_names(self, owner_address):
        """
        Get all names registered by an address from the old registrar
        
        Returns a list of (label_hash, registration_details) tuples
        """
        print(f"\n🔍 Searching for names registered by {owner_address}...")
        
        # Get HashRegistered events for this address
        event_filter = self.registrar.events.HashRegistered.create_filter(
            fromBlock=3605331,  # Old registrar deployment block
            toBlock='latest',
            argument_filters={'owner': owner_address}
        )
        
        events = event_filter.get_all_entries()
        
        registered_names = []
        for event in events:
            label_hash = event['args']['hash']
            registration_date = event['args']['registrationDate']
            value = event['args']['value']
            
            registered_names.append({
                'label_hash': label_hash.hex(),
                'registration_date': registration_date,
                'value': value,
                'block_number': event['blockNumber']
            })
        
        print(f"✓ Found {len(registered_names)} registered names")
        return registered_names
    
    def check_deed_status(self, label_hash):
        """
        Check the status of a deed for a given label hash
        
        Returns:
            dict with status information
        """
        label_hash_bytes = bytes.fromhex(label_hash.replace('0x', ''))
        
        # Get entry details
        try:
            mode, deed_address, registration_date, value, highest_bid = self.registrar.functions.entries(
                label_hash_bytes
            ).call()
            
            # Mode: 0=Open, 1=Auction, 2=Owned, 3=Forbidden, 4=Reveal, 5=NotYetAvailable
            mode_names = ['Open', 'Auction', 'Owned', 'Forbidden', 'Reveal', 'NotYetAvailable']
            
            result = {
                'mode': mode_names[mode] if mode < len(mode_names) else 'Unknown',
                'deed_address': deed_address,
                'registration_date': registration_date,
                'registration_date_human': datetime.fromtimestamp(registration_date).strftime('%Y-%m-%d %H:%M:%S') if registration_date > 0 else 'N/A',
                'value': value,
                'value_eth': self.w3.from_wei(value, 'ether'),
                'highest_bid': highest_bid,
                'releasable': False,
                'owner': None
            }
            
            # Check if deed exists and get owner
            if deed_address != '0x0000000000000000000000000000000000000000':
                deed_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(deed_address),
                    abi=DEED_ABI
                )
                try:
                    owner = deed_contract.functions.owner().call()
                    deed_value = deed_contract.functions.value().call()
                    result['owner'] = owner
                    result['deed_value_eth'] = self.w3.from_wei(deed_value, 'ether')
                except:
                    pass
            
            # Check if releasable (must be at least 1 year old)
            current_time = int(time.time())
            one_year = 365 * 24 * 60 * 60
            
            if registration_date > 0 and current_time >= registration_date + one_year:
                result['releasable'] = True
            
            return result
            
        except Exception as e:
            print(f"Error checking deed status: {e}")
            return None
    
    def release_deed(self, label_hash, gas_price_gwei=None):
        """
        Release a deed and recover the ETH
        
        Args:
            label_hash: The label hash to release
            gas_price_gwei: Optional custom gas price in Gwei
        
        Returns:
            Transaction hash if successful
        """
        if not self.account:
            raise Exception("Private key required to release deeds")
        
        label_hash_bytes = bytes.fromhex(label_hash.replace('0x', ''))
        
        # Check status first
        status = self.check_deed_status(label_hash)
        print(status)
        if not status:
            raise Exception("Could not check deed status")
        
        if not status['releasable']:
            raise Exception(f"Deed not releasable yet. Must be at least 1 year old. Registration date: {status['registration_date_human']}")
        
        if status['owner'] != self.account.address:
            raise Exception(f"You are not the owner of this deed. Owner: {status['owner']}")
        
        print(f"\n📝 Preparing to release deed...")
        print(f"   Label Hash: {label_hash}")
        print(f"   Value: {status['value_eth']} ETH")
        print(f"   Owner: {status['owner']}")
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(self.account.address)

        tx_params = {
            'from': self.account.address,
            'nonce': nonce,
            'gas': 300000,  # Sufficient gas for releaseDeed
        }

        # Use EIP-1559 transaction format
        if gas_price_gwei:
            # If user specified gas price, use legacy transaction
            tx_params['gasPrice'] = self.w3.to_wei(gas_price_gwei, 'gwei')
        else:
            # Use EIP-1559 with current network gas prices (Jan 2026: base ~0.131 gwei)
            # Setting higher than base fee to ensure inclusion
            tx_params['maxFeePerGas'] = self.w3.to_wei(0.2, 'gwei')  # Max 0.2 gwei (buffer above base)
            tx_params['maxPriorityFeePerGas'] = self.w3.to_wei(0.02, 'gwei')  # Tip 0.02 gwei

        # Build transaction
        transaction = self.registrar.functions.releaseDeed(
            label_hash_bytes
        ).build_transaction(tx_params)
        
        # Sign transaction
        signed_txn = self.account.sign_transaction(transaction)
        
        # Send transaction
        print(f"📤 Sending transaction...")
        print(f"   Gas settings: maxFee={tx_params.get('maxFeePerGas', tx_params.get('gasPrice'))} wei")
        print(f"   Gas limit: {tx_params['gas']}")

        # Try both attribute names for compatibility with different web3.py versions
        raw_tx = getattr(signed_txn, 'raw_transaction', None) or getattr(signed_txn, 'rawTransaction', None)

        try:
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            print(f"✓ Transaction sent: {tx_hash.hex()}")
        except Exception as e:
            print(f"\n⚠️  Transaction send failed. This might be due to:")
            print(f"   1. Public RPC restrictions (LlamaRPC may not support transaction sending)")
            print(f"   2. Insufficient gas or gas price too low")
            print(f"   3. Network congestion")
            print(f"\n💡 Recommendation: Use a dedicated RPC provider:")
            print(f"   - Infura: https://infura.io")
            print(f"   - Alchemy: https://alchemy.com")
            print(f"   - Your own Ethereum node")
            raise Exception(f"Failed to send transaction: {e}")
        
        # Wait for confirmation
        print(f"⏳ Waiting for confirmation...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt['status'] == 1:
            print(f"✅ Deed released successfully!")
            print(f"   Transaction: https://etherscan.io/tx/{tx_hash.hex()}")
            return tx_hash.hex()
        else:
            print(f"❌ Transaction failed!")
            return None


    def release_all_deeds(self, owner_address, gas_price_gwei=None):
        """
        Release all releasable deeds for an owner
        
        Args:
            owner_address: The address that owns the deeds
            gas_price_gwei: Optional custom gas price in Gwei
        
        Returns:
            List of transaction hashes
        """
        print(f"\n🚀 Starting batch deed release for {owner_address}")
        
        # Get all registered names
        names = self.get_registered_names(owner_address)
        
        if not names:
            print("No registered names found")
            return []
        
        # Check each deed
        releasable_deeds = []
        total_value = 0
        
        print(f"\n📊 Checking deed status...")
        print("-" * 80)
        
        for i, name_info in enumerate(names, 1):
            label_hash = name_info['label_hash']
            status = self.check_deed_status(label_hash)
            
            if status:
                print(f"\nDeed #{i}:")
                print(f"  Label Hash: {label_hash}")
                print(f"  Mode: {status['mode']}")
                print(f"  Value: {status['value_eth']} ETH")
                print(f"  Registration Date: {status['registration_date_human']}")
                print(f"  Releasable: {'✓ YES' if status['releasable'] else '✗ NO (not yet 1 year old)'}")
                
                if status['releasable'] and status['mode'] == 'Owned':
                    releasable_deeds.append(label_hash)
                    total_value += status['value']
        
        print("-" * 80)
        print(f"\n📈 Summary:")
        print(f"   Total deeds found: {len(names)}")
        print(f"   Releasable deeds: {len(releasable_deeds)}")
        print(f"   Total recoverable: {self.w3.from_wei(total_value, 'ether')} ETH")
        
        if not releasable_deeds:
            print("\n⚠️  No deeds are currently releasable")
            return []
        
        if not self.account:
            print("\n⚠️  Private key required to release deeds")
            print("    Add your private key to release these deeds automatically")
            return []
        
        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will release {len(releasable_deeds)} deeds")
        print("   Type 'yes' to continue: ", end='')
        confirmation = input().strip().lower()
        
        if confirmation != 'yes':
            print("❌ Cancelled")
            return []
        
        # Release each deed
        successful_releases = []
        for i, label_hash in enumerate(releasable_deeds, 1):
            print(f"\n[{i}/{len(releasable_deeds)}] Releasing deed {label_hash}...")
            try:
                tx_hash = self.release_deed(label_hash, gas_price_gwei)
                if tx_hash:
                    successful_releases.append(tx_hash)
                    print(f"✓ Success")
                else:
                    print(f"✗ Failed")
            except Exception as e:
                print(f"✗ Error: {e}")
            
            # Wait a bit between transactions
            if i < len(releasable_deeds):
                time.sleep(2)
        
        print(f"\n{'='*80}")
        print(f"🎉 Batch release complete!")
        print(f"   Successful: {len(successful_releases)}/{len(releasable_deeds)}")
        print(f"{'='*80}\n")
        
        return successful_releases

    def release_known_deeds(self, gas_price_gwei=None):
        """
        Release all known hard-coded deeds

        Args:
            gas_price_gwei: Optional custom gas price in Gwei

        Returns:
            List of transaction hashes
        """
        print(f"\n🚀 Starting batch deed release for {len(KNOWN_DEEDS)} known deeds")

        # Check each deed
        releasable_deeds = []
        total_value = 0

        print(f"\n📊 Checking deed status...")
        print("-" * 80)

        for i, (deed_addr, deed_info) in enumerate(KNOWN_DEED_MAPPINGS.items(), 1):
            label_hash = deed_info['label_hash']
            expected_value = deed_info['value_eth']

            print(f"\nDeed #{i}:")
            print(f"  Deed Address: {deed_addr}")
            print(f"  Label Hash: {label_hash}")
            print(f"  Expected Value: {expected_value} ETH")

            # Check deed ownership and balance
            try:
                deed_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(deed_addr),
                    abi=DEED_ABI
                )
                owner = deed_contract.functions.owner().call()
                deed_value = deed_contract.functions.value().call()
                deed_balance = self.w3.eth.get_balance(deed_addr)

                print(f"  Current Owner: {owner}")
                print(f"  Deed Value: {self.w3.from_wei(deed_value, 'ether')} ETH")
                print(f"  Contract Balance: {self.w3.from_wei(deed_balance, 'ether')} ETH")

                if owner.lower() == YOUR_ADDRESS.lower() and deed_balance > 0:
                    print(f"  ✅ RELEASABLE (Owner match & has balance)")
                    # Store both deed address and label hash for flexibility
                    releasable_deeds.append({
                        'deed_address': deed_addr,
                        'label_hash': label_hash,
                        'value': deed_value
                    })
                    total_value += deed_value
                else:
                    print(f"  ❌ NOT RELEASABLE (Owner: {owner[:10]}... Balance: {self.w3.from_wei(deed_balance, 'ether')} ETH)")

            except Exception as e:
                print(f"  ⚠️  Error checking deed: {e}")

        print("-" * 80)
        print(f"\n📈 Summary:")
        print(f"   Total deeds checked: {len(KNOWN_DEEDS)}")
        print(f"   Releasable deeds: {len(releasable_deeds)}")
        print(f"   Total recoverable: {self.w3.from_wei(total_value, 'ether')} ETH")

        if not releasable_deeds:
            print("\n⚠️  No deeds are currently releasable")
            return []

        if not self.account:
            print("\n⚠️  Private key required to release deeds")
            print("    Add your private key to release these deeds automatically")
            return []

        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will release {len(releasable_deeds)} deeds")
        print("   Type 'yes' to continue: ", end='')
        confirmation = input().strip().lower()

        if confirmation != 'yes':
            print("❌ Cancelled")
            return []

        # Release each deed
        successful_releases = []
        for i, deed_info in enumerate(releasable_deeds, 1):
            label_hash = deed_info['label_hash']

            print(f"\n[{i}/{len(releasable_deeds)}] Releasing deed with label hash {label_hash[:10]}...")

            try:
                # Use registrar's releaseDeed()
                print(f"   Using registrar.releaseDeed()...")
                tx_hash = self.release_deed(label_hash, gas_price_gwei)

                if tx_hash:
                    successful_releases.append(tx_hash)
                    print(f"✓ Success")
                else:
                    print(f"✗ Failed")
            except Exception as e:
                print(f"✗ Error: {e}")

            # Wait a bit between transactions
            if i < len(releasable_deeds):
                time.sleep(2)

        print(f"\n{'='*80}")
        print(f"🎉 Batch release complete!")
        print(f"   Successful: {len(successful_releases)}/{len(releasable_deeds)}")
        print(f"{'='*80}\n")

        return successful_releases


def main():
    """Main function"""
    print("=" * 80)
    print("ENS Old Registrar Deed Release Tool")
    print("=" * 80)
    print("\nThis tool helps you release deeds from the ENS old registrar")
    print("and recover your locked ETH.")
    print("\nIMPORTANT:")
    print("- Names must be at least 1 year old from registration date")
    print("- You need ETH for gas fees (typically 0.00001-0.00003 ETH per deed)")
    print("- This only works for the OLD registrar (deployed May 2017)")
    print()
    
    # Configuration
    print("Please configure your connection:\n")
    
    # RPC URL
    print("1. Enter your Ethereum RPC URL")
    print("   Examples:")
    print("   - Infura: https://mainnet.infura.io/v3/YOUR_KEY")
    print("   - Alchemy: https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY")
    print("   - Local: http://localhost:8545")
    rpc_url = input("\n   RPC URL: ").strip()
    
    if not rpc_url:
        print("❌ RPC URL is required")
        return
    
    # Private key (optional for view-only)
    print("\n2. Enter your private key (optional, leave empty for view-only mode)")
    print("   ⚠️  WARNING: Never share your private key!")
    private_key = input("\n   Private Key (or press Enter to skip): ").strip()
    
    # Initialize
    try:
        releaser = ENSDeedReleaser(rpc_url, private_key if private_key else None)
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        return
    
    # Get balance if wallet loaded
    if releaser.account:
        balance = releaser.w3.eth.get_balance(releaser.account.address)
        balance_eth = releaser.w3.from_wei(balance, 'ether')
        print(f"   Balance: {balance_eth} ETH")

        if balance_eth < 0.001:
            print(f"   ⚠️  Warning: Low balance. You may not have enough for gas fees.")
            print(f"   Recommended: At least 0.001 ETH for multiple deed releases")
    
    # Release deeds
    gas_price = input("\n3. Custom gas price in Gwei (press Enter for automatic): ").strip()
    gas_price_gwei = float(gas_price) if gas_price else None

    print("\n" + "=" * 80)
    print(f"\nFound {len(KNOWN_DEEDS)} hard-coded deeds to check")
    print("Using pre-computed deed addresses and label hashes")
    print("(This avoids slow event scanning on public RPC nodes)")

    try:
        releaser.release_known_deeds(gas_price_gwei)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
