#!/bin/bash
#
# T626 Pro Hybrid Firmware Builder
# Combines Stock Kernel + OpenWrt RootFS
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
WORK_DIR="${BUILD_DIR}/workspace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[*]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[X]${NC} $1"; exit 1; }
info() { echo -e "${CYAN}[i]${NC} $1"; }

echo "=================================================="
echo "  T626 Pro Hybrid Firmware Builder"
echo "  Stock Kernel 4.4.115 + OpenWrt RootFS"
echo "=================================================="
echo ""

# Check for required files
check_requirements() {
    log "Checking requirements..."

    if [ ! -f "${BUILD_DIR}/stock_kernel/vmlinux.bin" ]; then
        error "Stock kernel not found!"
    fi

    if [ ! -d "${BUILD_DIR}/critical_modules" ]; then
        error "Critical modules not found!"
    fi

    if ! command -v mksquashfs &> /dev/null; then
        error "mksquashfs not found! Install: apt install squashfs-tools"
    fi

    log "Requirements OK"
}

# Download OpenWrt rootfs
download_openwrt() {
    log "Downloading OpenWrt rootfs..."

    mkdir -p "${WORK_DIR}"
    cd "${WORK_DIR}"

    OPENWRT_URL="https://downloads.openwrt.org/releases/18.06.9/targets/armvirt/32/openwrt-18.06.9-armvirt-32-root.tar.gz"
    OPENWRT_FILE="openwrt-rootfs.tar.gz"

    if [ ! -f "${OPENWRT_FILE}" ]; then
        warn "OpenWrt rootfs not found, downloading..."
        wget -O "${OPENWRT_FILE}" "${OPENWRT_URL}" || {
            error "Failed to download OpenWrt rootfs"
        }
    else
        log "OpenWrt rootfs already exists"
    fi
}

# Extract and prepare rootfs
prepare_rootfs() {
    log "Preparing rootfs..."

    cd "${WORK_DIR}"

    # Clean previous build
    rm -rf rootfs
    mkdir -p rootfs

    # Extract OpenWrt rootfs
    tar -xzf openwrt-rootfs.tar.gz -C rootfs/

    log "Rootfs extracted"
}

# Inject stock components
inject_stock_components() {
    log "Injecting stock components..."

    ROOTFS="${WORK_DIR}/rootfs"

    # Create directories
    mkdir -p "${ROOTFS}/lib/modules"
    mkdir -p "${ROOTFS}/usr/bin"
    mkdir -p "${ROOTFS}/etc/init.d"

    # Inject kernel modules
    log "  - Copying kernel modules (41 files)..."
    cp -r "${BUILD_DIR}/critical_modules"/* "${ROOTFS}/lib/modules/" 2>/dev/null || true

    # Inject shared libraries
    log "  - Copying shared libraries..."
    cp "${BUILD_DIR}/stock_libs"/*.so* "${ROOTFS}/lib/" 2>/dev/null || true

    # Inject essential binaries
    log "  - Copying essential binaries..."
    for bin in ponmgr ponmgr_cfg tcapi ponvlancmd xponblapicmd; do
        if [ -f "${BUILD_DIR}/stock_binaries/${bin}" ]; then
            cp "${BUILD_DIR}/stock_binaries/${bin}" "${ROOTFS}/usr/bin/"
        fi
    done

    # Inject GPON loader script
    log "  - Installing GPON loader script..."
    cp "${BUILD_DIR}/scripts/load_gpon_modules.sh" "${ROOTFS}/etc/init.d/"
    chmod +x "${ROOTFS}/etc/init.d/load_gpon_modules.sh"

    # Inject GPON Clone scripts for AIS
    log "  - Installing GPON Clone scripts for AIS..."
    cp "${BUILD_DIR}/scripts/gpon_clone_ais.sh" "${ROOTFS}/usr/bin/gpon_clone"
    chmod +x "${ROOTFS}/usr/bin/gpon_clone"

    cp "${BUILD_DIR}/scripts/gpon_clone_init.sh" "${ROOTFS}/etc/init.d/gpon_clone"
    chmod +x "${ROOTFS}/etc/init.d/gpon_clone"

    # Copy GPON clone config example
    cp "${BUILD_DIR}/configs/gpon_clone.conf.example" "${ROOTFS}/etc/gpon_clone.conf.example"

    # Install LuCI GPON Clone interface (if LuCI exists)
    if [ -d "${ROOTFS}/usr/lib/lua/luci" ]; then
        log "  - Installing LuCI GPON Clone interface..."
        mkdir -p "${ROOTFS}/usr/lib/lua/luci/controller"
        mkdir -p "${ROOTFS}/usr/lib/lua/luci/model/cbi"
        cp "${BUILD_DIR}/luci/luasrc/controller/gpon_clone.lua" "${ROOTFS}/usr/lib/lua/luci/controller/"
        cp "${BUILD_DIR}/luci/luasrc/model/cbi/gpon_clone.lua" "${ROOTFS}/usr/lib/lua/luci/model/cbi/"
    fi

    # Create auto-start symlink
    mkdir -p "${ROOTFS}/etc/rc.d"
    ln -sf ../init.d/load_gpon_modules.sh "${ROOTFS}/etc/rc.d/S99gpon"
    ln -sf ../init.d/gpon_clone "${ROOTFS}/etc/rc.d/S98gpon_clone"

    # Add to rc.local
    cat >> "${ROOTFS}/etc/rc.local" << 'EOF'

# Load GPON/XPON modules for fiber connectivity
/etc/init.d/load_gpon_modules.sh

# Apply GPON Clone settings if configured
if [ -f /etc/gpon_clone.conf ]; then
    /etc/init.d/gpon_clone start
fi

exit 0
EOF

    log "Stock components injected"
    log "GPON Clone for AIS installed"
}

# Create squashfs
create_squashfs() {
    log "Creating squashfs filesystem..."

    cd "${WORK_DIR}"

    # Remove old squashfs
    rm -f new_rootfs.squashfs

    # Create squashfs with LZMA compression (matching original)
    mksquashfs rootfs/ new_rootfs.squashfs \
        -comp lzma \
        -b 131072 \
        -no-xattrs \
        -noappend

    SQUASHFS_SIZE=$(stat -c%s new_rootfs.squashfs)
    log "Squashfs created: $(( SQUASHFS_SIZE / 1024 / 1024 )) MB"
}

# Combine kernel + rootfs
combine_firmware() {
    log "Combining firmware..."

    cd "${WORK_DIR}"

    # Method 1: Simple concatenation (may need header adjustment)
    cat "${BUILD_DIR}/stock_kernel/mtd2_kernel.bin" new_rootfs.squashfs > hybrid_firmware_raw.bin

    log "Firmware combined"

    FIRMWARE_SIZE=$(stat -c%s hybrid_firmware_raw.bin)
    log "Total firmware size: $(( FIRMWARE_SIZE / 1024 / 1024 )) MB"

    warn "NOTE: This raw firmware may need TrendChip header adjustment"
    warn "Use tcrevenge tool for proper header creation"
    info "Output: ${WORK_DIR}/hybrid_firmware_raw.bin"
}

# Summary
print_summary() {
    echo ""
    echo "=================================================="
    echo "  BUILD COMPLETE"
    echo "=================================================="
    echo ""
    log "Output files:"
    ls -lh "${WORK_DIR}"/*.bin "${WORK_DIR}"/*.squashfs 2>/dev/null
    echo ""
    warn "NEXT STEPS:"
    echo "  1. Add TrendChip header using tcrevenge tool"
    echo "  2. Flash via recovery mode or TFTP"
    echo "  3. Backup original firmware first!"
    echo ""
    echo "For header creation:"
    echo "  tcrevenge -m T626Pro -f hybrid_firmware_raw.bin -o tclinux_hybrid.bin"
    echo ""
}

# Main
main() {
    check_requirements

    # Check if OpenWrt already downloaded
    if [ -f "${WORK_DIR}/openwrt-rootfs.tar.gz" ]; then
        log "Using existing OpenWrt rootfs"
    else
        warn "OpenWrt rootfs not found in workspace/"
        warn "Please download manually and place in: ${WORK_DIR}/"
        info "URL: https://downloads.openwrt.org/releases/18.06.9/targets/armvirt/32/openwrt-18.06.9-armvirt-32-root.tar.gz"

        read -p "Download now? [y/N]: " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            download_openwrt
        else
            error "OpenWrt rootfs required to continue"
        fi
    fi

    prepare_rootfs
    inject_stock_components
    create_squashfs
    combine_firmware
    print_summary
}

main "$@"
