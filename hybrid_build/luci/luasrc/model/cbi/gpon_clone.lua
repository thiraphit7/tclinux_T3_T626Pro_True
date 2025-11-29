--[[
LuCI CBI Model for GPON Clone
Path: /usr/lib/lua/luci/model/cbi/gpon_clone.lua
]]--

local sys = require "luci.sys"
local fs = require "nixio.fs"

m = Map("gpon_clone", translate("GPON Clone for AIS"),
    translate("Clone/Spoof GPON Serial Number, LOID, and MAC Address for AIS Fiber."))

-- Status Section
s = m:section(TypedSection, "status", translate("Current Status"))
s.anonymous = true

-- Display current values
local gpon_sn = sys.exec("tcapi get GPON_Common GPON_SN 2>/dev/null"):gsub("\n", "") or "N/A"
local loid = sys.exec("tcapi get GPON_Common LOID 2>/dev/null"):gsub("\n", "") or "N/A"
local pon_mac = sys.exec("tcapi get GPON_Common PON_MAC 2>/dev/null"):gsub("\n", "") or "N/A"
local onu_state = sys.exec("tcapi get GPON_Common ONUState 2>/dev/null"):gsub("\n", "") or "N/A"

s:option(DummyValue, "_gpon_sn", translate("Current GPON SN")).value = gpon_sn
s:option(DummyValue, "_loid", translate("Current LOID")).value = loid
s:option(DummyValue, "_pon_mac", translate("Current PON MAC")).value = pon_mac
s:option(DummyValue, "_onu_state", translate("ONU State")).value = onu_state

-- Clone Settings Section
s = m:section(TypedSection, "clone", translate("Clone Settings"))
s.anonymous = true
s.addremove = false

-- GPON Serial Number
o = s:option(Value, "gpon_sn", translate("GPON Serial Number"),
    translate("12-16 characters. Format: VENDORID + Serial (e.g., ZTEGC1234567)"))
o.datatype = "string"
o.rmempty = false
o.placeholder = "ZTEGC1234567"

-- LOID
o = s:option(Value, "loid", translate("LOID (Logical ONU ID)"),
    translate("Your AIS LOID number"))
o.datatype = "string"
o.rmempty = true
o.placeholder = "1234567890"

-- LOID Password
o = s:option(Value, "loid_password", translate("LOID Password"),
    translate("LOID password if required"))
o.datatype = "string"
o.password = true
o.rmempty = true

-- PON MAC Address
o = s:option(Value, "pon_mac", translate("PON MAC Address"),
    translate("Format: AA:BB:CC:DD:EE:FF"))
o.datatype = "macaddr"
o.rmempty = true
o.placeholder = "AA:BB:CC:DD:EE:FF"

-- Vendor ID
o = s:option(ListValue, "vendor_id", translate("Vendor ID"))
o:value("ZTEG", "ZTEG (ZTE)")
o:value("HWTC", "HWTC (Huawei)")
o:value("ALCL", "ALCL (Alcatel)")
o:value("GPON", "GPON (Generic)")
o.default = "ZTEG"

-- Equipment ID
o = s:option(Value, "equipment_id", translate("Equipment ID"),
    translate("Model name reported to OLT"))
o.datatype = "string"
o.rmempty = true
o.placeholder = "ZXHN_F670L"

-- Apply Button
s = m:section(TypedSection, "apply", translate("Apply Changes"))
s.anonymous = true

o = s:option(Button, "_apply", translate("Apply and Restart PON"))
o.inputtitle = translate("Apply Now")
o.inputstyle = "apply"
function o.write(self, section)
    -- Write config file
    local config = string.format([[
# GPON Clone Config - Auto Generated
GPON_SN="%s"
LOID="%s"
LOID_PASSWORD="%s"
PON_MAC="%s"
VENDOR_ID="%s"
EQUIPMENT_ID="%s"
]],
        m:formvalue("cbid.gpon_clone.clone.gpon_sn") or "",
        m:formvalue("cbid.gpon_clone.clone.loid") or "",
        m:formvalue("cbid.gpon_clone.clone.loid_password") or "",
        m:formvalue("cbid.gpon_clone.clone.pon_mac") or "",
        m:formvalue("cbid.gpon_clone.clone.vendor_id") or "ZTEG",
        m:formvalue("cbid.gpon_clone.clone.equipment_id") or ""
    )

    fs.writefile("/etc/gpon_clone.conf", config)

    -- Apply settings
    sys.exec("/etc/init.d/gpon_clone restart")
end

return m
