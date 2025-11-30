import http.client
import json
    
    
    
    
    
def send_sms(phone, message):
    conn = http.client.HTTPSConnection("api.sms.ir")
    payload = json.dumps({
    "lineNumber": "30002101005709",
    "messageText": message,
    "mobiles": [
        phone,
    ],
    "sendDateTime": None
    })
    headers = {
    'X-API-KEY': '2z6bzhAL0rEjgJLJO3UnZYo2gFBdajuT6ha8narWTHyPcJ3o',
    'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/send/bulk", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    
    