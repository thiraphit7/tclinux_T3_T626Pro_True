#!/usr/bin/env python3
"""
TrendChip/MediaTek romfile.cfg decryption tool

The romfile.cfg export from TrendChip routers appears to use AES-ECB encryption.
This script attempts various common keys to decrypt the file.
"""

import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def try_decrypt_aes_ecb(data, key):
    """Try to decrypt data using AES-ECB with given key"""
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(data)

        # Check if decryption looks valid (must start with <ROMFILE or <?xml)
        if decrypted[:8] == b'<ROMFILE' or decrypted[:5] == b'<?xml':
            return decrypted

        # Try to unpad PKCS7
        try:
            unpadded = unpad(decrypted, AES.block_size)
            if unpadded[:8] == b'<ROMFILE' or unpadded[:5] == b'<?xml':
                return unpadded
        except:
            pass

        return None
    except Exception as e:
        return None

def analyze_file(filepath):
    """Analyze the encrypted file structure"""
    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)} bytes")
    print(f"First 64 bytes (hex):")
    print(' '.join(f'{b:02x}' for b in data[:64]))
    print(f"\nFirst 64 bytes (ASCII):")
    print(''.join(chr(b) if 32 <= b < 127 else '.' for b in data[:64]))

    # Check byte distribution
    low_bytes = sum(1 for b in data if b < 0x20)
    mid_bytes = sum(1 for b in data if 0x20 <= b < 0x80)
    high_bytes = sum(1 for b in data if b >= 0x80)

    print(f"\nByte distribution:")
    print(f"  Low (0x00-0x1f): {low_bytes} ({100*low_bytes/len(data):.1f}%)")
    print(f"  Printable (0x20-0x7f): {mid_bytes} ({100*mid_bytes/len(data):.1f}%)")
    print(f"  High (0x80-0xff): {high_bytes} ({100*high_bytes/len(data):.1f}%)")

    return data

def try_xor_keys(data):
    """Try various XOR patterns"""
    # Expected start: <ROMFILE = 3c 52 4f 4d 46 49 4c 45
    expected = b'<ROMFILE'
    actual_start = data[:8]

    print("\n--- XOR Key Analysis ---")
    print(f"Expected start: {expected.hex()}")
    print(f"Actual start:   {actual_start.hex()}")

    # Calculate what XOR key would produce this
    xor_key = bytes(a ^ b for a, b in zip(actual_start, expected))
    print(f"XOR key needed: {xor_key.hex()}")
    print(f"XOR key ASCII:  {''.join(chr(b) if 32 <= b < 127 else '.' for b in xor_key)}")

    # Try single-byte XOR
    for key_byte in range(256):
        decrypted = bytes(b ^ key_byte for b in data[:100])
        if decrypted.startswith(b'<ROMFILE') or decrypted.startswith(b'<?xml'):
            print(f"\nFound single-byte XOR key: 0x{key_byte:02x}")
            return key_byte

    return None

def try_common_aes_keys(data):
    """Try common AES keys used in TrendChip routers"""
    # Common keys found in various router firmwares
    common_keys = [
        b'\x00' * 16,  # All zeros
        b'\xff' * 16,  # All ones
        b'0123456789abcdef',  # Sequential
        b'EcoNetTrendChip\x00',
        b'TrendChipEcoNet\x00',
        b'MediaTekRouter\x00\x00',
        b'TRUECORPORATION',
        b'trueaisconfigkey',
        b'defaultkeyvalue\x00',
        b'econetdefaultke',
        b'trendchipdefaul',
        b'configbackupkey\x00',
        b'romfileencrypti',
        b'sky_romfile_key\x00',
        b'T626ProTRUEAIS\x00\x00',
    ]

    print("\n--- AES-ECB Decryption Attempts ---")

    # Make sure data is aligned to 16 bytes
    padded_data = data[:len(data) - (len(data) % 16)]

    for key in common_keys:
        key = key[:16].ljust(16, b'\x00')  # Ensure 16 bytes
        result = try_decrypt_aes_ecb(padded_data, key)
        if result:
            print(f"SUCCESS with key: {key}")
            return result

    print("No common AES key worked")
    return None

def try_mac_derived_key(data, mac="E0:AE:A2:EF:B1:CD"):
    """Try keys derived from MAC address"""
    print(f"\n--- MAC-derived key attempts (MAC: {mac}) ---")

    mac_bytes = bytes.fromhex(mac.replace(':', ''))

    # Various MAC-based key derivations
    keys_to_try = [
        mac_bytes + mac_bytes + mac_bytes[:4],  # MAC repeated
        mac_bytes + b'\x00' * 10,  # MAC + padding
        mac_bytes[::-1] + mac_bytes[::-1] + mac_bytes[::-1][:4],  # Reversed MAC
    ]

    # Expand MAC to 16 bytes with XOR
    expanded = bytes((mac_bytes[i % 6] ^ (i * 17)) & 0xff for i in range(16))
    keys_to_try.append(expanded)

    padded_data = data[:len(data) - (len(data) % 16)]

    for i, key in enumerate(keys_to_try):
        result = try_decrypt_aes_ecb(padded_data, key)
        if result:
            print(f"SUCCESS with MAC-derived key variant {i}: {key.hex()}")
            return result

    print("No MAC-derived key worked")
    return None

def check_base64_variant(data):
    """Check if data might be base64 with some transformation"""
    print("\n--- Base64 Analysis ---")

    # Check character range
    printable = sum(1 for b in data if 0x20 <= b < 0x80)
    total = len(data)

    print(f"Printable ratio: {100*printable/total:.1f}%")

    if printable > total * 0.9:
        print("High printable ratio - might be base64 encoded")

        # Try standard base64
        import base64
        try:
            decoded = base64.b64decode(data)
            if decoded[:1] == b'<':
                print("Standard base64 decoded successfully!")
                return decoded
        except:
            pass

        # Try with XOR first
        for xor_key in [0x20, 0x40, 0x80]:
            try:
                xored = bytes(b ^ xor_key for b in data)
                decoded = base64.b64decode(xored)
                if decoded[:1] == b'<':
                    print(f"Base64 after XOR 0x{xor_key:02x} decoded successfully!")
                    return decoded
            except:
                pass

    return None

def main():
    if len(sys.argv) < 2:
        filepath = '/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt'
    else:
        filepath = sys.argv[1]

    print(f"Analyzing: {filepath}")
    print("=" * 60)

    data = analyze_file(filepath)

    # Try various decryption methods
    xor_result = try_xor_keys(data)

    base64_result = check_base64_variant(data)
    if base64_result:
        output_path = filepath.replace('.txt', '_decrypted.cfg')
        with open(output_path, 'wb') as f:
            f.write(base64_result)
        print(f"\nDecrypted output saved to: {output_path}")
        return

    aes_result = try_common_aes_keys(data)
    if aes_result:
        output_path = filepath.replace('.txt', '_decrypted.cfg')
        with open(output_path, 'wb') as f:
            f.write(aes_result)
        print(f"\nDecrypted output saved to: {output_path}")
        return

    mac_result = try_mac_derived_key(data)
    if mac_result:
        output_path = filepath.replace('.txt', '_decrypted.cfg')
        with open(output_path, 'wb') as f:
            f.write(mac_result)
        print(f"\nDecrypted output saved to: {output_path}")
        return

    print("\n" + "=" * 60)
    print("RESULT: Could not decrypt with common methods")
    print("The encryption may use:")
    print("  - Device-specific key derived from hardware ID")
    print("  - Custom proprietary algorithm")
    print("  - Key stored in flash/NVRAM")
    print("\nNext steps:")
    print("  1. Extract key from running router: cat /proc/xxx or tcapi get")
    print("  2. Use IDA/Ghidra to analyze libcfg_clisvc.so")
    print("  3. Check if router can export unencrypted config")

if __name__ == '__main__':
    main()
