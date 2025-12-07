#!/bin/sh
#
# Clone HG8145B7N → T626 Pro
# คำสั่งที่ทดสอบแล้วว่าใช้งานได้จริง
#
# Usage: ./clone_hg8145b7n.sh
#

# ===== ค่าจาก HG8145B7N =====
GPON_SN="HWTC286F3DB5"
VENDOR_ID="HWTC"
LOID="8806480495"
LOID_PASSWORD=""
# MAC จะถูกตั้งอัตโนมัติจาก hardware

echo "=========================================="
echo "  Clone HG8145B7N → T626 Pro"
echo "=========================================="
echo ""

# ===== ขั้นตอนที่ 1: ตั้ง GPON Serial Number =====
echo "[1/4] Setting GPON Serial Number..."

# ผ่าน ponmgr (ได้ผลทันที)
ponmgr gpon set sn HWTC 286f3db5
echo "      ponmgr: OK"

# ผ่าน tcapi (สำหรับบันทึกถาวร)
tcapi set GPON_ONU SerialNumber "$GPON_SN"
tcapi set GPON_ONU VendorId "$VENDOR_ID"
echo "      tcapi GPON_ONU: OK"

# ===== ขั้นตอนที่ 2: ตั้ง LOID =====
echo "[2/4] Setting LOID..."

tcapi set GPON_LOIDAuth LOID "$LOID"
tcapi set GPON_LOIDAuth Password "$LOID_PASSWORD"
echo "      tcapi GPON_LOIDAuth: OK"

# ===== ขั้นตอนที่ 3: Commit และ Save =====
echo "[3/4] Saving configuration (persistent)..."

tcapi commit GPON_ONU
tcapi commit GPON_LOIDAuth
tcapi save
echo "      tcapi save: OK"

# ===== ขั้นตอนที่ 4: ตรวจสอบ =====
echo "[4/4] Verifying..."
echo ""

echo "--- Current Settings ---"
echo "SN:   $(omcicfgCmd get sn 2>/dev/null | grep 'ONU SN' || tcapi get GPON_ONU SerialNumber)"
echo "LOID: $(omcicfgCmd get loid 2>/dev/null | grep 'loid' || tcapi get GPON_LOIDAuth LOID)"
echo ""

echo "--- ONU Status ---"
ponmgr gpon get info | head -10
echo ""

echo "=========================================="
echo "  Clone Complete!"
echo "=========================================="
echo ""
echo "ถ้า ONU State เป็น O5 = ลงทะเบียนสำเร็จ"
echo "ถ้า ONU State เป็น O1 = รอสักครู่หรือ reboot"
echo ""
