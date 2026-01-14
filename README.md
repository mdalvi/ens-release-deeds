# ENS Old Registrar Deed Release Tool

Complete toolkit to release your ENS deeds from the old registrar and recover your locked ETH.

**Old Registrar Contract:** `0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef`

## 📦 What's Included

- [check_deeds.py](check_deeds.py) - View-only script to check your deed status (no private key needed)
- [release_ens_deeds.py](release_ens_deeds.py) - Full automated release tool (requires private key)
- [requirements.txt](requirements.txt) - Python dependencies

## 🚀 Quick Start

### Step 1: Configure Your Address

Before running the scripts, edit the Python files and replace the placeholder address:

In [check_deeds.py](check_deeds.py:15):
```python
YOUR_ADDRESS = "0xYourAddressHere"  # Replace with your Ethereum address
```

In [release_ens_deeds.py](release_ens_deeds.py:24):
```python
YOUR_ADDRESS = "0xYourAddressHere"  # Replace with your Ethereum address
```

#### Optional: Configure Block Range (Speeds Up Scanning)

In [check_deeds.py](check_deeds.py:31-33), you can narrow the block range to speed up scanning:

```python
START_BLOCK = 3_605_331  # Start of scan range
END_BLOCK = 10_000_000    # End of scan range
```

**How to find your block range:**

1. **Open Etherscan:** Go to https://etherscan.io/address/YOUR_ADDRESS (replace with your address)
2. **Navigate to Transactions:** Click the **"Transactions"** tab
3. **Find ENS Transactions:**
   - Scroll through your transactions or use the search box
   - Look for transactions **"To:"** `0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef` (ENS Old Registrar)
   - Common ENS methods: `newBid`, `unsealBid`, `finalizeAuction`
4. **Note Block Numbers:**
   - **First ENS transaction:** Click on it and find "Block" number
   - **Last ENS transaction:** Do the same for your last transaction
5. **Calculate Range:**
   - `START_BLOCK = First_Block - 1000`
   - `END_BLOCK = Last_Block + 1000`

**Example:**
```
First ENS transaction: Block 4008256
Last ENS transaction:  Block 4108256

→ START_BLOCK = 4007256 (4008256 - 1,000)
→ END_BLOCK   = 4109256  (4108256 + 1,000)
```

**Why this helps:**
- Default range scans 23,000 blocks (~3 days of Ethereum)
- Narrowing to your specific range can reduce scan time by 10-100x
- Helps avoid RPC rate limits on public endpoints
- Makes the tool more reliable and faster

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Check Your Deeds (Safe, No Private Key)

```bash
python check_deeds.py
```

This will show you:
- All ENS names you registered in the old registrar
- Which ones are releasable (1+ year old)
- How much ETH you can recover
- Current deed status

### Step 4: Automated Release (Requires Private Key)

```bash
python release_ens_deeds.py
```

You'll need:
- Ethereum RPC URL (see RPC Configuration section below)
- Your private key
- ETH for gas fees (typically 0.00001-0.00003 ETH per deed at current gas prices)

The tool will:
1. Find all your deeds
2. Check which are releasable
3. Show you a summary
4. Ask for confirmation
5. Release all releasable deeds
6. Return the ETH to your wallet

### Option: Manual Release via Etherscan

If you prefer not to use the automated scripts:

1. Go to the [Old Registrar Contract on Etherscan](https://etherscan.io/address/0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef#writeContract)
2. Connect your wallet (MetaMask, WalletConnect, etc.)
3. Find the `releaseDeed` function
4. Enter your label hash (see "Finding Your Label Hash" section below)
5. Set gas limit to ~300,000
6. Submit the transaction

## 🔍 Finding Your Label Hash

The **label hash** is a cryptographic hash (keccak256) of your ENS name without the `.eth` suffix. You need this to manually release deeds via Etherscan or to add to `KNOWN_DEED_MAPPINGS`.

### Method 1: Use check_deeds.py (Easiest)

Run the checker script - it automatically displays the label hash for each deed:

```bash
python check_deeds.py
```

Output will show:
```
📋 Deed #1
   Label Hash: 0xe4c631ca9a4f6a07ec48db28244ff17b2ac819cdee271615c7a403a39962ac95
   Value: 0.01 ETH
   ...
```

### Method 2: Check Etherscan Events

1. Go to [Etherscan](https://etherscan.io/address/0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef) (Old Registrar)
2. Click the **"Events"** tab
3. Filter by your address (in the search box)
4. Look for **"HashRegistered"** or **"BidRevealed"** events
5. The **"hash"** field contains your label hash

**Example:**
```
Event: HashRegistered
hash: 0xe4c631ca9a4f6a07ec48db28244ff17b2ac819cdee271615c7a403a39962ac95
owner: 0xYourAddress...
value: 10000000000000000 (0.01 ETH)
```

### Method 3: Calculate It Yourself

If you know your ENS name, calculate the label hash:

**Using Python:**
```python
from web3 import Web3

# For "myname.eth", use just "myname"
label = "myname"
label_hash = Web3.keccak(text=label).hex()
print(f"Label hash: {label_hash}")
```

**Using Online Tools:**
- Use a Keccak-256 calculator (e.g., https://emn178.github.io/online-tools/keccak_256.html)
- Input your ENS name **without** `.eth` (e.g., just "myname")
- The output is your label hash

**Important:** Use only the name part, not the full domain:
- ✅ Correct: `myname` → keccak256("myname")
- ❌ Wrong: `myname.eth` → keccak256("myname.eth")

## ⚙️ Installation

### Requirements
- Python 3.7+
- pip
- Ethereum RPC access (see RPC Configuration below)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install web3>=6.0.0 eth-account>=0.8.0
```

## 🌐 RPC Configuration

The scripts use Ethereum RPC endpoints to communicate with the blockchain. You have several options:

### Public RPC (Default)

The scripts are configured to use **LlamaRPC** by default:
```
https://eth.llamarpc.com
```

This is free and requires no API key, but may have rate limits.

### Private RPC Providers (Recommended for Reliability)

For better reliability and higher rate limits, use a dedicated RPC provider:

**Infura** (Free tier available)
- Sign up: https://infura.io
- Get your API key
- RPC URL: `https://mainnet.infura.io/v3/YOUR_API_KEY`

**Alchemy** (Free tier available)
- Sign up: https://alchemy.com
- Get your API key
- RPC URL: `https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY`

**QuickNode** (Free trial available)
- Sign up: https://quicknode.com
- Get your endpoint
- RPC URL: `https://YOUR_ENDPOINT.quiknode.pro/YOUR_API_KEY`

To use a different RPC:
- Edit the `PUBLIC_RPC` variable in [check_deeds.py](check_deeds.py:22)
- Or provide it when prompted by [release_ens_deeds.py](release_ens_deeds.py)

## 📋 Understanding Deed Release

### What is a Deed?
In the ENS old registrar (2017-2019), when you registered a name through auction, your bid amount was locked in a "deed" contract. This ETH has been locked since registration.

### When Can I Release?
- Names must be **at least 1 year old** from registration date
- You must be the **deed owner**
- The deed must still be in **"Owned"** state

### What Happens When I Release?
✅ **You get:** Your locked ETH deposit returned to your wallet  
❌ **You lose:** The ENS name (it becomes available for anyone to register)

### Why Release Instead of Migrate?
The migration period to the new permanent registrar ended on **May 4, 2020**. If you didn't migrate by then:
- You can no longer migrate the name
- The name is already available for others to register
- But you can still recover your deposit by releasing the deed

## 🔐 Security Notes

**IMPORTANT:**
- ⚠️ Never share your private key
- ⚠️ Always verify contract addresses
- ⚠️ Scripts run locally on your machine
- ⚠️ Double-check transaction details before signing

**Contract Address Verification:**
- Old Registrar: `0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef`
- Always verify on: https://etherscan.io/address/0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef

## 💡 Usage Examples

### Example 1: Check Status

```bash
$ python check_deeds.py

================================================================================
ENS Old Registrar Deed Checker
================================================================================

Your Address: 0xYourAddress...
Connecting to Ethereum...
✓ Connected to Ethereum
✓ Current block: 18500000

🔍 Searching for your registered names...

✓ Found 3 registered name(s)

================================================================================

📋 Deed #1
   Label Hash: 0x1234...
   Value: 0.05 ETH
   Registration Date: 2017-08-15 10:30:00
   Status: Owned
   Deed Address: 0xabcd...
   Deed Owner: 0xYourAddress...
   Deed Value: 0.05 ETH
   ✅ RELEASABLE (Age: 7.42 years)

================================================================================

📊 SUMMARY:
   Total names found: 3
   Releasable deeds: 2
   Total recoverable: 0.15 ETH

✅ You have 2 deed(s) ready to release!
```

### Example 2: Release Deeds

```bash
$ python release_ens_deeds.py

Please configure your connection:

1. Enter your Ethereum RPC URL
   Examples:
   - Infura: https://mainnet.infura.io/v3/YOUR_KEY
   - Alchemy: https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
   - Local: http://localhost:8545

   RPC URL: https://mainnet.infura.io/v3/YOUR_KEY

2. Enter your private key (optional, leave empty for view-only mode)
   ⚠️  WARNING: Never share your private key!

   Private Key (or press Enter to skip): 0x...

✓ Connected to Ethereum node
✓ Wallet loaded: 0xYourAddress...
   Balance: 0.5 ETH

================================================================================

🚀 Starting batch deed release for 0xYourAddress...

📊 Checking deed status...
--------------------------------------------------------------------------------
Deed #1:
  Label Hash: 0x1234...
  Mode: Owned
  Value: 0.05 ETH
  Registration Date: 2017-08-15 10:30:00
  Releasable: ✓ YES

📈 Summary:
   Total deeds found: 3
   Releasable deeds: 2
   Total recoverable: 0.15 ETH

⚠️  WARNING: This will release 2 deeds
   Type 'yes' to continue: yes

[1/2] Releasing deed 0x1234...
📤 Sending transaction...
✓ Transaction sent: 0xabcd...
⏳ Waiting for confirmation...
✅ Deed released successfully!
   Transaction: https://etherscan.io/tx/0xabcd...

🎉 Batch release complete!
   Successful: 2/2
```

## 🛠️ Troubleshooting

### "No registered names found"
- Verify you've configured `YOUR_ADDRESS` correctly in the script
- You may have registered under a different address
- Names may have already been released/migrated
- Try checking your address on [Etherscan](https://etherscan.io) for ENS activity

### "Deed not releasable yet"
- Names must be at least 1 year old from registration date
- Check the registration date in the output
- Wait until the required time has passed

### "Transaction failed"
- Insufficient gas (try increasing to 300,000)
- Not the deed owner (verify you're using the correct wallet)
- Name already released
- RPC provider may not support transaction sending (try Infura or Alchemy)

### "Failed to connect to Ethereum node"
- Check your RPC URL is correct
- Try a different RPC provider (see RPC Configuration section)
- Check your internet connection
- Verify API key is valid (for Infura/Alchemy)

### RPC Rate Limiting
If you see rate limit errors with public RPC:
- Use a dedicated RPC provider (Infura, Alchemy)
- Add delays between requests
- Use the pre-computed deed mappings feature to avoid blockchain scans

## 📚 Additional Resources

- **ENS Documentation:** https://docs.ens.domains/
- **Old Registrar Contract:** https://etherscan.io/address/0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef
- **ENS Forum:** https://discuss.ens.domains/
- **ENS Discord:** https://chat.ens.domains/

## ❓ FAQ

**Q: Will I lose my ENS name?**  
A: Yes. Releasing the deed means the name goes back to the available pool. If you wanted to keep the name, you should have migrated it by May 4, 2020.

**Q: How much ETH will I get back?**
A: You'll receive the exact amount you deposited when you won the auction (minus gas fees for the release transaction).

**Q: Can I still use the name after releasing?**  
A: No, anyone can register it immediately after you release it.

**Q: Is this safe?**  
A: Yes, this is the official ENS smart contract function. However, always verify addresses and be careful with your private key.

**Q: What if I want to keep the name?**  
A: Unfortunately, the migration period ended in 2020. The name is likely already available for registration by others. You should recover your deposit.

**Q: Gas fees?**
A: Gas fees vary with network conditions. As of January 2026, typical costs are:
- **Normal conditions:** 0.00001-0.00003 ETH per deed release (300,000 gas at ~0.04-0.1 Gwei)
- **High congestion:** Up to 0.0001-0.0005 ETH per transaction
- Check real-time prices at https://etherscan.io/gastracker

## ⚖️ License & Disclaimer

This tool is provided as-is for educational and utility purposes. Always verify transactions before signing. The authors are not responsible for any loss of funds. Use at your own risk.

## 🤝 Contributing

Contributions are welcome! If you find bugs or have improvements:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is provided as-is under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- ENS team for the original smart contracts
- Ethereum community for documentation and support

---

**Last Updated:** January 2026
