# คู่มือ Clone GPON จาก Huawei HG8145B7N ไปยัง T626 Pro

## ข้อมูล ONU ต้นทาง

| Parameter | Value |
|-----------|-------|
| Model | HG8145B7N-AIS |
| GPON SN (hex) | 48575443286F3DB5 |
| GPON SN (decoded) | HWTC286F3DB5 |
| **LOID** | **8806480495** |
| Vendor ID | HWTC (Huawei) |
| MAC Address | E0:AE:A2:EF:B1:CD |
| Hardware Version | 39E7.A |
| Software Version | V5R023C10S104 |
| Manufacture Info | 2150087381LDR7001564.C402 |

---

## วิธีที่ 1: ใช้คำสั่ง tcapi (แนะนำ)

```bash
# 1. ดูค่าปัจจุบันก่อน
tcapi get GPON_Common GPON_SN
tcapi get GPON_Common PON_MAC
tcapi get GPON_Common VendorID

# 2. ตั้งค่า GPON Serial Number
tcapi set GPON_Common GPON_SN "HWTC286F3DB5"
tcapi set Info_GPON GPON_SN "HWTC286F3DB5"

# 3. ตั้งค่า PON MAC Address
tcapi set GPON_Common PON_MAC "E0:AE:A2:EF:B1:CD"
tcapi set Info_GPON PON_MAC "E0:AE:A2:EF:B1:CD"

# 4. ตั้งค่า Vendor ID (HWTC = Huawei)
tcapi set GPON_Common VendorID "HWTC"
tcapi set Info_GPON VendorID "HWTC"

# 5. ตั้งค่า Equipment ID
tcapi set GPON_Common EquipmentID "HG8145B7N"
tcapi set Info_GPON EquipmentID "HG8145B7N"

# 6. ตั้งค่า LOID
tcapi set GPON_Common LOID "8806480495"
tcapi set Info_GPON LOID "8806480495"

# 7. บันทึกการเปลี่ยนแปลง
tcapi commit GPON_Common
tcapi commit Info_GPON
tcapi save

# 8. Restart PON interface
ifconfig pon down
sleep 2
ifconfig pon up

# 9. ตรวจสอบผลลัพธ์
tcapi get GPON_Common GPON_SN
tcapi get GPON_Common PON_MAC
cat /proc/tc3162/pon_status
```

---

## วิธีที่ 2: ใช้ gpon_clone script

```bash
# Clone ทั้งหมดพร้อม restart
gpon_clone -s HWTC286F3DB5 \
           -l 8806480495 \
           -m E0:AE:A2:EF:B1:CD \
           -v HWTC \
           -e HG8145B7N \
           -R

# ตรวจสอบค่าที่ตั้ง
gpon_clone -c
```

---

## วิธีที่ 3: เขียนค่าผ่าน /proc โดยตรง

```bash
# เขียน GPON SN
echo "HWTC286F3DB5" > /proc/tc3162/gpon_sn

# เขียน PON MAC
echo "E0:AE:A2:EF:B1:CD" > /proc/tc3162/pon_mac

# ตรวจสอบ
cat /proc/tc3162/gpon_sn
cat /proc/tc3162/pon_mac
```

---

## Script สำเร็จรูป

สร้างไฟล์ `/tmp/clone_hg8145b7n.sh`:

```bash
#!/bin/sh
# Clone HG8145B7N to T626 Pro

echo "=== Cloning HG8145B7N GPON Profile ==="

# Set GPON SN
tcapi set GPON_Common GPON_SN "HWTC286F3DB5"
echo "[OK] GPON_SN = HWTC286F3DB5"

# Set LOID
tcapi set GPON_Common LOID "8806480495"
echo "[OK] LOID = 8806480495"

# Set MAC
tcapi set GPON_Common PON_MAC "E0:AE:A2:EF:B1:CD"
echo "[OK] PON_MAC = E0:AE:A2:EF:B1:CD"

# Set Vendor ID
tcapi set GPON_Common VendorID "HWTC"
echo "[OK] VendorID = HWTC"

# Set Equipment ID
tcapi set GPON_Common EquipmentID "HG8145B7N"
echo "[OK] EquipmentID = HG8145B7N"

# Commit and save
tcapi commit GPON_Common
tcapi save
echo "[OK] Settings saved"

# Restart PON
echo "Restarting PON interface..."
ifconfig pon down && sleep 2 && ifconfig pon up
echo "[OK] PON restarted"

# Verify
echo ""
echo "=== Verification ==="
tcapi get GPON_Common GPON_SN
tcapi get GPON_Common PON_MAC
tcapi get GPON_Common VendorID
tcapi get GPON_Common EquipmentID

echo ""
echo "=== Clone Complete ==="
```

---

## ตรวจสอบสถานะหลัง Clone

```bash
# ตรวจสอบ PON Status
cat /proc/tc3162/pon_status

# ตรวจสอบ OMCI Status
cat /proc/tc3162/omci_status

# ตรวจสอบ Registration
tcapi get GPON_Common ONUState
```

### สถานะ ONU ที่คาดหวัง

| State | ความหมาย |
|-------|----------|
| O1 | Initial state |
| O2 | Standby state |
| O3 | Serial number state |
| O4 | Ranging state |
| O5 | **Operation state** (ปกติ - ลงทะเบียนสำเร็จ) |
| O6 | POPUP state |
| O7 | Emergency stop |

---

## หมายเหตุสำคัญ

1. **LOID**: ค่า LOID ที่ใช้คือ `8806480495`

2. **SN Format**:
   - Hex: `48575443286F3DB5`
   - ASCII: `HWTC286F3DB5` (ใช้แบบนี้)

3. **ถ้าไม่ Online**: ตรวจสอบว่า OLT ของ AIS ต้องการ parameter อื่นเพิ่มเติมหรือไม่

---

## แหล่งข้อมูล

- Config file: `/home/user/tclinux_T3_T626Pro_True/configs/gpon_clone_hg8145b7n.conf`
- Clone script: `/home/user/tclinux_T3_T626Pro_True/hybrid_build/scripts/gpon_clone_ais.sh`
