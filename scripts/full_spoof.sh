#!/bin/sh
# =============================================================================
# Full HG8145B7N Clone Spoof Script for T626 Pro
# Vendor: HWTC, SN: HWTC286F3DB5, LOID: 8806480495
# Includes: ACS disable, GPON spoof, persistent save
# =============================================================================

echo "=========================================="
echo "  HG8145B7N Full Clone Spoof"
echo "=========================================="

# -----------------------------------------------------------------------------
# Step 1: Disable ACS (TR-069 Auto Configuration Server)
# -----------------------------------------------------------------------------
echo "[1/5] Disabling ACS/TR-069..."

tcapi set Cwmp_Entry Active "No"
tcapi set Cwmp_Entry ACS_URL ""
tcapi set Cwmp_Entry ACS_UserName ""
tcapi set Cwmp_Entry ACS_Password ""
tcapi set Cwmp_Entry Inform_Enable "No"
tcapi set Cwmp_Entry Inform_Interval "0"
tcapi set Cwmp_Entry ConnectionRequestUserName ""
tcapi set Cwmp_Entry ConnectionRequestPassword ""
tcapi commit Cwmp_Entry

# Alternative method if Cwmp_Entry doesn't work
tcapi set TR069_Entry Active "No" 2>/dev/null
tcapi set TR069_Entry ACS_URL "" 2>/dev/null
tcapi commit TR069_Entry 2>/dev/null

echo "    ACS disabled"

# -----------------------------------------------------------------------------
# Step 2: Set GPON Serial Number (Vendor + Serial)
# -----------------------------------------------------------------------------
echo "[2/5] Setting GPON Serial Number..."

# Method 1: ponmgr (immediate effect)
ponmgr gpon set sn HWTC 286f3db5

# Method 2: tcapi (persistent)
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5"
tcapi set GPON_ONU VendorId "HWTC"
tcapi commit GPON_ONU

echo "    SN: HWTC286F3DB5"

# -----------------------------------------------------------------------------
# Step 3: Set LOID Authentication
# -----------------------------------------------------------------------------
echo "[3/5] Setting LOID Authentication..."

tcapi set GPON_LOIDAuth LOID "8806480495"
tcapi set GPON_LOIDAuth Password ""
tcapi commit GPON_LOIDAuth

echo "    LOID: 8806480495"

# -----------------------------------------------------------------------------
# Step 4: Set Equipment ID and Version Info (Optional - for full clone)
# -----------------------------------------------------------------------------
echo "[4/5] Setting Equipment Info..."

tcapi set GPON_ONU EquipmentId "HG8145B7N" 2>/dev/null
tcapi set GPON_ONU OmciSwVer1 "V5R023C10S104" 2>/dev/null
tcapi set GPON_ONU OmciSwVer2 "V5R023C10S104" 2>/dev/null
tcapi set GPON_ONU HWVer "39E7.A" 2>/dev/null
tcapi set GPON_ONU OMCCVersion "163" 2>/dev/null
tcapi commit GPON_ONU 2>/dev/null

echo "    EquipmentId: HG8145B7N"

# -----------------------------------------------------------------------------
# Step 5: Save All Changes Persistently
# -----------------------------------------------------------------------------
echo "[5/5] Saving configuration..."

tcapi save

echo ""
echo "=========================================="
echo "  Configuration Complete!"
echo "=========================================="

# -----------------------------------------------------------------------------
# Verify Configuration
# -----------------------------------------------------------------------------
echo ""
echo "Verifying settings:"
echo "-------------------"

echo ""
echo "GPON Info:"
ponmgr gpon get info

echo ""
echo "LOID:"
omcicfgCmd get loid 2>/dev/null || tcapi get GPON_LOIDAuth LOID

echo ""
echo "ACS Status:"
tcapi get Cwmp_Entry Active 2>/dev/null || echo "Cwmp_Entry not found"

echo ""
echo "=========================================="
echo "  Reboot required for full effect"
echo "  Run: reboot"
echo "=========================================="
