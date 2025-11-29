# Hybrid Firmware Installation Guide for T626 Pro

## Overview

**Full Port: Stock MediaTek + OpenWrt + LuCI**

This hybrid firmware combines:
- Stock MediaTek Kernel 4.4.115 (preserved for hardware compatibility)
- OpenWrt 23.05.5 RootFS with LuCI Web UI
- All stock binaries, libraries, and tools unlocked
- GPON/XPON/PON management tools
- WiFi management tools
- Stock Boa web interface (port 8080)

## Firmware Structure

```
Offset      Size        Content
──────────────────────────────────────────
0x000       256 B       HDR2 Header (Magic + Version + Model + Chipset)
0x100       8,404 B     FDT (Device Tree)
0x21D4      2,651,840 B LZMA Kernel (compressed)
0x289894    ~22 MB      Squashfs RootFS (Full Port)
...         padding     0xFF to 32MB
──────────────────────────────────────────
Total:      32 MB       (33,554,432 bytes)
```

## Firmware Files

| File | Size | Description |
|------|------|-------------|
| `hybrid_firmware_ais.bin` | 32 MB | Full port firmware with all stock functions |
| `tclinux.bin` | 32 MB | Original stock firmware (backup) |

## What's Included (Full Port)

### Binaries
| Location | Count | Description |
|----------|-------|-------------|
| /bin | 61 | Core utilities |
| /sbin | 56 | System utilities |
| /usr/bin | 114 | User tools + stock tools |
| /usr/sbin | 25 | System daemons |
| /userfs/bin | 89 | Stock MediaTek tools (GPON/WiFi/etc) |

### Libraries
| Location | Count | Description |
|----------|-------|-------------|
| /lib | 247 | Core + stock libraries |
| /usr/lib | 38 | Additional libraries |

### Kernel Modules
- 41 stock kernel modules for GPON/XPON/WiFi/Network

### Key Tools
- **tcapi** - TrendChip Configuration API
- **omci/omcicfgCmd** - OMCI management
- **ponmgr** - PON Manager
- **gponflowcmd/gponmapcmd** - GPON flow control
- **xponblapicmd/xponigmpcmd** - XPON tools
- **wifimgr/wapp/wappctrl** - WiFi management
- **switchmgr** - Switch management
- **hw_nat** - Hardware NAT
- **boa** - Stock web server (port 8080)

### Web Interfaces
| Interface | Port | Description |
|-----------|------|-------------|
| LuCI | 80 | OpenWrt Web UI |
| Boa | 8080 | Stock Web UI |

---

## MTD Partition Layout

```
mtd0 - Bootloader (DO NOT TOUCH)
mtd1 - Bootloader Config (256KB)
mtd2 - Kernel (2.6MB)
mtd3 - RootFS (19.6MB)
mtd4 - tclinux (Kernel+RootFS combined)
```

---

## Method 1: Flash via Web Interface (Safest)

1. Access router web interface: `http://192.168.1.1`
2. Login with admin credentials
3. Go to **Administration** > **Firmware Upgrade**
4. Select `hybrid_firmware_ais.bin`
5. Click **Upgrade** and wait for reboot

---

## Method 2: Flash via SSH + mtd write

### Prerequisites
- SSH access to router
- Transfer firmware to router via SCP/TFTP

### Steps

```bash
# 1. Transfer firmware to router
scp hybrid_firmware_ais.bin root@192.168.1.1:/tmp/

# 2. SSH into router
ssh root@192.168.1.1

# 3. Verify firmware file
ls -la /tmp/hybrid_firmware_ais.bin
md5sum /tmp/hybrid_firmware_ais.bin

# 4. Flash firmware (to tclinux partition)
mtd write /tmp/hybrid_firmware_ais.bin tclinux

# 5. Reboot
reboot
```

---

## Method 3: Flash via dd (Advanced)

### WARNING: Using dd incorrectly can brick your device!

```bash
# 1. Backup current firmware FIRST!
dd if=/dev/mtd4 of=/tmp/backup_tclinux.bin

# 2. Flash new firmware
dd if=/tmp/hybrid_firmware_ais.bin of=/dev/mtd4

# 3. Sync and reboot
sync
reboot
```

---

## Method 4: Flash via tcapi

```bash
tcapi set SysInfo_Entry FwUpgrade /tmp/hybrid_firmware_ais.bin
tcapi commit SysInfo_Entry
tcapi save
reboot
```

---

## Method 5: Recovery via TFTP (If bricked)

1. Set PC IP to `192.168.1.100`
2. Start TFTP server with firmware
3. Rename: `mv hybrid_firmware_ais.bin tclinux.bin`
4. Power off router
5. Hold **RESET** button
6. Power on while holding RESET
7. Wait for TFTP download (~30 seconds)
8. Release RESET and wait for reboot

---

## Post-Installation

### Access Web Interfaces

| Interface | URL | Login |
|-----------|-----|-------|
| LuCI (OpenWrt) | http://192.168.1.1 | root / (blank) |
| Stock Boa | http://192.168.1.1:8080 | admin / admin |

### SSH Access

```bash
ssh root@192.168.1.1
# Password: (blank by default)
```

### Using Stock Tools

```bash
# tcapi - Configuration API
tcapi get GPON_ONU GPON_SN
tcapi set GPON_ONU GPON_SN "ZTEGC1234567"
tcapi commit GPON_ONU
tcapi save

# ponmgr - PON Manager
ponmgr_cfg status

# omci - OMCI Management
omcicfgCmd read

# WiFi Management
wifimgr
wapp
iwconfig ra0
```

### GPON Clone for AIS

```bash
# View current settings
gpon_clone -r

# Clone GPON credentials
gpon_clone -s ZTEGC1234567 -l 1234567890 -m AA:BB:CC:DD:EE:FF -R
```

#### GPON Clone Options

| Option | Description | Example |
|--------|-------------|---------|
| `-s` | GPON Serial Number | `ZTEGC1234567` |
| `-l` | LOID/PLOAM Password | `1234567890` |
| `-m` | WAN MAC Address | `AA:BB:CC:DD:EE:FF` |
| `-r` | Read current settings | - |
| `-R` | Reboot after changes | - |

---

## Troubleshooting

### Check Module Status
```bash
lsmod | grep -E 'xpon|gpon|pon|wifi|mt79'
```

### Check PON Status
```bash
cat /proc/tc3162/pon_status
cat /proc/tc3162/omci_status
```

### Restart Services
```bash
/etc/init.d/stock_services restart
/etc/init.d/ponmgr restart
/etc/init.d/wifimgr restart
```

---

## Important Notes

1. **ALWAYS backup** original firmware before flashing
2. **DO NOT** flash via wireless - use wired connection only
3. **DO NOT** power off during flash process
4. Keep original `tclinux.bin` for recovery
5. LuCI runs on port 80, Stock Boa on port 8080

---

## File Checksums

```bash
# Verify firmware integrity before flashing
md5sum hybrid_firmware_ais.bin
# Expected: cc14795fcc0a239b8c47fa22588c94bd

sha256sum hybrid_firmware_ais.bin
# Expected: 0c23ebd59ce50ed6f11d932d14a45572e418a04dd2bdff4bea6aa5c62963f9e7

# File size must be exactly 32MB (33554432 bytes)
ls -la hybrid_firmware_ais.bin
```
