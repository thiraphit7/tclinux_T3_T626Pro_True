# Hybrid Firmware Installation Guide for T626 Pro

## Firmware Files

| File | Size | Description |
|------|------|-------------|
| `hybrid_firmware_ais.bin` | 32 MB | Hybrid firmware with GPON Clone for AIS |
| `tclinux.bin` | 32 MB | Original stock firmware (backup) |

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

### Alternative: Flash kernel and rootfs separately

```bash
# Extract kernel (first 2.6MB)
dd if=/tmp/hybrid_firmware_ais.bin of=/tmp/kernel.bin bs=1024 count=2660

# Extract rootfs (remaining)
dd if=/tmp/hybrid_firmware_ais.bin of=/tmp/rootfs.bin bs=1024 skip=2660

# Flash separately
mtd write /tmp/kernel.bin kernel
mtd write /tmp/rootfs.bin rootfs
reboot
```

---

## Method 3: Flash via dd (Advanced)

### WARNING: Using dd incorrectly can brick your device!

```bash
# 1. Transfer firmware to router
scp hybrid_firmware_ais.bin root@192.168.1.1:/tmp/

# 2. SSH into router
ssh root@192.168.1.1

# 3. Check current MTD devices
cat /proc/mtd

# 4. Backup current firmware FIRST!
dd if=/dev/mtd4 of=/tmp/backup_tclinux.bin
# Transfer backup to PC via scp

# 5. Flash new firmware
dd if=/tmp/hybrid_firmware_ais.bin of=/dev/mtd4

# 6. Sync and reboot
sync
reboot
```

### Flash to specific partitions with dd

```bash
# Flash kernel only (mtd2)
dd if=/tmp/hybrid_firmware_ais.bin of=/dev/mtd2 bs=1024 count=2660

# Flash rootfs only (mtd3)
dd if=/tmp/hybrid_firmware_ais.bin of=/dev/mtd3 bs=1024 skip=2660

sync
reboot
```

---

## Method 4: Flash via tcapi (TrendChip API)

```bash
# 1. Transfer firmware
scp hybrid_firmware_ais.bin root@192.168.1.1:/tmp/

# 2. SSH into router
ssh root@192.168.1.1

# 3. Use tcapi to flash
tcapi set SysInfo_Entry FwUpgrade /tmp/hybrid_firmware_ais.bin
tcapi commit SysInfo_Entry
tcapi save

# 4. Or use fwupgrade command if available
fwupgrade /tmp/hybrid_firmware_ais.bin

# 5. Reboot
reboot
```

---

## Method 5: Recovery via TFTP (If bricked)

### Requirements
- TFTP server on PC (IP: 192.168.1.100)
- Ethernet cable connected to LAN port 1
- Firmware renamed to specific filename

### Steps

1. Set PC IP to `192.168.1.100`
2. Start TFTP server with firmware file
3. Rename firmware: `mv hybrid_firmware_ais.bin tclinux.bin`
4. Power off router
5. Hold **RESET** button
6. Power on while holding RESET
7. Wait for router to download firmware via TFTP
8. Release RESET after ~30 seconds
9. Wait for reboot

---

## Post-Installation: GPON Clone Setup

After successful flash, configure GPON for AIS:

```bash
# SSH into router
ssh root@192.168.1.1

# View current GPON settings
gpon_clone -c

# Clone AIS credentials
gpon_clone -s ZTEGC1234567 -l 1234567890 -m AA:BB:CC:DD:EE:FF

# Clone with auto-restart PON interface
gpon_clone -s ZTEGC1234567 -l 1234567890 -R

# Apply settings permanently
cp /etc/gpon_clone.conf.example /etc/gpon_clone.conf
# Edit with your actual values
vi /etc/gpon_clone.conf
```

### GPON Clone Options

| Option | Description | Example |
|--------|-------------|---------|
| `-s, --sn` | GPON Serial Number | `ZTEGC1234567` |
| `-l, --loid` | LOID (Logical ONU ID) | `1234567890` |
| `-p, --password` | LOID Password | `password123` |
| `-m, --mac` | PON MAC Address | `AA:BB:CC:DD:EE:FF` |
| `-v, --vendor` | Vendor ID | `ZTEG` |
| `-e, --equipment` | Equipment ID | `ZXHN_F670L` |
| `-c, --current` | Show current settings | - |
| `-b, --backup` | Backup current settings | - |
| `-r, --restore` | Restore from backup | - |
| `-R, --restart` | Restart PON after changes | - |

---

## Troubleshooting

### Router not booting after flash
1. Try TFTP recovery method
2. Use serial console to access bootloader
3. Restore original `tclinux.bin` backup

### GPON not connecting
1. Check PON light status (should be solid green)
2. Verify GPON SN matches ISP records
3. Check LOID is correct
4. Try restarting PON: `gpon_clone -R`

### SSH not working
1. Default IP: `192.168.1.1`
2. Default user: `root`
3. Check firewall settings

### Check GPON status
```bash
# View PON status
cat /proc/tc3162/pon_status

# View OMCI status
cat /proc/tc3162/omci_status

# Check kernel modules
lsmod | grep -E 'xpon|gpon|pon'
```

---

## Important Notes

1. **ALWAYS backup** original firmware before flashing
2. **DO NOT** flash via wireless - use wired connection only
3. **DO NOT** power off during flash process
4. Keep original `tclinux.bin` for recovery
5. AIS default parameters are pre-configured (Vendor: ZTEG, Equipment: ZXHN_F670L)

---

## File Checksums

```bash
# Verify firmware integrity before flashing
md5sum hybrid_firmware_ais.bin
# Expected: ffa7661092f0a007c955054e03cd402e

sha256sum hybrid_firmware_ais.bin
# Expected: a596b541b9c755e5bf91aa7e7db57b17933663c2c86e28554d8bad03667f52e5
```
