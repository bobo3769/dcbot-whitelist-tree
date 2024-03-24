import json

wlsttree = {}
try:
    with open("treedata.json", "r") as f:
        wlsttree = json.load(f)
except FileNotFoundError:
    print('tree file not fond')
    pass
except json.decoder.JSONDecodeError:
    print('file empty')

mcwhitelist = []
try:
    with open("whitelist.json", "r") as f:
        mcwhitelist = json.load(f)
except FileNotFoundError:
    print('mc whitelist file not fond')
    pass
except json.decoder.JSONDecodeError:
    print('file empty')

def save_mcwhitelist():
    with open("whitelist.json", 'w') as file:
        json.dump(mcwhitelist, file, indent=2)

#嘗試加入白名單
def try_addwhitelist(dcid):
    try:
        if wlsttree[dcid]['in_whitelist'] == 1 and wlsttree[dcid]['mcid'] != None and wlsttree[dcid]['uuid'] != None:
            uuid, mcid = str(wlsttree[dcid]['uuid']), str(wlsttree[dcid]['mcid'])
            formatted_uuid = (
                uuid[:8] + "-" +
                uuid[8:12] + "-" +
                uuid[12:16] + "-" +
                uuid[16:20] + "-" +
                uuid[20:]
            )
            mcdata = {"uuid": formatted_uuid,"name": mcid}
            mcwhitelist.append(mcdata)
    except:
        print(f'將{dcid}加入白名單失敗')

for dcid in wlsttree:
    try_addwhitelist(dcid)

print(mcwhitelist)

save_mcwhitelist()
print('已儲存為whitelist.json，可拿去給minecraft伺服器使用')