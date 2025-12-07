# Romfile.cfg Encryption Analysis

## Overview

The T626 Pro router exports configuration backups as encrypted `romfile.cfg` files.
This document summarizes the analysis of the encryption method.

## File Information

| Property | Value |
|----------|-------|
| Encrypted file | `romfile.cfg.txt` |
| Size | 153,120 bytes |
| Reference plaintext | `romfile_f.cfg` (48,161 bytes) |
| Size ratio | 3.18x |

## Encryption Method

### Confirmed: AES-ECB Mode

Evidence:
- Library contains `AES_ECB_PKCS5Padding`, `AES_ECB_PKCS7Padding`, `AES_ecb_encrypt`
- **497 repeated 16-byte blocks** (classic ECB fingerprint)
- Most repeated block: `c5cf5aec4f4b5a644f4b5a64e3c35ac0` (303 occurrences)

### Key Discovery

The AES key is **NOT** a simple hardcoded string. Analysis shows:
- `default_MAC_AES_encrypt` function suggests key derivation from MAC address
- Key is likely device-specific (derived from hardware ID)

### Byte Distribution

```
Low bytes (0x00-0x1f):    0.0%
Printable (0x20-0x7f): 66.7%
High bytes (0x80-0xff): 33.3%
```

This non-uniform distribution indicates additional encoding/transformation.

## Related Library Functions

Found in `libcfg_clisvc.so`:

| Function | Description |
|----------|-------------|
| `cfg_load_romfile` | Load romfile from file |
| `tc_parse_romfile` | Parse romfile XML |
| `sky_cfg_write_romfile_to_flash` | Write to flash |
| `default_MAC_AES_encrypt` | MAC-based AES encryption |
| `AES_ECB_PKCS5Padding` | PKCS5 padding |
| `AES_ECB_PKCS7Padding` | PKCS7 padding |
| `AES_set_encrypt_key` | Set AES key |
| `AES_ecb_encrypt` | ECB encryption |

## Decryption Approach

### Method 1: On-Device Decryption

Run on the T626 Pro router directly:

```bash
# Check for decryption tools
ls -la /userfs/bin/ | grep -i cfg

# The router can import romfile directly via web UI
# Export will produce decrypted XML internally

# Try tcapi to read config
tcapi show > /tmp/current_config.txt
```

### Method 2: Extract Key from Running Router

```bash
# Dump potential key locations
cat /proc/mtd
strings /dev/mtdblock* | grep -i key

# Check NVRAM
nvram show | grep -i key

# Memory dump (if access available)
dd if=/dev/mem of=/tmp/memdump bs=1M count=1
strings /tmp/memdump | grep -E '^.{16}$'
```

### Method 3: Reverse Engineer Key Derivation

The `default_MAC_AES_encrypt` function suggests:
1. Key is derived from MAC address
2. Possible algorithm: `key = derive(WAN_MAC || some_constant)`

To reverse engineer:
1. Use Ghidra/IDA to analyze `libcfg_clisvc.so`
2. Find the `default_MAC_AES_encrypt` function
3. Trace key derivation logic

## Scripts Created

| Script | Purpose |
|--------|---------|
| `scripts/decrypt_romfile.py` | Try common AES keys |
| `scripts/analyze_romfile.py` | Deep pattern analysis |
| `scripts/crack_romfile.py` | XOR key finding |
| `scripts/crack_romfile_v2.py` | Known-plaintext attack |
| `scripts/ecb_analysis.py` | ECB block analysis |

## Workaround: Use Web UI Restore

Instead of decrypting, you can:

1. Create a valid romfile from `romfile_f.cfg` template
2. Modify GPON settings in plaintext
3. Import via web UI

Example modified romfile: `configs/romfile_clone_hg8145b7n.cfg`

## References

- [ASUS Romfile Tools](https://github.com/pawitp/asus-romfile-tools) - Similar concept for ASUS routers
- [TrendChip Firmware RE](https://vasvir.wordpress.com/2015/03/08/reverse-engineering-trendchip-firmware-zte-h108ns-part-i/)
- [Router Config Decryption](https://reverseengineering.stackexchange.com/questions/29257/decrypting-my-router-config-backup-file)

## Conclusion

The `romfile.cfg` encryption uses AES-128-ECB with a device-specific key, likely derived from the MAC address. Without access to the actual router or detailed reverse engineering of the key derivation algorithm, decryption is not straightforward.

**Recommended approach**: Use the web UI restore functionality with a manually crafted romfile, or extract the key from a running router.
