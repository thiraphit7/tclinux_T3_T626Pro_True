#!/usr/bin/env python3
"""
Deep analysis of libcfg_clisvc.so to find exact key derivation
"""

import struct

def find_function_code(data, func_name):
    """Find function by string reference and analyze nearby code"""
    # Find the string
    pos = data.find(func_name.encode())
    if pos == -1:
        return None

    print(f"\nFound '{func_name}' string at 0x{pos:06x}")

    # In ARM, function code is usually before the string table
    # Let's search for code patterns

    return pos

def analyze_arm_code_area(data, start, size=512):
    """Analyze ARM code area for interesting patterns"""
    print(f"\nARM code analysis (0x{start:06x} - 0x{start+size:06x}):")

    # Look for function prologs (PUSH) and epilogs (POP)
    # ARM Thumb: 0xB5xx = PUSH, 0xBDxx = POP
    # ARM: 0xE92Dxxxx = STMFD (push), 0xE8BDxxxx = LDMFD (pop)

    for i in range(0, min(size, len(data) - start), 2):
        pos = start + i
        if pos + 4 > len(data):
            break

        word = struct.unpack('<H', data[pos:pos+2])[0]

        # Thumb PUSH
        if (word & 0xFF00) == 0xB500:
            print(f"  0x{pos:06x}: PUSH (function start?)")

        # Thumb POP with PC (return)
        if (word & 0xFF00) == 0xBD00:
            print(f"  0x{pos:06x}: POP PC (function return)")

        # BL instruction (function call)
        if (word & 0xF800) == 0xF000:
            print(f"  0x{pos:06x}: BL (function call)")

def find_hardcoded_constants(data):
    """Find potential hardcoded encryption constants"""
    print("\n" + "=" * 60)
    print("SEARCHING FOR HARDCODED CONSTANTS")
    print("=" * 60)

    # Common AES-related magic numbers
    constants = [
        (bytes.fromhex('63 7c 77 7b'), "AES S-box start"),
        (bytes.fromhex('52 09 6a d5'), "AES inverse S-box start"),
        (bytes.fromhex('01 02 04 08'), "AES Rcon start"),
    ]

    for pattern, name in constants:
        pos = data.find(pattern)
        if pos != -1:
            print(f"  Found {name} at 0x{pos:06x}")
            # Print context
            print(f"    Context: {data[pos:pos+32].hex()}")

    # Look for 16-byte aligned strings that might be keys
    print("\n  Looking for 16-char alphanumeric strings:")
    for i in range(0, len(data) - 16, 4):  # 4-byte aligned
        chunk = data[i:i+16]
        # Check if all alphanumeric
        if all((65 <= b <= 90) or (97 <= b <= 122) or (48 <= b <= 57) or b == 95 for b in chunk):
            text = chunk.decode('ascii')
            # Filter out common non-key strings
            if not any(kw in text.lower() for kw in ['func', 'init', 'data', 'text', 'code']):
                print(f"    0x{i:06x}: '{text}'")

def find_decode_romfile(data):
    """Find and analyze update_DecodeRomfile function"""
    print("\n" + "=" * 60)
    print("ANALYZING DECODE ROMFILE FUNCTION")
    print("=" * 60)

    # Search for related strings
    decode_strings = [
        b"update_DecodeRomfile",
        b"tmp_decoderomfile",
        b"DecodeRomfile",
    ]

    for s in decode_strings:
        pos = data.find(s)
        if pos != -1:
            print(f"\nFound '{s.decode()}' at 0x{pos:06x}")

            # Print context
            start = max(0, pos - 64)
            end = min(len(data), pos + len(s) + 64)
            print(f"  Context:")
            for i in range(start, end, 16):
                line = data[i:i+16]
                hex_str = ' '.join(f'{b:02x}' for b in line)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
                print(f"    {i:06x}: {hex_str}  |{ascii_str}|")

def search_for_key_patterns(data):
    """Search for patterns that might indicate key location"""
    print("\n" + "=" * 60)
    print("SEARCHING FOR KEY PATTERNS")
    print("=" * 60)

    # Look for references to "key", "aes", "encrypt" near each other
    key_indicators = [
        b"key",
        b"KEY",
        b"aes",
        b"AES",
        b"encrypt",
        b"ENCRYPT",
    ]

    positions = {}
    for indicator in key_indicators:
        pos = 0
        while True:
            pos = data.find(indicator, pos)
            if pos == -1:
                break
            if indicator not in positions:
                positions[indicator] = []
            positions[indicator].append(pos)
            pos += 1

    # Find clusters where multiple indicators are close together
    all_positions = []
    for indicator, pos_list in positions.items():
        for pos in pos_list:
            all_positions.append((pos, indicator.decode()))

    all_positions.sort()

    print("\n  Key-related string clusters:")
    i = 0
    while i < len(all_positions):
        cluster = [all_positions[i]]
        j = i + 1
        while j < len(all_positions) and all_positions[j][0] - cluster[-1][0] < 100:
            cluster.append(all_positions[j])
            j += 1

        if len(cluster) >= 2:
            print(f"\n  Cluster at 0x{cluster[0][0]:06x}:")
            for pos, name in cluster:
                context = data[pos:pos+32]
                ascii_ctx = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
                print(f"    0x{pos:06x}: {name} ... {ascii_ctx[:40]}")

        i = j

def check_for_static_key(data):
    """Check if there's a static key in the data section"""
    print("\n" + "=" * 60)
    print("CHECKING FOR STATIC KEY")
    print("=" * 60)

    # Common locations for static keys: after .rodata section, near crypto strings
    # Let's find the AES function imports and look nearby

    aes_refs = [
        b"AES_set_encrypt_key",
        b"AES_ecb_encrypt",
        b"AES_ECB_PKCS5Padding",
    ]

    for ref in aes_refs:
        pos = data.find(ref)
        if pos != -1:
            print(f"\nFound '{ref.decode()}' at 0x{pos:06x}")

            # Check if there's a 16-byte key nearby
            for offset in range(-256, 512, 16):
                key_pos = pos + offset
                if 0 <= key_pos <= len(data) - 16:
                    key = data[key_pos:key_pos+16]

                    # Check if it could be a key (reasonable entropy)
                    if len(set(key)) >= 8 and 0 not in key[:8]:
                        is_ascii = all(32 <= b < 127 for b in key)
                        if is_ascii:
                            print(f"    Potential ASCII key at 0x{key_pos:06x}: '{key.decode()}'")
                        elif len(set(key)) >= 12:
                            print(f"    Potential binary key at 0x{key_pos:06x}: {key.hex()}")

def main():
    lib_path = "/home/user/tclinux_T3_T626Pro_True/hybrid_build/stock_root/lib/libcfg_clisvc.so"

    print(f"Deep analysis of: {lib_path}")

    with open(lib_path, 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)} bytes")

    # Find and analyze key functions
    find_function_code(data, "default_MAC_AES_encrypt")
    find_decode_romfile(data)
    find_hardcoded_constants(data)
    search_for_key_patterns(data)
    check_for_static_key(data)

if __name__ == '__main__':
    main()
