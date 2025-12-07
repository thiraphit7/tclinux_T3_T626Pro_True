#!/usr/bin/env python3
"""
Deep analysis of TrendChip romfile.cfg encryption

Looking at the byte distribution pattern:
- 66.7% printable (0x20-0x7f)
- 33.3% high bytes (0x80-0xff)
- 0% control bytes (0x00-0x1f)

This is NOT random (AES would be ~uniform), suggesting:
- Some kind of encoding (not pure encryption)
- Possibly nibble manipulation or custom XOR
"""

import sys
from collections import Counter

def analyze_patterns(data):
    """Analyze byte patterns in the encrypted data"""

    print("=" * 60)
    print("BYTE FREQUENCY ANALYSIS")
    print("=" * 60)

    counter = Counter(data)

    # Most common bytes
    print("\nTop 20 most common bytes:")
    for byte_val, count in counter.most_common(20):
        pct = 100 * count / len(data)
        char = chr(byte_val) if 32 <= byte_val < 127 else '.'
        print(f"  0x{byte_val:02x} '{char}': {count:6d} ({pct:5.2f}%)")

    # Check for ASCII patterns
    print("\n" + "=" * 60)
    print("LOOKING FOR PATTERNS")
    print("=" * 60)

    # Check every 4 bytes for patterns
    print("\nFirst 128 bytes as 4-byte groups:")
    for i in range(0, min(128, len(data)), 4):
        group = data[i:i+4]
        hex_str = ' '.join(f'{b:02x}' for b in group)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in group)
        print(f"  {i:04x}: {hex_str}  |{ascii_str}|")

def try_nibble_swap(data):
    """Try nibble swap transformation"""
    print("\n" + "=" * 60)
    print("NIBBLE SWAP ATTEMPT")
    print("=" * 60)

    swapped = bytes(((b & 0x0f) << 4) | ((b & 0xf0) >> 4) for b in data[:100])
    print("First 50 bytes after nibble swap:")
    print(''.join(chr(b) if 32 <= b < 127 else '.' for b in swapped[:50]))

    if swapped[:8] == b'<ROMFILE':
        return swapped
    return None

def try_rotation(data):
    """Try bit rotation"""
    print("\n" + "=" * 60)
    print("BIT ROTATION ATTEMPTS")
    print("=" * 60)

    for rot in range(1, 8):
        rotated = bytes(((b << rot) | (b >> (8 - rot))) & 0xff for b in data[:50])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in rotated)
        print(f"  ROL {rot}: {ascii_str[:30]}")
        if rotated[:8] == b'<ROMFILE':
            return rotated

    for rot in range(1, 8):
        rotated = bytes(((b >> rot) | (b << (8 - rot))) & 0xff for b in data[:50])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in rotated)
        print(f"  ROR {rot}: {ascii_str[:30]}")
        if rotated[:8] == b'<ROMFILE':
            return rotated

    return None

def try_xor_patterns(data):
    """Try XOR with various patterns"""
    print("\n" + "=" * 60)
    print("MULTI-BYTE XOR PATTERNS")
    print("=" * 60)

    expected = b'<ROMFILE>'

    # Calculate what multi-byte XOR key would be needed
    key_len = 16
    key = bytes(data[i] ^ expected[i % len(expected)] for i in range(key_len))
    print(f"XOR key to get '<ROMFILE>': {key.hex()}")
    print(f"Key as ASCII: {''.join(chr(b) if 32 <= b < 127 else '.' for b in key)}")

    # Try applying this key to the whole file
    decrypted = bytes(data[i] ^ key[i % key_len] for i in range(min(200, len(data))))
    print(f"\nDecrypted with this key (first 100 chars):")
    print(''.join(chr(b) if 32 <= b < 127 else '.' for b in decrypted[:100]))

    if decrypted[:8] == b'<ROMFILE':
        return key

    return None

def try_substitution_cipher(data):
    """Analyze as substitution cipher"""
    print("\n" + "=" * 60)
    print("SUBSTITUTION CIPHER ANALYSIS")
    print("=" * 60)

    # In plaintext XML, common bytes are: < > = " / space a e i n o r s t
    # In the encrypted data, find the most common and try to map

    expected_common = b'<>"= /aeinorstWan'  # Common in romfile XML

    counter = Counter(data)
    most_common = [b for b, _ in counter.most_common(len(expected_common))]

    print("Mapping most common encrypted -> expected common plaintext:")
    for enc, plain in zip(most_common[:10], expected_common[:10]):
        print(f"  0x{enc:02x} -> 0x{plain:02x} ('{chr(plain)}')")

def try_base64_custom(data):
    """Try custom base64 variants"""
    print("\n" + "=" * 60)
    print("CUSTOM BASE64 ANALYSIS")
    print("=" * 60)

    # Standard base64 charset
    std_b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    # Check if data uses mostly base64-like characters
    b64_chars = set(std_b64.encode())
    b64_count = sum(1 for b in data if b in b64_chars)
    high_count = sum(1 for b in data if b >= 0x80)

    print(f"Base64 chars: {b64_count} ({100*b64_count/len(data):.1f}%)")
    print(f"High bytes: {high_count} ({100*high_count/len(data):.1f}%)")

    # This looks like base64 with some bytes XORed
    # Try to identify the pattern

def analyze_block_patterns(data):
    """Look for repeating block patterns (common in ECB mode)"""
    print("\n" + "=" * 60)
    print("BLOCK PATTERN ANALYSIS (16-byte blocks)")
    print("=" * 60)

    block_size = 16
    blocks = [data[i:i+block_size] for i in range(0, len(data) - block_size + 1, block_size)]

    block_counter = Counter(blocks)
    repeated = [(b, c) for b, c in block_counter.items() if c > 1]

    print(f"Total blocks: {len(blocks)}")
    print(f"Unique blocks: {len(block_counter)}")
    print(f"Repeated blocks: {len(repeated)}")

    if repeated:
        print("\nRepeated blocks (ECB fingerprint):")
        for block, count in sorted(repeated, key=lambda x: -x[1])[:5]:
            print(f"  {block.hex()} : {count} times")

def main():
    if len(sys.argv) < 2:
        filepath = '/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt'
    else:
        filepath = sys.argv[1]

    print(f"Analyzing: {filepath}")

    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)} bytes")

    analyze_patterns(data)
    analyze_block_patterns(data)
    try_nibble_swap(data)
    try_rotation(data)
    xor_key = try_xor_patterns(data)
    try_substitution_cipher(data)
    try_base64_custom(data)

    if xor_key:
        print("\n" + "=" * 60)
        print(f"POTENTIAL XOR KEY FOUND: {xor_key.hex()}")
        print("=" * 60)

        # Decrypt full file
        full_decrypted = bytes(data[i] ^ xor_key[i % len(xor_key)] for i in range(len(data)))
        output_path = filepath.replace('.txt', '_xor_decrypted.cfg')
        with open(output_path, 'wb') as f:
            f.write(full_decrypted)
        print(f"Decrypted output saved to: {output_path}")

if __name__ == '__main__':
    main()
