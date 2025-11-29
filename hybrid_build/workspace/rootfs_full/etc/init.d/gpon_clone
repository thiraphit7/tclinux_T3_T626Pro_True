#!/bin/sh /etc/rc.common
#
# GPON Clone Init Script
# Loads cloned GPON credentials at boot
#
# Install: cp gpon_clone_init.sh /etc/init.d/gpon_clone
#          /etc/init.d/gpon_clone enable
#

START=98
STOP=10

CLONE_CONFIG="/etc/gpon_clone.conf"
TCAPI_BIN="/usr/bin/tcapi"
PONMGR_BIN="/usr/bin/ponmgr"

log() {
    logger -t gpon_clone "$1"
    echo "gpon_clone: $1"
}

load_config() {
    if [ -f "$CLONE_CONFIG" ]; then
        . "$CLONE_CONFIG"
        return 0
    fi
    return 1
}

apply_gpon_settings() {
    log "Applying GPON clone settings..."

    # Load config
    if ! load_config; then
        log "No clone config found at $CLONE_CONFIG"
        return 1
    fi

    # Apply GPON Serial Number
    if [ -n "$GPON_SN" ]; then
        log "Setting GPON SN: $GPON_SN"
        if [ -x "$TCAPI_BIN" ]; then
            $TCAPI_BIN set GPON_Common GPON_SN "$GPON_SN"
            $TCAPI_BIN set Info_GPON GPON_SN "$GPON_SN"
        fi
        if [ -f "/proc/tc3162/gpon_sn" ]; then
            echo "$GPON_SN" > /proc/tc3162/gpon_sn
        fi
    fi

    # Apply LOID
    if [ -n "$LOID" ]; then
        log "Setting LOID: $LOID"
        if [ -x "$TCAPI_BIN" ]; then
            $TCAPI_BIN set GPON_Common LOID "$LOID"
            $TCAPI_BIN set Info_GPON LOID "$LOID"
        fi
    fi

    # Apply LOID Password
    if [ -n "$LOID_PASSWORD" ]; then
        log "Setting LOID Password"
        if [ -x "$TCAPI_BIN" ]; then
            $TCAPI_BIN set GPON_Common LOIDPassword "$LOID_PASSWORD"
        fi
    fi

    # Apply PON MAC
    if [ -n "$PON_MAC" ]; then
        log "Setting PON MAC: $PON_MAC"
        if [ -x "$TCAPI_BIN" ]; then
            $TCAPI_BIN set GPON_Common PON_MAC "$PON_MAC"
        fi
        if [ -f "/proc/tc3162/pon_mac" ]; then
            echo "$PON_MAC" > /proc/tc3162/pon_mac
        fi
    fi

    # Apply Vendor ID
    if [ -n "$VENDOR_ID" ]; then
        log "Setting Vendor ID: $VENDOR_ID"
        if [ -x "$TCAPI_BIN" ]; then
            $TCAPI_BIN set GPON_Common VendorID "$VENDOR_ID"
        fi
    fi

    # Apply Equipment ID
    if [ -n "$EQUIPMENT_ID" ]; then
        log "Setting Equipment ID: $EQUIPMENT_ID"
        if [ -x "$TCAPI_BIN" ]; then
            $TCAPI_BIN set GPON_Common EquipmentID "$EQUIPMENT_ID"
        fi
    fi

    # Commit changes
    if [ -x "$TCAPI_BIN" ]; then
        $TCAPI_BIN commit GPON_Common
        $TCAPI_BIN save
    fi

    log "GPON clone settings applied"
}

start() {
    log "Starting GPON Clone service..."
    apply_gpon_settings
}

stop() {
    log "GPON Clone service stopped"
}

restart() {
    stop
    start

    # Restart PON interface
    if [ -e "/sys/class/net/pon" ]; then
        log "Restarting PON interface..."
        ifconfig pon down
        sleep 2
        ifconfig pon up
    fi
}

status() {
    echo "=== GPON Clone Status ==="

    if [ -f "$CLONE_CONFIG" ]; then
        echo "Config file: $CLONE_CONFIG"
        echo ""
        cat "$CLONE_CONFIG"
    else
        echo "No clone config found"
    fi

    echo ""
    echo "=== Current GPON Settings ==="

    if [ -x "$TCAPI_BIN" ]; then
        echo "GPON_SN: $($TCAPI_BIN get GPON_Common GPON_SN 2>/dev/null)"
        echo "LOID: $($TCAPI_BIN get GPON_Common LOID 2>/dev/null)"
        echo "PON_MAC: $($TCAPI_BIN get GPON_Common PON_MAC 2>/dev/null)"
        echo "VendorID: $($TCAPI_BIN get GPON_Common VendorID 2>/dev/null)"
        echo "EquipmentID: $($TCAPI_BIN get GPON_Common EquipmentID 2>/dev/null)"
        echo "ONUState: $($TCAPI_BIN get GPON_Common ONUState 2>/dev/null)"
    fi
}
