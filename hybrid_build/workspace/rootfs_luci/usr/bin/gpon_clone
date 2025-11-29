#!/bin/sh
#
# GPON Clone Script for AIS Fiber
# Clone/Spoof GPON SN, LOID, MAC Address
#
# Usage: ./gpon_clone_ais.sh [options]
#
# For educational and authorized testing purposes only!
#

CONFIG_FILE="/tmp/gpon_clone.conf"
TCAPI_BIN="/usr/bin/tcapi"
PONMGR_BIN="/usr/bin/ponmgr"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# AIS Default Parameters
AIS_VENDOR_ID="ZTEG"
AIS_EQUIPMENT_ID="ZXHN_F670L"
AIS_OMCC_VERSION="0xA3"

print_banner() {
    echo ""
    echo "=================================================="
    echo "  GPON Clone Tool for AIS Fiber"
    echo "  T626 Pro Hybrid Firmware"
    echo "=================================================="
    echo ""
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --sn <GPON_SN>       Set GPON Serial Number (e.g., ZTEGC1234567)"
    echo "  -l, --loid <LOID>        Set Logical ONU ID"
    echo "  -p, --password <PASS>    Set LOID Password"
    echo "  -m, --mac <MAC>          Set PON MAC Address (e.g., AA:BB:CC:DD:EE:FF)"
    echo "  -v, --vendor <VENDOR>    Set Vendor ID (default: ZTEG)"
    echo "  -e, --equip <EQUIP_ID>   Set Equipment ID (default: ZXHN_F670L)"
    echo "  -r, --restore            Restore original values"
    echo "  -c, --current            Show current GPON settings"
    echo "  -h, --help               Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 -s ZTEGC1234567 -l 1234567890 -p password123"
    echo "  $0 --sn ZTEGC1234567 --loid 1234567890 --mac AA:BB:CC:DD:EE:FF"
    echo "  $0 -c     # Show current settings"
    echo ""
}

# Get current GPON settings using tcapi
get_current_settings() {
    log_info "=== Current GPON Settings ==="
    echo ""

    if [ -x "$TCAPI_BIN" ]; then
        echo -e "${CYAN}GPON Serial Number:${NC}"
        $TCAPI_BIN get GPON_Common GPON_SN 2>/dev/null || echo "  (not available)"

        echo -e "${CYAN}LOID:${NC}"
        $TCAPI_BIN get GPON_Common LOID 2>/dev/null || echo "  (not available)"

        echo -e "${CYAN}LOID Password:${NC}"
        $TCAPI_BIN get GPON_Common LOIDPassword 2>/dev/null || echo "  (not available)"

        echo -e "${CYAN}PON MAC Address:${NC}"
        $TCAPI_BIN get GPON_Common PON_MAC 2>/dev/null || echo "  (not available)"

        echo -e "${CYAN}Vendor ID:${NC}"
        $TCAPI_BIN get GPON_Common VendorID 2>/dev/null || echo "  (not available)"

        echo -e "${CYAN}Equipment ID:${NC}"
        $TCAPI_BIN get GPON_Common EquipmentID 2>/dev/null || echo "  (not available)"

        echo -e "${CYAN}ONU State:${NC}"
        $TCAPI_BIN get GPON_Common ONUState 2>/dev/null || echo "  (not available)"
    else
        # Alternative: read from /proc or nvram
        echo "Reading from /proc/tc3162/..."

        if [ -f "/proc/tc3162/gpon_sn" ]; then
            echo -e "${CYAN}GPON SN:${NC} $(cat /proc/tc3162/gpon_sn)"
        fi

        if [ -f "/proc/tc3162/gpon_loid" ]; then
            echo -e "${CYAN}LOID:${NC} $(cat /proc/tc3162/gpon_loid)"
        fi

        if [ -f "/proc/tc3162/pon_mac" ]; then
            echo -e "${CYAN}PON MAC:${NC} $(cat /proc/tc3162/pon_mac)"
        fi
    fi

    echo ""
}

# Validate GPON Serial Number format
validate_gpon_sn() {
    SN=$1
    # GPON SN format: 4 chars vendor + 8 chars serial (e.g., ZTEGC1234567)
    if [ ${#SN} -ne 12 ] && [ ${#SN} -ne 16 ]; then
        log_error "Invalid GPON SN format. Expected 12 or 16 characters."
        log_info "Example: ZTEGC1234567 or ZTEGC12345678901"
        return 1
    fi
    return 0
}

# Validate MAC address format
validate_mac() {
    MAC=$1
    echo "$MAC" | grep -qE "^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
    if [ $? -ne 0 ]; then
        log_error "Invalid MAC address format. Expected: AA:BB:CC:DD:EE:FF"
        return 1
    fi
    return 0
}

# Backup current settings
backup_settings() {
    log_info "Backing up current settings..."

    BACKUP_FILE="/tmp/gpon_backup_$(date +%Y%m%d_%H%M%S).conf"

    if [ -x "$TCAPI_BIN" ]; then
        echo "# GPON Backup - $(date)" > $BACKUP_FILE
        echo "GPON_SN=$($TCAPI_BIN get GPON_Common GPON_SN 2>/dev/null)" >> $BACKUP_FILE
        echo "LOID=$($TCAPI_BIN get GPON_Common LOID 2>/dev/null)" >> $BACKUP_FILE
        echo "LOIDPassword=$($TCAPI_BIN get GPON_Common LOIDPassword 2>/dev/null)" >> $BACKUP_FILE
        echo "PON_MAC=$($TCAPI_BIN get GPON_Common PON_MAC 2>/dev/null)" >> $BACKUP_FILE
        echo "VendorID=$($TCAPI_BIN get GPON_Common VendorID 2>/dev/null)" >> $BACKUP_FILE
        echo "EquipmentID=$($TCAPI_BIN get GPON_Common EquipmentID 2>/dev/null)" >> $BACKUP_FILE

        log_info "Backup saved to: $BACKUP_FILE"
    fi
}

# Set GPON Serial Number
set_gpon_sn() {
    SN=$1
    log_info "Setting GPON Serial Number: $SN"

    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN set GPON_Common GPON_SN "$SN"
        # Also set in different locations for compatibility
        $TCAPI_BIN set Info_GPON GPON_SN "$SN"
    fi

    # Write to proc if available
    if [ -f "/proc/tc3162/gpon_sn" ]; then
        echo "$SN" > /proc/tc3162/gpon_sn
    fi

    # Use ponmgr if available
    if [ -x "$PONMGR_BIN" ]; then
        $PONMGR_BIN set sn "$SN" 2>/dev/null
    fi
}

# Set LOID (Logical ONU ID)
set_loid() {
    LOID=$1
    LOID_PASS=$2

    log_info "Setting LOID: $LOID"

    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN set GPON_Common LOID "$LOID"
        $TCAPI_BIN set Info_GPON LOID "$LOID"

        if [ -n "$LOID_PASS" ]; then
            log_info "Setting LOID Password"
            $TCAPI_BIN set GPON_Common LOIDPassword "$LOID_PASS"
            $TCAPI_BIN set Info_GPON LOIDPassword "$LOID_PASS"
        fi
    fi

    # Write to proc if available
    if [ -f "/proc/tc3162/gpon_loid" ]; then
        echo "$LOID" > /proc/tc3162/gpon_loid
    fi
}

# Set PON MAC Address
set_pon_mac() {
    MAC=$1
    log_info "Setting PON MAC Address: $MAC"

    # Convert to different formats
    MAC_NOCOLON=$(echo "$MAC" | tr -d ':')

    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN set GPON_Common PON_MAC "$MAC"
        $TCAPI_BIN set Info_GPON PON_MAC "$MAC"
    fi

    # Write to proc if available
    if [ -f "/proc/tc3162/pon_mac" ]; then
        echo "$MAC" > /proc/tc3162/pon_mac
    fi

    # Use ponmgr if available
    if [ -x "$PONMGR_BIN" ]; then
        $PONMGR_BIN set mac "$MAC" 2>/dev/null
    fi
}

# Set Vendor ID
set_vendor_id() {
    VENDOR=$1
    log_info "Setting Vendor ID: $VENDOR"

    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN set GPON_Common VendorID "$VENDOR"
        $TCAPI_BIN set Info_GPON VendorID "$VENDOR"
    fi
}

# Set Equipment ID
set_equipment_id() {
    EQUIP=$1
    log_info "Setting Equipment ID: $EQUIP"

    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN set GPON_Common EquipmentID "$EQUIP"
        $TCAPI_BIN set Info_GPON EquipmentID "$EQUIP"
    fi
}

# Apply and commit changes
apply_changes() {
    log_info "Applying changes..."

    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN commit GPON_Common
        $TCAPI_BIN save
    fi

    log_warn "Restart PON interface to apply changes..."
    log_info "Run: ifconfig pon down && sleep 2 && ifconfig pon up"
}

# Restart PON interface
restart_pon() {
    log_info "Restarting PON interface..."

    if [ -e "/sys/class/net/pon" ]; then
        ifconfig pon down
        sleep 2
        ifconfig pon up
        log_info "PON interface restarted"
    fi

    if [ -e "/sys/class/net/omci" ]; then
        ifconfig omci down
        sleep 1
        ifconfig omci up
        log_info "OMCI interface restarted"
    fi
}

# Clone complete profile for AIS
clone_ais_profile() {
    GPON_SN=$1
    LOID=$2
    LOID_PASS=$3
    PON_MAC=$4

    print_banner

    log_info "=== Cloning AIS GPON Profile ==="
    echo ""

    # Backup first
    backup_settings

    # Set AIS default vendor info
    set_vendor_id "$AIS_VENDOR_ID"
    set_equipment_id "$AIS_EQUIPMENT_ID"

    # Set user-provided values
    if [ -n "$GPON_SN" ]; then
        set_gpon_sn "$GPON_SN"
    fi

    if [ -n "$LOID" ]; then
        set_loid "$LOID" "$LOID_PASS"
    fi

    if [ -n "$PON_MAC" ]; then
        set_pon_mac "$PON_MAC"
    fi

    # Apply changes
    apply_changes

    echo ""
    log_info "=== Clone Complete ==="
    echo ""
    get_current_settings
}

# Main
main() {
    GPON_SN=""
    LOID=""
    LOID_PASS=""
    PON_MAC=""
    VENDOR_ID=""
    EQUIP_ID=""
    SHOW_CURRENT=0
    DO_RESTART=0

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            -s|--sn)
                GPON_SN="$2"
                shift 2
                ;;
            -l|--loid)
                LOID="$2"
                shift 2
                ;;
            -p|--password)
                LOID_PASS="$2"
                shift 2
                ;;
            -m|--mac)
                PON_MAC="$2"
                shift 2
                ;;
            -v|--vendor)
                VENDOR_ID="$2"
                shift 2
                ;;
            -e|--equip)
                EQUIP_ID="$2"
                shift 2
                ;;
            -c|--current)
                SHOW_CURRENT=1
                shift
                ;;
            -R|--restart)
                DO_RESTART=1
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Show current settings only
    if [ $SHOW_CURRENT -eq 1 ]; then
        print_banner
        get_current_settings
        exit 0
    fi

    # Validate inputs
    if [ -n "$GPON_SN" ]; then
        validate_gpon_sn "$GPON_SN" || exit 1
    fi

    if [ -n "$PON_MAC" ]; then
        validate_mac "$PON_MAC" || exit 1
    fi

    # Check if any value provided
    if [ -z "$GPON_SN" ] && [ -z "$LOID" ] && [ -z "$PON_MAC" ]; then
        print_banner
        log_error "No values provided. Use -h for help."
        echo ""
        show_help
        exit 1
    fi

    # Override vendor/equipment if provided
    if [ -n "$VENDOR_ID" ]; then
        AIS_VENDOR_ID="$VENDOR_ID"
    fi
    if [ -n "$EQUIP_ID" ]; then
        AIS_EQUIPMENT_ID="$EQUIP_ID"
    fi

    # Do the clone
    clone_ais_profile "$GPON_SN" "$LOID" "$LOID_PASS" "$PON_MAC"

    # Restart if requested
    if [ $DO_RESTART -eq 1 ]; then
        restart_pon
    fi
}

main "$@"
