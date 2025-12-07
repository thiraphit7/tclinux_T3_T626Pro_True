#!/usr/bin/env python3
"""
ECB block analysis - find the AES key by analyzing repeated blocks
"""

import sys
from collections import Counter
from Crypto.Cipher import AES

def analyze_blocks(data, block_size=16):
    """Analyze block patterns"""
    blocks = [data[i:i+block_size] for i in range(0, len(data) - block_size + 1, block_size)]

    counter = Counter(blocks)
    repeated = [(b, c) for b, c in counter.items() if c > 1]

    print(f"Total blocks: {len(blocks)}")
    print(f"Unique blocks: {len(counter)}")
    print(f"Repeated blocks: {len(repeated)}")

    return sorted(repeated, key=lambda x: -x[1])

def guess_plaintext_for_blocks(repeated_blocks):
    """
    Common repeating 16-byte patterns in XML romfile:
    - Padding bytes (0x00, 0x10, etc for PKCS7)
    - Empty string values ""
    - Common values like "0" or "1"
    - Whitespace (spaces, tabs, newlines)
    """

    common_plaintexts = [
        b'\x10' * 16,  # PKCS7 padding for empty block
        b'\x00' * 16,  # Null padding
        b'" ' + b' ' * 14,  # Empty attribute
        b'="0" ' + b' ' * 10,
        b'="1" ' + b' ' * 10,
        b'\t' * 16,  # Tabs
        b'            \t\t\t\t',  # Mixed whitespace
    ]

    print("\nGuessing plaintext for most common blocks:")
    for block, count in repeated_blocks[:5]:
        print(f"\n  Block: {block.hex()} ({count} times)")

def try_known_keys(data):
    """Try known TrendChip/MediaTek AES keys"""

    keys = [
        # Common default keys
        b'\x00' * 16,
        b'SixteenByteKey!\x00',  # 16 bytes
        b'econet_romfile_',  # 16 bytes
        b'trendchip_crypt',
        b'MediaTek_Config',
        b'SKY_CFG_ENCRYPT',
        b'romfile_encrypt',
        b'config_aes_key\x00\x00',
        b'TRUEINTERNET\x00\x00\x00\x00',
        b'ais_thailand\x00\x00\x00\x00',
        b't626pro_encrypt',
        # From library strings
        b'default_MAC_AES',
        b'AES_ECB_PKCS5Pa',
        b'AES_ECB_PKCS7Pa',
    ]

    print("\n" + "=" * 60)
    print("TRYING KNOWN KEYS")
    print("=" * 60)

    for key in keys:
        key = key[:16].ljust(16, b'\x00')
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(data[:64])

            # Check for XML start
            if decrypted[:1] == b'<' or b'<' in decrypted[:32]:
                print(f"\nPotential match with key: {key}")
                print(f"Decrypted start: {decrypted[:32]}")
                print(f"Hex: {decrypted[:32].hex()}")

                # Try full decryption
                full = cipher.decrypt(data[:len(data) - len(data) % 16])
                if full[:8] == b'<ROMFILE':
                    return key, full

        except Exception as e:
            pass

    return None, None

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else '/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt'

    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"File: {filepath}")
    print(f"Size: {len(data)} bytes")

    # Analyze blocks
    repeated = analyze_blocks(data)
    guess_plaintext_for_blocks(repeated)

    # Try known keys
    key, decrypted = try_known_keys(data)

    if key:
        print(f"\n*** SUCCESS! Found key: {key}")
        output = filepath.replace('.txt', '_aes_decrypted.xml')
        with open(output, 'wb') as f:
            f.write(decrypted)
        print(f"Saved to: {output}")
    else:
        print("\nNo key found. The encryption might use:")
        print("  - Device-specific key (MAC, serial, etc.)")
        print("  - Key stored in NVRAM")
        print("  - Non-standard algorithm")

        # Show info for manual analysis
        print("\n" + "=" * 60)
        print("INFO FOR MANUAL ANALYSIS")
        print("=" * 60)

        print("\nMost repeated block (hex):")
        if repeated:
            print(f"  {repeated[0][0].hex()}")

        # If we knew what plaintext encrypts to this block,
        # we could derive the key

        print("\nTo find the key on the router, try:")
        print("  cat /proc/mtd")
        print("  tcapi show")
        print("  strings /dev/mtdX | grep -i key")

if __name__ == '__main__':
    main()
