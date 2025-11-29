--[[
LuCI Controller for GPON Clone
Path: /usr/lib/lua/luci/controller/gpon_clone.lua
]]--

module("luci.controller.gpon_clone", package.seeall)

function index()
    entry({"admin", "network", "gpon_clone"}, cbi("gpon_clone"), _("GPON Clone"), 90)
    entry({"admin", "network", "gpon_clone", "status"}, call("action_status"), nil)
    entry({"admin", "network", "gpon_clone", "apply"}, call("action_apply"), nil)
end

function action_status()
    local sys = require "luci.sys"
    local http = require "luci.http"

    local status = {}

    -- Get current GPON settings
    status.gpon_sn = sys.exec("tcapi get GPON_Common GPON_SN 2>/dev/null"):gsub("\n", "")
    status.loid = sys.exec("tcapi get GPON_Common LOID 2>/dev/null"):gsub("\n", "")
    status.pon_mac = sys.exec("tcapi get GPON_Common PON_MAC 2>/dev/null"):gsub("\n", "")
    status.vendor_id = sys.exec("tcapi get GPON_Common VendorID 2>/dev/null"):gsub("\n", "")
    status.equipment_id = sys.exec("tcapi get GPON_Common EquipmentID 2>/dev/null"):gsub("\n", "")
    status.onu_state = sys.exec("tcapi get GPON_Common ONUState 2>/dev/null"):gsub("\n", "")

    -- Check PON interface
    status.pon_up = sys.exec("ifconfig pon 2>/dev/null | grep -c 'UP'"):gsub("\n", "")

    http.prepare_content("application/json")
    http.write_json(status)
end

function action_apply()
    local sys = require "luci.sys"
    local http = require "luci.http"

    -- Restart PON interface to apply changes
    sys.exec("ifconfig pon down && sleep 2 && ifconfig pon up")

    http.prepare_content("application/json")
    http.write_json({success = true, message = "PON interface restarted"})
end
