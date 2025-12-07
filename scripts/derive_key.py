#!/usr/bin/env python3
"""
Derive AES key based on analysis of libcfg_clisvc.so

Key derivation logic found:
- sys_get_mac -> get device MAC address
- MD52PWD -> MD5 hash to password
- Base64_encode -> base64 encoding
- default_MAC_AES_encrypt -> final AES key

The key is likely: MD5(MAC) or Base64(MD5(MAC)) truncated to 16 bytes
"""

import hashlib
import base64
import sys
from Crypto.Cipher import AES

def try_key(encrypted_file, key, description):
    """Try a key and check if decryption produces valid XML"""
    with open(encrypted_file, 'rb') as f:
        data = f.read()

    try:
        # Ensure key is 16 bytes
        key = key[:16].ljust(16, b'\x00')

        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(data[:64])

        if decrypted[:8] == b'<ROMFILE' or decrypted[:5] == b'<?xml':
            print(f"\n*** SUCCESS with {description}")
            print(f"    Key: {key.hex()}")
            print(f"    Key ASCII: {key}")
            print(f"    Decrypted start: {decrypted[:32]}")
            return True, key

        # Check if first byte is '<'
        if decrypted[0:1] == b'<':
            print(f"  Partial match with {description}")
            print(f"    Decrypted start: {decrypted[:16]}")

    except Exception as e:
        pass

    return False, None

def generate_keys_from_mac(mac):
    """Generate various key derivations from MAC address"""
    keys = []

    # Clean MAC formats
    mac_clean = mac.replace(':', '').replace('-', '').upper()
    mac_lower = mac_clean.lower()
    mac_bytes = bytes.fromhex(mac_clean)

    print(f"\nMAC Address: {mac}")
    print(f"MAC bytes: {mac_bytes.hex()}")

    # Method 1: Raw MAC repeated
    key = mac_bytes + mac_bytes + mac_bytes[:4]
    keys.append((key, "MAC bytes repeated"))

    # Method 2: MD5 of MAC string (uppercase)
    md5_hash = hashlib.md5(mac_clean.encode()).digest()
    keys.append((md5_hash, "MD5(MAC uppercase string)"))

    # Method 3: MD5 of MAC string (lowercase)
    md5_hash = hashlib.md5(mac_lower.encode()).digest()
    keys.append((md5_hash, "MD5(MAC lowercase string)"))

    # Method 4: MD5 of MAC bytes
    md5_hash = hashlib.md5(mac_bytes).digest()
    keys.append((md5_hash, "MD5(MAC bytes)"))

    # Method 5: MD5 of MAC with colons
    md5_hash = hashlib.md5(mac.encode()).digest()
    keys.append((md5_hash, "MD5(MAC with colons)"))

    # Method 6: MD5 of MAC with dashes
    mac_dashes = mac.replace(':', '-')
    md5_hash = hashlib.md5(mac_dashes.encode()).digest()
    keys.append((md5_hash, "MD5(MAC with dashes)"))

    # Method 7: Base64 of MAC
    b64_mac = base64.b64encode(mac_bytes)
    keys.append((b64_mac[:16], "Base64(MAC bytes)[:16]"))

    # Method 8: Base64 of MD5 of MAC
    md5_hash = hashlib.md5(mac_bytes).digest()
    b64_md5 = base64.b64encode(md5_hash)
    keys.append((b64_md5[:16], "Base64(MD5(MAC))[:16]"))

    # Method 9: MD5 hex string (first 16 chars)
    md5_hex = hashlib.md5(mac_clean.encode()).hexdigest()[:16]
    keys.append((md5_hex.encode(), "MD5(MAC).hexdigest()[:16]"))

    # Method 10: MD5 of MAC || MAC
    md5_hash = hashlib.md5(mac_bytes + mac_bytes).digest()
    keys.append((md5_hash, "MD5(MAC || MAC)"))

    # Method 11: Simple XOR pattern with MAC
    key = bytes((mac_bytes[i % 6] ^ (i * 17)) for i in range(16))
    keys.append((key, "MAC XOR pattern"))

    # Method 12: MD5 of "MAC:" + mac
    md5_hash = hashlib.md5(f"MAC:{mac}".encode()).digest()
    keys.append((md5_hash, "MD5('MAC:' + mac)"))

    # Method 13: MD5 of WAN MAC variations
    for prefix in ['WAN_', 'wan_', 'LAN_', 'lan_', 'PON_', 'pon_', '']:
        for suffix in ['', '_KEY', '_AES', '_ENCRYPT']:
            test_str = f"{prefix}{mac_clean}{suffix}"
            md5_hash = hashlib.md5(test_str.encode()).digest()
            keys.append((md5_hash, f"MD5('{test_str}')"))

    # Method 14: Common MediaTek/TrendChip patterns
    for const in ['MediaTek', 'TrendChip', 'EcoNet', 'TRUE', 'AIS', 'SKY', 'T626Pro']:
        # const + MAC
        md5_hash = hashlib.md5((const + mac_clean).encode()).digest()
        keys.append((md5_hash, f"MD5('{const}' + MAC)"))

        # MAC + const
        md5_hash = hashlib.md5((mac_clean + const).encode()).digest()
        keys.append((md5_hash, f"MD5(MAC + '{const}')"))

    # Method 15: SHA256 truncated
    sha256 = hashlib.sha256(mac_bytes).digest()[:16]
    keys.append((sha256, "SHA256(MAC)[:16]"))

    return keys

def main():
    encrypted_file = "/home/user/tclinux_T3_T626Pro_True/romfile.cfg.txt"

    # Known MAC addresses from the router
    mac_addresses = [
        "E0:AE:A2:EF:B1:CD",  # PON MAC from HG8145B7N
        "00:00:00:00:00:00",  # Default
        "FF:FF:FF:FF:FF:FF",  # Broadcast
    ]

    # Try to find T626 Pro's actual MAC from config files
    try:
        import glob
        for cfg_file in glob.glob("/home/user/tclinux_T3_T626Pro_True/**/*.cfg", recursive=True):
            with open(cfg_file, 'r', errors='ignore') as f:
                content = f.read()
                # Look for MAC patterns
                import re
                macs = re.findall(r'([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}', content)
                for mac in macs:
                    if mac not in mac_addresses:
                        mac_addresses.append(mac)
    except:
        pass

    print("=" * 60)
    print("KEY DERIVATION FROM MAC ADDRESS")
    print("=" * 60)

    print(f"\nMAC addresses to try: {len(mac_addresses)}")
    for mac in mac_addresses[:5]:
        print(f"  {mac}")

    found = False
    for mac in mac_addresses:
        keys = generate_keys_from_mac(mac)
        print(f"\nTrying {len(keys)} key derivations for MAC {mac}...")

        for key, description in keys:
            success, working_key = try_key(encrypted_file, key, f"{description} (MAC: {mac})")
            if success:
                # Save decrypted file
                with open(encrypted_file, 'rb') as f:
                    data = f.read()

                cipher = AES.new(working_key, AES.MODE_ECB)
                decrypted = cipher.decrypt(data[:len(data) - len(data) % 16])

                output = encrypted_file.replace('.txt', '_decrypted_mac.xml')
                with open(output, 'wb') as f:
                    f.write(decrypted)
                print(f"Saved decrypted file to: {output}")
                found = True
                break

        if found:
            break

    if not found:
        print("\n" + "=" * 60)
        print("NO KEY FOUND")
        print("=" * 60)
        print("\nThe key derivation might use:")
        print("  - A different MAC address (router's actual MAC)")
        print("  - A more complex derivation algorithm")
        print("  - Additional salt or IV")
        print("\nTo find the actual MAC, check on router:")
        print("  ifconfig | grep -i hwaddr")
        print("  cat /sys/class/net/*/address")

if __name__ == '__main__':
    main()
