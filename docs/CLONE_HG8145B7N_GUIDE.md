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

---

## คำสั่งที่ทดสอบแล้วว่าใช้งานได้จริง

### Tools ที่ใช้ (อยู่ใน /userfs/bin/)

| Tool | คำสั่ง | หน้าที่ |
|------|--------|---------|
| **ponmgr** | `ponmgr gpon set sn` | ตั้ง SN ได้ผลทันที |
| **tcapi** | `tcapi set/get/commit/save` | ตั้งค่าและบันทึกถาวร |
| **omcicfgCmd** | `omcicfgCmd get sn/loid` | ตรวจสอบค่า |

---

## วิธีที่ 1: คำสั่งที่ใช้งานได้จริง (ทดสอบแล้ว)

```bash
# ===== ขั้นตอนที่ 1: ตั้ง GPON Serial Number =====

# ผ่าน ponmgr (ได้ผลทันที)
ponmgr gpon set sn HWTC 286f3db5

# ผ่าน tcapi (สำหรับบันทึกถาวร)
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5"
tcapi set GPON_ONU VendorId "HWTC"

# ===== ขั้นตอนที่ 2: ตั้ง LOID =====

tcapi set GPON_LOIDAuth LOID "8806480495"
tcapi set GPON_LOIDAuth Password ""

# ===== ขั้นตอนที่ 3: บันทึกถาวร =====

tcapi commit GPON_ONU
tcapi commit GPON_LOIDAuth
tcapi save

# ===== ขั้นตอนที่ 4: ตรวจสอบ =====

omcicfgCmd get sn
omcicfgCmd get loid
ponmgr gpon get info
```

---

## วิธีที่ 2: ใช้ Script สำเร็จรูป

```bash
# ดาวน์โหลดและรัน script
/userfs/bin/clone_hg8145b7n.sh

# หรือสร้างเอง:
cat > /tmp/clone.sh << 'EOF'
#!/bin/sh
ponmgr gpon set sn HWTC 286f3db5
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5"
tcapi set GPON_ONU VendorId "HWTC"
tcapi set GPON_LOIDAuth LOID "8806480495"
tcapi set GPON_LOIDAuth Password ""
tcapi commit GPON_ONU
tcapi commit GPON_LOIDAuth
tcapi save
echo "Done! Check: ponmgr gpon get info"
EOF
chmod +x /tmp/clone.sh
/tmp/clone.sh
```

---

## ตรวจสอบสถานะ

```bash
# ดู ONU info
ponmgr gpon get info

# ดู SN และ LOID
omcicfgCmd get sn
omcicfgCmd get loid

# ดู interface
ifconfig pon
ifconfig ppp0
```

### ผลลัพธ์ที่ถูกต้อง

```
ONU Info:
 ONU ID:    1          <-- ต้องเป็น 1 (ไม่ใช่ 255)
 ONU State: O5         <-- ต้องเป็น O5 (Operation)
 SN:        HWTC286f3db5
```

---

## สถานะ ONU

| State | ความหมาย |
|-------|----------|
| O1 | Initial state (ยังไม่ลงทะเบียน) |
| O2 | Standby state |
| O3 | Serial number state |
| O4 | Ranging state |
| **O5** | **Operation state (ลงทะเบียนสำเร็จ!)** |
| O6 | POPUP state |
| O7 | Emergency stop |

---

## Table Names ที่ถูกต้อง

| Table | ใช้สำหรับ |
|-------|-----------|
| `GPON_ONU` | SerialNumber, VendorId |
| `GPON_LOIDAuth` | LOID, Password |

**หมายเหตุ**: `GPON_Common` และ `Info_GPON` ใช้ไม่ได้บน firmware นี้

---

## MAC Address

MAC Address (`E0:AE:A2:EF:B1:CD`) จะถูกตั้งอัตโนมัติจาก hardware ของ T626 Pro
ไม่ต้องตั้งค่าแยก - ระบบจะใช้ MAC ของ pon interface

```bash
# ดู MAC ปัจจุบัน
ifconfig pon | grep HWaddr
```

---

## Troubleshooting

### ONU State ยังเป็น O1

1. ตรวจสอบสาย fiber เสียบถูกต้อง
2. ถอด ONU เดิม (HG8145B7N) ออกก่อน
3. รอ 1-2 นาทีให้ OLT รู้จัก SN ใหม่
4. ลอง `reboot`

### ดู LOS Status

```bash
cat /proc/tc3162/los_status
# 0 = มี signal, 1 = ไม่มี signal
```

---

## สรุปคำสั่งสั้นๆ

```bash
# Clone แบบถาวร (ครบทุกขั้นตอน)
ponmgr gpon set sn HWTC 286f3db5 && \
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5" && \
tcapi set GPON_ONU VendorId "HWTC" && \
tcapi set GPON_LOIDAuth LOID "8806480495" && \
tcapi commit GPON_ONU && \
tcapi commit GPON_LOIDAuth && \
tcapi save && \
ponmgr gpon get info
```

---

## แหล่งข้อมูล

- Config file: `configs/gpon_clone_hg8145b7n.conf`
- Clone script: `scripts/clone_hg8145b7n.sh`
