# T626 Pro Hybrid Firmware Build

## Firmware Analysis Summary

| Property | Value |
|----------|-------|
| **Device** | True T626 Pro (TZN20 AX3000) |
| **Architecture** | ARM 32-bit (EABI5) |
| **Kernel** | Linux 4.4.115 |
| **Build Date** | 18 Mar 2024 |
| **Compiler** | GCC 4.9.3 (Buildroot 2015.08.1) |
| **Chipset** | MediaTek/EcoNet EN75xx series |

## Directory Structure

```
hybrid_build/
├── stock_kernel/           # Original kernel (DO NOT MODIFY!)
│   ├── vmlinux.bin        # Decompressed kernel (7MB)
│   └── mtd2_kernel.bin    # Original MTD2 partition
├── critical_modules/       # Kernel modules (.ko files)
│   ├── xpon.ko            # XPON/GPON core driver
│   ├── gpon_flow.ko       # GPON flow control
│   ├── mt7916_ap.ko       # WiFi 6 driver (9MB)
│   ├── hw_nat.ko          # Hardware NAT accelerator
│   └── ... (41 modules total)
├── stock_binaries/         # Essential userspace binaries
│   ├── ponmgr             # PON Manager
│   ├── tcapi              # TrendChip API
│   └── ... (89 binaries)
├── stock_libs/             # Shared libraries
│   ├── libxpon.so.1       # XPON library
│   ├── libpon_svc.so      # PON service library
│   ├── libapi_omci_*.so   # OMCI libraries
│   └── ... (234 libraries)
├── configs/
│   └── scripts/           # Startup scripts
│       ├── lib_xpon       # XPON module loader
│       ├── lib_modules    # Core module loader
│       └── ...
└── scripts/
    └── load_gpon_modules.sh  # Custom module loader
```

## Critical GPON Modules

These modules are **REQUIRED** for fiber internet:

| Module | Description |
|--------|-------------|
| `xpon.ko` | XPON/GPON core driver |
| `xpon_int.ko` | XPON interface |
| `xponmap.ko` | XPON GEM/LLID mapping |
| `gpon_flow.ko` | GPON flow control |
| `xpon_igmp.ko` | Multicast for GPON |
| `ponvlan.ko` | PON VLAN tagging |
| `phy.ko` | Optical PHY driver |

## How to Build Hybrid Firmware

### Step 1: Prepare OpenWrt RootFS

Download OpenWrt rootfs for ARM (Kernel 4.x):

```bash
# OpenWrt 17.01 (Kernel 4.4) recommended
wget https://downloads.openwrt.org/releases/17.01.7/targets/armvirt/32/openwrt-17.01.7-armvirt-32-root.tar.gz

# Or OpenWrt 18.06 (Kernel 4.9)
wget https://downloads.openwrt.org/releases/18.06.9/targets/armvirt/32/openwrt-18.06.9-armvirt-32-root.tar.gz
```

### Step 2: Extract and Inject Modules

```bash
# Create rootfs directory
mkdir -p rootfs
cd rootfs
tar xzf ../openwrt-*.tar.gz

# Inject stock kernel modules
cp -r ../hybrid_build/critical_modules/* lib/modules/

# Inject stock libraries
cp ../hybrid_build/stock_libs/*.so* lib/

# Inject stock binaries (PON management)
mkdir -p usr/bin
cp ../hybrid_build/stock_binaries/* usr/bin/

# Copy startup script
cp ../hybrid_build/scripts/load_gpon_modules.sh etc/init.d/
chmod +x etc/init.d/load_gpon_modules.sh

# Create symlink for auto-start
ln -s ../init.d/load_gpon_modules.sh etc/rc.d/S99gpon
```

### Step 3: Configure Auto-start

Add to `/etc/rc.local`:

```bash
# Load GPON modules at boot
/etc/init.d/load_gpon_modules.sh

# Start essential services
/usr/bin/ponmgr &
```

### Step 4: Repack Firmware

Use tcrevenge or similar tool:

```bash
# Create new squashfs
mksquashfs rootfs/ new_rootfs.squashfs -comp lzma -b 131072

# Combine with stock kernel
cat stock_kernel/mtd2_kernel.bin new_rootfs.squashfs > new_firmware.bin

# Add TrendChip header (using tcrevenge)
tcrevenge -m T626Pro -f new_firmware.bin -o tclinux_hybrid.bin
```

## Important Notes

### PON/GPON Interface Names
- `pon` - Main PON interface
- `omci` - OMCI management interface (GPON only)
- `oam` - OAM management interface (EPON only)
- `ae_wan` - Active Ethernet WAN

### Module Loading Order
The modules MUST be loaded in this order:
1. `fe_core.ko` - Forward Engine
2. `ifc.ko` - Interface Control
3. `qdma_lan.ko` / `qdma_wan.ko` - QDMA
4. `eth.ko` + `eth_ephy.ko` - Ethernet
5. `phy.ko` - PHY
6. `xpon.ko` - XPON Core
7. `xpon_int.ko` - XPON Interface
8. `xponmap.ko` + `gpon_flow.ko` - GPON specific
9. `hw_nat.ko` - Hardware NAT (optional but recommended)

### Troubleshooting

#### PON light not lit
- Check module loading order
- Verify `xpon.ko` and `phy.ko` loaded correctly
- Run `dmesg | grep -i pon` for errors

#### No internet after PON sync
- Check `ponmgr` is running: `ps | grep ponmgr`
- Verify OMCI interface: `ifconfig omci`
- Check PON registration: `cat /proc/tc3162/xpon_status`

#### WiFi not working
- Load `mt7916_ap.ko` module
- Check `/proc/tc3162/wifi_status`

## Disclaimer

This hybrid firmware approach is for educational purposes. Modifying router firmware:
- May void warranty
- May violate ISP terms of service
- Could brick your device if done incorrectly

Always backup original firmware before modifications!
