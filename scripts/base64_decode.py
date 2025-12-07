#!/usr/bin/env python3
"""
Decode romfile.cfg which appears to be Base64 encoded
(Found "Base64_decode failed" string in library)
"""

import base64
import sys
from Crypto.Cipher import AES

def try_base64_variants(data):
    """Try various base64 decoding approaches"""

    print("=" * 60)
    print("BASE64 DECODING ATTEMPTS")
    print("=" * 60)

    # Remove any whitespace/newlines first
    data_clean = data.replace(b'\n', b'').replace(b'\r', b'').replace(b' ', b'')

    print(f"\nOriginal size: {len(data)}")
    print(f"Cleaned size: {len(data_clean)}")

    # Standard base64 decoding
    print("\n1. Standard Base64:")
    try:
        decoded = base64.b64decode(data_clean)
        print(f"   Success! Decoded size: {len(decoded)}")
        print(f"   First 64 bytes: {decoded[:64]}")
        if decoded[:8] == b'<ROMFILE' or decoded[:5] == b'<?xml':
            print("   *** VALID XML DETECTED! ***")
            return decoded
    except Exception as e:
        print(f"   Failed: {e}")

    # URL-safe base64
    print("\n2. URL-safe Base64:")
    try:
        decoded = base64.urlsafe_b64decode(data_clean)
        print(f"   Success! Decoded size: {len(decoded)}")
        print(f"   First 64 bytes: {decoded[:64]}")
        if decoded[:8] == b'<ROMFILE':
            return decoded
    except Exception as e:
        print(f"   Failed: {e}")

    # Try with padding added
    print("\n3. Base64 with padding fix:")
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(data_clean + padding.encode())
            print(f"   Success with '{padding}' padding! Decoded size: {len(decoded)}")
            print(f"   First 32 bytes: {decoded[:32].hex()}")
            if decoded[:8] == b'<ROMFILE':
                return decoded
        except:
            pass

    # Maybe it's base64 then XOR
    print("\n4. Base64 + XOR with common bytes:")
    for xor_byte in [0x00, 0x20, 0x40, 0x80, 0xFF]:
        try:
            xored = bytes(b ^ xor_byte for b in data_clean)
            decoded = base64.b64decode(xored)
            if decoded[:8] == b'<ROMFILE':
                print(f"   Success with XOR 0x{xor_byte:02x}!")
                return decoded
        except:
            pass

    # Maybe XOR then base64
    print("\n5. XOR then Base64:")
    for xor_byte in [0x20, 0x40, 0x80]:
        try:
            decoded = base64.b64decode(data_clean)
            xored = bytes(b ^ xor_byte for b in decoded)
            if xored[:8] == b'<ROMFILE':
                print(f"   Success with XOR 0x{xor_byte:02x} after decode!")
                return xored
        except:
            pass

    # Maybe custom base64 alphabet
    print("\n6. Trying to detect custom base64 alphabet:")
    # Standard: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/

    # Count characters used
    from collections import Counter
    counter = Counter(data_clean)
    chars_used = sorted([chr(b) for b in counter.keys() if 32 <= b < 127])
    print(f"   Characters used: {''.join(chars_used[:64])}")
    print(f"   Total unique: {len(counter)}")

    return None

def try_aes_then_base64(data):
    """Maybe it's AES encrypted then base64 encoded"""
    print("\n" + "=" * 60)
    print("AES + BASE64 COMBINATIONS")
    print("=" * 60)

    # First try to decode as base64
    data_clean = data.replace(b'\n', b'').replace(b'\r', b'').replace(b' ', b'')

    try:
        decoded = base64.b64decode(data_clean)
        print(f"Base64 decoded: {len(decoded)} bytes")

        # Now try AES decryption on the decoded data
        common_keys = [
            b'\x00' * 16,
            b'econet_romfile_',
            b'trendchipdefaul',
            b'MediaTek_Config',
        ]

        for key in common_keys:
            try:
                key = key[:16].ljust(16, b'\x00')
                cipher = AES.new(key, AES.MODE_ECB)
                decrypted = cipher.decrypt(decoded[:len(decoded) - len(decoded) % 16])
                if decrypted[:8] == b'<ROMFILE':
                    print(f"SUCCESS! AES key: {key}")
                    return decrypted
            except:
                pass
    except:
        pass

    return None

def check_if_already_encoded(data):
    """Check the byte distribution to understand the encoding"""
    print("\n" + "=" * 60)
    print("BYTE ANALYSIS")
    print("=" * 60)

    from collections import Counter
    counter = Counter(data)

    # Check if it looks like base64
    b64_chars = set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
    b64_count = sum(counter.get(b, 0) for b in b64_chars)

    # Check high bytes
    high_count = sum(count for byte, count in counter.items() if byte >= 0x80)

    print(f"Standard base64 chars: {b64_count}/{len(data)} ({100*b64_count/len(data):.1f}%)")
    print(f"High bytes (>=0x80): {high_count}/{len(data)} ({100*high_count/len(data):.1f}%)")

    # Most common bytes
    print("\nTop 10 most common bytes:")
    for byte, count in counter.most_common(10):
        char = chr(byte) if 32 <= byte < 127 else '.'
        print(f"  0x{byte:02x} '{char}': {count} ({100*count/len(data):.1f}%)")

    if high_count > len(data) * 0.2:
        print("\n*** High byte count suggests NOT standard base64 ***")
        print("    Might be: custom encoding, binary encryption, or XOR'ed base64")

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else '/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt'

    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"File: {filepath}")
    print(f"Size: {len(data)} bytes")

    check_if_already_encoded(data)

    result = try_base64_variants(data)
    if result:
        output = filepath.replace('.txt', '_base64_decoded.xml')
        with open(output, 'wb') as f:
            f.write(result)
        print(f"\n*** Saved to: {output}")
        return

    result = try_aes_then_base64(data)
    if result:
        output = filepath.replace('.txt', '_aes_base64_decoded.xml')
        with open(output, 'wb') as f:
            f.write(result)
        print(f"\n*** Saved to: {output}")
        return

    print("\n" + "=" * 60)
    print("DECODING FAILED")
    print("=" * 60)
    print("The file is encrypted/encoded with a non-standard method.")
    print("Based on analysis:")
    print("  - Library uses Base64 + AES combination")
    print("  - Key is derived from MAC address")
    print("  - Need to run on actual router to decrypt")

if __name__ == '__main__':
    main()
