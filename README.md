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

Flash แล้วบอกผลด้วยครับ! 🤞​​​​​​​​​​​​​​​​
