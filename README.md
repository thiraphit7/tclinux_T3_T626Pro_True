# tclinux_T3_T626Pro_True
```xml
<Entry0 Active="Yes" username="superadmin" web_passwd="n#$32*77($E4p*P" display_mask="FF FF FF FF FF BF FF FF FF" pwd_control="1" Logged="0" Logoff="0" LoginIp="192.168.51.10" /> 
<Entry0 Enable="1" Username="superadmin" Alias="superadmin" Password="n#$32*77($E4p*P" RmtAccCap="0" /> 
```

```bash

sed -i 's/VendorId="T3TH"/VendorId="HWTC"/g' /tmp/ctromfile.cfg
sed -i 's/SerialNumber="T3TH6572C8A2"/SerialNumber="HWTC286F3DB5"/g' /tmp/ctromfile.cfg
sed -i 's/EquipmentId="PT632"/EquipmentId="HG8145B7N"/g' /tmp/ctromfile.cfg
sed -i 's/OMCCVersion="96"/OMCCVersion="160"/g' /tmp/ctromfile.cfg

sed -i 's/LOID="2407486479"/LOID="8806480495"/g' /tmp/ctromfile.cfg

sed -i 's/<OLT VendorId="ZTEG"/<OLT VendorId="HWTC"/g' /tmp/ctromfile.cfg

sed -i 's/WAN_MAC="00:aa:bb:cc:dd:ee"/WAN_MAC="E0:AE:A2:EF:B1:CD"/g' /tmp/ctromfile.cfg
sed -i 's/AL-MAC="64:20:e1:72:c8:a2"/AL-MAC="e0:ae:a2:ef:b1:cd"/g' /tmp/ctromfile.cfg

sed -i 's/wan_telnet_enable="0"/wan_telnet_enable="1"/g' /tmp/ctromfile.cfg
sed -i 's/<TelnetEntry Active="No" telnet_username="admin" telnet_passwd="[^"]*" telnet_port="[^"]*"/<TelnetEntry Active="Yes" telnet_username="admin" telnet_passwd="16122516" telnet_port="23"/g' /tmp/ctromfile.cfg

sed -i 's/web_passwd="[^"]*"/web_passwd="16122516"/g' /tmp/ctromfile.cfg
sed -i 's/Username="superadmin" Alias="superadmin" Password="[^"]*"/Username="superadmin" Alias="superadmin" Password="16122516"/g' /tmp/ctromfile.cfg

sed -i 's/Tr069Enable="1"/Tr069Enable="0"/g' /tmp/ctromfile.cfg
sed -i 's/periodActive="Yes"/periodActive="No"/g' /tmp/ctromfile.cfg
sed -i 's/<Entry Active="Yes" periodInterval="3600"/<Entry Active="No" periodInterval="3600"/g' /tmp/ctromfile.cfg
```
48575443286F3DB5

# แก้ไข Telnet Entry และปิด TR069​​​​​​​​​​​​​​​​

# ✅ อัปเดตเรียบร้อย!

## สรุปค่าทั้งหมดที่แก้ไข

|Parameter              |ค่าเดิม            |ค่าใหม่                |
|-----------------------|-----------------|---------------------|
|**ONU VendorId**       |T3TH             |**HWTC**             |
|**SerialNumber**       |T3TH6572C8A2     |**HWTC286F3DB5**     |
|**EquipmentId**        |PT632            |**HG8145B7N**        |
|**OMCCVersion**        |96               |**160**              |
|**LOID**               |2407486479       |**8806480495**       |
|**OLT VendorId**       |ZTEG             |**HWTC**             |
|**WAN_MAC**            |00:aa:bb:cc:dd:ee|**E0:AE:A2:EF:B1:CD**|
|**AL-MAC**             |64:20:e1:72:c8:a2|**e0:ae:a2:ef:b1:cd**|
|**WAN Telnet**         |0                |**1**                |
|**superadmin password**|7*![%K27Nkd$_r4  |**16122516**         |
|**Telnet Active**      |No               |**Yes**              |
|**Telnet Username**    |admin            |**admin**            |
|**Telnet Password**    |$O(Li0_o)$!%^    |**16122516**         |
|**Telnet Port**        |22666            |**23**               |
|**TR069 Enable**       |1                |**0**                |
|**TR069 periodActive** |Yes              |**No**               |
|**TR069 Active**       |Yes              |**No**               |

-----

## ดาวน์โหลดไฟล์

[ดาวน์โหลด mtd1_ais_clone.bin](computer:///mnt/user-data/outputs/mtd1_ais_clone.bin)

-----

## วิธี Flash

```bash
ECNT> loadx 0x81800000
# (ส่งไฟล์ผ่าน Xmodem)

ECNT> flash erase 0x80000 0x40000
ECNT> flash write 0x80000 0x40000 0x81800000
ECNT> reset
```

-----

## หลัง Reboot

**Telnet:**

```bash
telnet 192.168.1.1 23
```

- Username: `admin`
- Password: `16122516`

**Web Interface:**

- Username: `superadmin`
- Password: `16122516`

**TR069:** ปิดแล้ว ❌

-----

Flash แล้วบอกผลด้วย# พบคำสั่ง prolinecmd ทั้งหมดแล้ว!

จากภาพเห็นคำสั่งที่สำคัญสำหรับ GPON Clone:

## คำสั่งตั้งค่า GPON ทั้งหมด

```bash
# 1. ตั้ง Serial Number
prolinecmd xponsn set HWTC286F3DB5

# 2. ตั้ง Vendor ID
prolinecmd VendorID set HWTC

# 3. ตั้ง GPON Registration ID (PLOAM Password)
prolinecmd GponRegId set 2150087381LDR7001564

# 4. ตั้ง Hardware Version
prolinecmd hwver set 39E7.A

# 5. ตั้ง Product Class
prolinecmd productclass set HG8145B7N

# 6. ตั้ง Manufacturer OUI
prolinecmd manufacturerOUI set HWTC
```

-----

## หลังตั้งค่าเสร็จ

```bash
# Save
prolinecmd save

# หรือ
cfgmgr save

# Reboot
reboot
```

-----

## ตรวจสอบค่าที่ตั้ง

```bash
# ดูค่าปัจจุบัน
prolinecmd xponsn get
prolinecmd VendorID get
prolinecmd GponRegId get
```

-----

# คำสั่ง tcapi ทั้งหมด

```bash
# ===== GPON ONU Identity =====
tcapi set GPON_ONU VendorId "HWTC"
tcapi set GPON_ONU SerialNumber "HWTC286F3DB5"
tcapi set GPON_ONU EquipmentId "HG8145B7N"
tcapi set GPON_ONU OMCCVersion "160"

# ===== LOID =====
tcapi set GPON_LOIDAuth LOID "8806480495"

# ===== OLT Vendor =====
tcapi set GPON_OLT VendorId "HWTC"

# ===== MAC Address =====
tcapi set Mac WAN_MAC "E0:AE:A2:EF:B1:CD"
tcapi set mapcfg AL-MAC "e0:ae:a2:ef:b1:cd"

# ===== Telnet Enable =====
tcapi set Firewall wan_telnet_enable "1"
tcapi set TelnetEntry Active "Yes"
tcapi set TelnetEntry telnet_username "admin"
tcapi set TelnetEntry telnet_passwd "16122516"
tcapi set TelnetEntry telnet_port "23"

# ===== Superadmin Password =====
tcapi set Account0 web_passwd "16122516"
tcapi set Account0 Password "16122516"

# ===== Disable TR069 =====
tcapi set Cwmp Tr069Enable "0"
tcapi set Cwmp periodActive "No"
tcapi set Cwmp Active "No"

# ===== Save & Reboot =====
tcapi save
reboot
```

-----

## สรุป

|Parameter   |คำสั่ง tcapi                                       |
|------------|------------------------------------------------|
|VendorId    |`tcapi set GPON_ONU VendorId "HWTC"`            |
|SerialNumber|`tcapi set GPON_ONU SerialNumber "HWTC286F3DB5"`|
|EquipmentId |`tcapi set GPON_ONU EquipmentId "HG8145B7N"`    |
|OMCCVersion |`tcapi set GPON_ONU OMCCVersion "160"`          |
|LOID        |`tcapi set GPON_LOIDAuth LOID "8806480495"`     |
|OLT VendorId|`tcapi set GPON_OLT VendorId "HWTC"`            |
|WAN_MAC     |`tcapi set Mac WAN_MAC "E0:AE:A2:EF:B1:CD"`     |
|Telnet      |`tcapi set TelnetEntry Active "Yes"`            |
|TR069       |`tcapi set Cwmp Tr069Enable "0"`                |

-----

## One-liner (Copy ทั้งหมด)

```bash
tcapi set GPON_ONU VendorId "HWTC" && tcapi set GPON_ONU SerialNumber "HWTC286F3DB5" && tcapi set GPON_ONU EquipmentId "HG8145B7N" && tcapi set GPON_ONU OMCCVersion "160" && tcapi set GPON_LOIDAuth LOID "8806480495" && tcapi set GPON_OLT VendorId "HWTC" && tcapi set Mac WAN_MAC "E0:AE:A2:EF:B1:CD" && tcapi set Firewall wan_telnet_enable "1" && tcapi set TelnetEntry Active "Yes" && tcapi set TelnetEntry telnet_username "admin" && tcapi set TelnetEntry telnet_passwd "16122516" && tcapi set TelnetEntry telnet_port "23" && tcapi set Cwmp Tr069Enable "0" && tcapi set Cwmp periodActive "No" && tcapi set Cwmp Active "No" && tcapi save && reboot
```

-----

ลองรันแล้วบอกผลด้วยครับ! 🤞​​​​​​​​​​​​​​​​

