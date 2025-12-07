# HG8145B7N → T626 Pro Clone Reference

## Source Device: Huawei HG8145B7N-AIS

### Device Information
| Parameter | Value |
|-----------|-------|
| Model Name | HG8145B7N-AIS |
| Device Type | HG8145B7N |
| Description | OptiXstar HG8145B7N GPON Terminal (CLASS B+/PRODUCT ID:2150087381LDR7001564) |
| MAC Address | E0:AE:A2:EF:B1:CD |
| Serial Number (Hex) | 48575443286F3DB5 |
| Serial Number (ASCII) | HWTC286F3DB5 |
| Vendor ID | HWTC |
| Hardware Version | 39E7.A |
| Software Version | V5R023C10S104 |
| Software Sub-version | 1.0 |
| Manufacture Info | 2150087381LDR7001564.C402 |
| ONT Registration Status | O5 (Operation state) |
| ONT ID | 1 |
| Custom Info | AIS |
| LOID | 8806480495 |

### Serial Number Breakdown
```
Full SN (Hex): 48575443286F3DB5
├── Vendor ID (ASCII): HWTC (48 57 54 43)
└── Serial Part: 286F3DB5 (28 6F 3D B5)

Full SN (ASCII): HWTC286F3DB5
├── Vendor: HWTC (Huawei Technologies Co.)
└── Serial: 286F3DB5
```

---

## Clone Commands for T626 Pro

### Quick One-Liner (Full Clone + ACS Disable)
```bash
tcapi set Cwmp_Entry Active "No" && tcapi commit Cwmp_Entry && \
ponmgr gpon set sn HWTC 286f3db5 && \
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5" && \
tcapi set GPON_ONU VendorId "HWTC" && \
tcapi set GPON_ONU EquipmentId "HG8145B7N" && \
tcapi set GPON_LOIDAuth LOID "8806480495" && \
tcapi set GPON_LOIDAuth Password "" && \
tcapi commit GPON_ONU && \
tcapi commit GPON_LOIDAuth && \
tcapi save && \
ponmgr gpon get info
```

### Step-by-Step Commands

#### 1. Disable ACS/TR-069
```bash
tcapi set Cwmp_Entry Active "No"
tcapi set Cwmp_Entry ACS_URL ""
tcapi set Cwmp_Entry Inform_Enable "No"
tcapi commit Cwmp_Entry
```

#### 2. Set GPON Serial Number
```bash
# Immediate effect
ponmgr gpon set sn HWTC 286f3db5

# Persistent
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5"
tcapi set GPON_ONU VendorId "HWTC"
tcapi commit GPON_ONU
```

#### 3. Set LOID Authentication
```bash
tcapi set GPON_LOIDAuth LOID "8806480495"
tcapi set GPON_LOIDAuth Password ""
tcapi commit GPON_LOIDAuth
```

#### 4. Set Equipment Info (Optional)
```bash
tcapi set GPON_ONU EquipmentId "HG8145B7N"
tcapi set GPON_ONU OmciSwVer1 "V5R023C10S104"
tcapi set GPON_ONU OmciSwVer2 "V5R023C10S104"
tcapi set GPON_ONU HWVer "39E7.A"
tcapi set GPON_ONU OMCCVersion "163"
tcapi commit GPON_ONU
```

#### 5. Save & Reboot
```bash
tcapi save
reboot
```

---

## Verification Commands

```bash
# Check GPON status
ponmgr gpon get info

# Check Serial Number
omcicfgCmd get sn

# Check LOID
omcicfgCmd get loid

# Check all GPON settings
tcapi get GPON_ONU
tcapi get GPON_LOIDAuth

# Check ACS status
tcapi get Cwmp_Entry Active
```

### Expected Output After Clone
```
ONU State: O5
PON SN: HWTC286f3db5
LOID: 8806480495
```

---

## GPON ONU States Reference

| State | Name | Description |
|-------|------|-------------|
| O1 | Initial | Starting up |
| O2 | Standby | Waiting for upstream |
| O3 | Serial Number | Authentication in progress |
| O4 | Ranging | Distance measurement |
| **O5** | **Operation** | **SUCCESS - Connected** |
| O6 | POPUP | Intermittent |
| O7 | Emergency Stop | Error state |

---

## Troubleshooting

### Stuck at O3
1. ตรวจสอบว่า ONU เดิม (HG8145B7N) ปิดแล้ว
2. รอ 5-10 นาทีให้ OLT clear session
3. ตรวจสอบ LOID ถูกต้อง
4. Reboot T626 Pro

### Stuck at O1
1. ตรวจสอบสาย fiber
2. ตรวจสอบ SN format ถูกต้อง
3. `ponmgr gpon set state disable && sleep 2 && ponmgr gpon set state enable`

### ACS Reset ค่า
1. Disable ACS ก่อน clone
2. `tcapi set Cwmp_Entry Active "No" && tcapi commit Cwmp_Entry`

---

## Important Notes

- **ต้องปิด ONU เดิม** ก่อน clone เพราะ OLT ไม่รับ SN ซ้ำ
- **LOID** เป็นค่าเฉพาะของแต่ละ account
- **MAC Address** ไม่จำเป็นต้อง clone (T626 Pro ใช้ MAC ตัวเอง)
- **ACS** ควร disable เพื่อไม่ให้ ISP reset ค่า
