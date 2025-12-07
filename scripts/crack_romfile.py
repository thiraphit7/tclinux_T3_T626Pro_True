#!/usr/bin/env python3
"""
Crack the romfile.cfg XOR encryption

Based on analysis:
- File uses XOR encryption
- Key starts with e68c1995... but needs refinement
- Expected plaintext starts with <ROMFILE>
"""

import sys

def find_xor_key(data, known_plaintext):
    """Find XOR key by comparing with known plaintext"""
    key = bytes(data[i] ^ known_plaintext[i] for i in range(len(known_plaintext)))
    return key

def try_key_lengths(data):
    """Try different key lengths based on repeating patterns"""

    # We know plaintext should start with "<ROMFILE> \n<Wan>" based on romfile_f.cfg
    expected_start = b'<ROMFILE> \n<Wan>\n\t<Common ReConnect="1" '

    print("Testing key lengths...")

    for key_len in [4, 8, 12, 16, 24, 32]:
        # Get key from first key_len bytes
        key = bytes(data[i] ^ expected_start[i] for i in range(min(key_len, len(expected_start))))

        # Decrypt with this key
        decrypted = bytes(data[i] ^ key[i % len(key)] for i in range(min(200, len(data))))

        # Check how much matches
        match_count = sum(1 for i in range(min(len(expected_start), len(decrypted)))
                        if decrypted[i] == expected_start[i])

        print(f"\nKey length {key_len}:")
        print(f"  Key: {key.hex()}")
        print(f"  Match: {match_count}/{len(expected_start)} bytes")
        print(f"  Decrypted: {''.join(chr(b) if 32 <= b < 127 else '.' for b in decrypted[:80])}")

        if match_count >= len(expected_start) - 5:
            return key, decrypted

    return None, None

def analyze_key_cycle(data, expected):
    """Analyze where the key repeats"""

    print("\n" + "=" * 60)
    print("KEY CYCLE ANALYSIS")
    print("=" * 60)

    # Calculate XOR difference at each position
    xor_diff = [data[i] ^ expected[i] for i in range(min(len(data), len(expected)))]

    print("\nXOR differences at each position:")
    for i in range(min(64, len(xor_diff))):
        if i % 8 == 0:
            print()
            print(f"{i:3d}: ", end="")
        print(f"{xor_diff[i]:02x} ", end="")
    print()

    # Look for repeating pattern
    for cycle_len in range(4, 33):
        is_repeating = True
        for i in range(cycle_len, min(64, len(xor_diff))):
            if xor_diff[i] != xor_diff[i % cycle_len]:
                is_repeating = False
                break
        if is_repeating:
            print(f"\nFound repeating pattern at cycle length: {cycle_len}")
            key = bytes(xor_diff[:cycle_len])
            print(f"Key: {key.hex()}")
            return key

    return None

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else '/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt'

    print(f"Cracking: {filepath}")

    with open(filepath, 'rb') as f:
        data = f.read()

    # Load reference plaintext
    ref_path = '/home/user/tclinux_T3_T626Pro_True/hybrid_build/stock_root/userfs/romfile_f.cfg'
    with open(ref_path, 'rb') as f:
        reference = f.read()

    print(f"\nEncrypted file size: {len(data)}")
    print(f"Reference file size: {len(reference)}")

    # The encrypted file is 3x larger - it might have padding or be a different config
    # But let's try to find the key using known XML patterns

    expected_patterns = [
        b'<ROMFILE>',
        b'<ROMFILE> \n',
        b'<ROMFILE>\n',
        b'<?xml version',
    ]

    for pattern in expected_patterns:
        key = find_xor_key(data, pattern)
        print(f"\nPattern: {pattern}")
        print(f"Key (first {len(pattern)} bytes): {key.hex()}")

        # Check if key looks reasonable (printable or known encryption constant)
        printable = sum(1 for b in key if 32 <= b < 127)
        print(f"Printable chars in key: {printable}/{len(key)}")

    # Try to find the actual key cycle
    key = analyze_key_cycle(data, b'<ROMFILE> \n<Wan>\n\t<Common ReConnect="1" WANAccessType="')

    if key:
        print("\n" + "=" * 60)
        print("ATTEMPTING FULL DECRYPTION")
        print("=" * 60)

        decrypted = bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

        print(f"\nFirst 200 chars of decrypted:")
        print(''.join(chr(b) if 32 <= b < 127 else '.' for b in decrypted[:200]))

        # Check if it's valid XML
        if decrypted.startswith(b'<ROMFILE') or decrypted.startswith(b'<?xml'):
            output_path = filepath.replace('.txt', '_decrypted.xml')
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            print(f"\n*** SUCCESS! Saved to: {output_path}")
        else:
            print("\nDecryption result doesn't look like valid XML")

    # Also try the simple approach
    try_key_lengths(data)

if __name__ == '__main__':
    main()
