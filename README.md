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
