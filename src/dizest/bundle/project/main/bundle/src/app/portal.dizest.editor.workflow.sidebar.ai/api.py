import requests

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl()
fs = wiz.fs()
llmconfig = fs.read.json("dizest.json", {})
keys = ['use_ai', 'llm_gateway', 'llm_api_key', 'llm_model']
for key in keys:
    if key not in llmconfig or llmconfig[key] == '' or llmconfig[key] is None:
        llmconfig[key] = config[key]
        
def llmRequest(text, context):
    api_host = llmconfig["llm_gateway"]
    api_key = llmconfig["llm_api_key"]
    model = llmconfig["llm_model"]

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": context
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ],
        "max_tokens": 4096
    }

    response = requests.post(api_host + "/chat/completions", headers=headers, json=payload)
    response = response.json()
    
    try:
        return response["choices"][0]['message']["content"]
    except:
        return response["error"]['message']

def request():
    query = wiz.request.query("query", True)
    context = wiz.request.query("context", "")
    resp = llmRequest(query, context)
    wiz.response.status(200, resp)
