#!/usr/bin/env python3
"""
Analyze libcfg_clisvc.so to find AES key derivation logic
"""

import sys
import struct
import re

def find_strings(data, min_len=4):
    """Find all printable strings in binary data"""
    result = []
    current = b""
    start_pos = 0

    for i, b in enumerate(data):
        if 32 <= b < 127:
            if not current:
                start_pos = i
            current += bytes([b])
        else:
            if len(current) >= min_len:
                result.append((start_pos, current.decode('ascii')))
            current = b""

    return result

def find_aes_sbox(data):
    """Find AES S-box in binary (indicates AES implementation)"""
    # AES S-box starts with: 63 7c 77 7b f2 6b 6f c5
    sbox_start = bytes([0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5])

    pos = data.find(sbox_start)
    if pos != -1:
        return pos
    return None

def find_potential_keys(data):
    """Find potential 16-byte AES keys"""
    keys = []

    # Look for 16-byte sequences that could be keys
    # Keys often appear near string references or at aligned addresses

    strings = find_strings(data, 8)

    # Find strings related to encryption
    for offset, s in strings:
        if any(keyword in s.lower() for keyword in ['aes', 'key', 'encrypt', 'romfile', 'mac']):
            print(f"  0x{offset:06x}: {s}")

            # Check nearby bytes for potential keys (within 256 bytes)
            for delta in range(-128, 256, 16):
                pos = offset + delta
                if 0 <= pos <= len(data) - 16:
                    key_bytes = data[pos:pos+16]
                    # Check if it looks like a key (not all zeros, not all same, reasonable entropy)
                    if len(set(key_bytes)) > 4 and 0 not in key_bytes[:8]:
                        keys.append((pos, key_bytes))

    return keys

def analyze_mac_encrypt_function(data):
    """Try to find and analyze default_MAC_AES_encrypt function"""
    print("\n" + "=" * 60)
    print("SEARCHING FOR MAC ENCRYPTION LOGIC")
    print("=" * 60)

    # Find the string "default_MAC_AES_encrypt"
    search_str = b"default_MAC_AES_encrypt"
    pos = data.find(search_str)

    if pos != -1:
        print(f"\nFound string at offset 0x{pos:06x}")

        # Look for references to this string in the code
        # In ARM, references are usually PC-relative

        # Dump context around the string
        print("\nContext (256 bytes around the string):")
        start = max(0, pos - 128)
        context = data[start:pos + 256]
        print_hex_dump(context, start)

    # Also search for the pattern that might be the key
    # Common patterns: repeated bytes, sequential bytes, etc.

    # Search for hardcoded 16-byte values that appear multiple times
    print("\n" + "=" * 60)
    print("SEARCHING FOR REPEATED 16-BYTE PATTERNS")
    print("=" * 60)

    patterns = {}
    for i in range(0, len(data) - 16, 4):  # 4-byte aligned
        pattern = data[i:i+16]
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(i)

    # Find patterns that appear more than once (could be constants)
    repeated = [(p, locs) for p, locs in patterns.items() if len(locs) > 1 and len(set(p)) > 4]

    print(f"\nFound {len(repeated)} repeated 16-byte patterns")
    for pattern, locs in sorted(repeated, key=lambda x: -len(x[1]))[:10]:
        if all(32 <= b < 127 for b in pattern):
            print(f"  ASCII: '{pattern.decode('ascii')}' at {len(locs)} locations")
        else:
            print(f"  HEX: {pattern.hex()} at {len(locs)} locations")

def print_hex_dump(data, base_offset=0, width=16):
    """Print hex dump of data"""
    for i in range(0, len(data), width):
        line = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in line)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
        print(f"  {base_offset + i:06x}: {hex_part:<{width*3}} |{ascii_part}|")

def find_key_in_data_section(data):
    """Search for potential keys in data sections"""
    print("\n" + "=" * 60)
    print("SEARCHING DATA SECTIONS FOR KEYS")
    print("=" * 60)

    # Look for 16-byte sequences that look like keys
    # Keys typically have good entropy but aren't random

    candidates = []

    for i in range(0, len(data) - 16):
        chunk = data[i:i+16]

        # Skip all zeros or all same byte
        if len(set(chunk)) < 4:
            continue

        # Skip if contains null bytes in first 8 positions (likely not a key)
        if 0 in chunk[:8]:
            continue

        # Check if it looks like ASCII
        is_ascii = all(32 <= b < 127 for b in chunk)

        # Check entropy (simple measure)
        unique = len(set(chunk))

        if unique >= 8 or is_ascii:
            candidates.append((i, chunk, is_ascii, unique))

    # Print promising candidates
    print(f"\nFound {len(candidates)} potential key candidates")

    # Filter for likely keys (16-char ASCII strings or high entropy)
    likely_keys = []
    for offset, chunk, is_ascii, unique in candidates:
        if is_ascii:
            # Check if it's a meaningful string
            text = chunk.decode('ascii')
            # Look for key-like strings
            if any(kw in text.lower() for kw in ['key', 'aes', 'enc', 'cfg', 'rom']):
                likely_keys.append((offset, chunk, text))
        elif unique >= 12:
            # High entropy non-ASCII could be a key
            likely_keys.append((offset, chunk, None))

    print(f"\nLikely key candidates ({len(likely_keys)}):")
    for offset, chunk, text in likely_keys[:20]:
        if text:
            print(f"  0x{offset:06x}: ASCII '{text}'")
        else:
            print(f"  0x{offset:06x}: HEX {chunk.hex()}")

    return likely_keys

def main():
    lib_path = "/home/user/tclinux_T3_T626Pro_True/hybrid_build/stock_root/lib/libcfg_clisvc.so"

    print(f"Analyzing: {lib_path}")

    with open(lib_path, 'rb') as f:
        data = f.read()

    print(f"Size: {len(data)} bytes")

    # Check for AES S-box
    sbox_pos = find_aes_sbox(data)
    if sbox_pos:
        print(f"\nAES S-box found at offset 0x{sbox_pos:06x}")
    else:
        print("\nNo AES S-box found (AES might use external library)")

    # Find encryption-related strings
    print("\n" + "=" * 60)
    print("ENCRYPTION-RELATED STRINGS")
    print("=" * 60)

    strings = find_strings(data, 8)
    enc_strings = [(off, s) for off, s in strings
                   if any(kw in s.lower() for kw in ['aes', 'encrypt', 'key', 'romfile', 'mac_aes', 'pkcs'])]

    for offset, s in enc_strings:
        print(f"  0x{offset:06x}: {s}")

    # Analyze MAC encrypt function area
    analyze_mac_encrypt_function(data)

    # Find potential keys
    likely_keys = find_key_in_data_section(data)

    # Try each likely key against the encrypted file
    print("\n" + "=" * 60)
    print("TESTING CANDIDATE KEYS")
    print("=" * 60)

    enc_file = "/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt"
    try:
        with open(enc_file, 'rb') as f:
            encrypted = f.read()

        from Crypto.Cipher import AES

        for offset, key, text in likely_keys[:30]:
            try:
                cipher = AES.new(key, AES.MODE_ECB)
                decrypted = cipher.decrypt(encrypted[:64])

                if decrypted[:8] == b'<ROMFILE' or decrypted[:5] == b'<?xml':
                    print(f"\n*** SUCCESS! Key found at 0x{offset:06x}")
                    if text:
                        print(f"    Key (ASCII): '{text}'")
                    else:
                        print(f"    Key (HEX): {key.hex()}")
                    return key
            except:
                pass

        print("\nNo working key found in library")

    except Exception as e:
        print(f"Error testing keys: {e}")

    return None

if __name__ == '__main__':
    main()
