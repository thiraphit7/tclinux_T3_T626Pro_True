#!/bin/sh
#
# T626 Pro GPON Module Loader for Hybrid Firmware
# Stock Kernel 4.4.115 + OpenWrt RootFS
#
# This script loads the proprietary GPON/XPON modules
# Required for fiber internet connectivity
#

MODULES_DIR="/lib/modules"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

load_module() {
    MODULE=$1
    PARAMS=$2
    if [ -f "${MODULES_DIR}/${MODULE}" ]; then
        log_info "Loading ${MODULE}..."
        insmod ${MODULES_DIR}/${MODULE} ${PARAMS}
        if [ $? -eq 0 ]; then
            log_info "${MODULE} loaded successfully"
        else
            log_error "Failed to load ${MODULE}"
            return 1
        fi
    else
        log_warn "${MODULE} not found, skipping..."
    fi
}

# ==============================================================
# STEP 1: Core Network Modules
# ==============================================================
log_info "=== Loading Core Network Modules ==="

# Forward Engine Core
load_module "fe_core.ko"

# Interface Control
load_module "ifc.ko"

# QDMA (Queue/DMA)
load_module "qdma_lan.ko"
load_module "qdma_wan.ko"

# Ethernet
load_module "eth.ko"
load_module "eth_ephy.ko"

# PHY
load_module "phy.ko"

# ==============================================================
# STEP 2: GPON/XPON Modules (Critical for Fiber!)
# ==============================================================
log_info "=== Loading GPON/XPON Modules ==="

# XPON Core Driver
load_module "xpon.ko"

# XPON Interface
load_module "xpon_int.ko"

# XPON Mapping
load_module "xponmap.ko"

# GPON Flow Control
load_module "gpon_flow.ko"

# XPON IGMP
load_module "xpon_igmp.ko"

# PON VLAN
load_module "ponvlan.ko"

# PON MAC Filter
load_module "ponmacfilter.ko"

# ==============================================================
# STEP 3: Hardware NAT (Performance)
# ==============================================================
log_info "=== Loading Hardware NAT ==="

load_module "hw_nat.ko"
load_module "swnat.ko"

# ==============================================================
# STEP 4: WiFi Modules (Optional)
# ==============================================================
log_info "=== Loading WiFi Modules ==="

# MediaTek MT7916 WiFi 6 Driver
load_module "mt7916_ap.ko"
load_module "mt_whnat.ko"

# ==============================================================
# STEP 5: Miscellaneous
# ==============================================================
log_info "=== Loading Misc Modules ==="

load_module "tcledctrl.ko"
load_module "module_sel.ko"
load_module "nlk_msg.ko"
load_module "sif.ko"

# ==============================================================
# STEP 6: Bring up PON Interface
# ==============================================================
log_info "=== Configuring PON Interface ==="

# Bring up PON interface
if [ -e "/sys/class/net/pon" ]; then
    ifconfig pon up
    log_info "PON interface is UP"
else
    log_warn "PON interface not found"
fi

# Bring up OMCI interface (for GPON)
if [ -e "/sys/class/net/omci" ]; then
    ifconfig omci up
    log_info "OMCI interface is UP"
fi

# ==============================================================
# STEP 7: Start PON Manager
# ==============================================================
log_info "=== Starting PON Manager ==="

if [ -x "/usr/bin/ponmgr" ]; then
    /usr/bin/ponmgr &
    log_info "PON Manager started"
else
    log_warn "PON Manager not found"
fi

log_info "=== GPON Module Loading Complete ==="
