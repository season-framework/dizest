dconfig = wiz.model("portal/dizest/dconfig")
uWebClass = wiz.model("portal/dizest/uweb")

if wiz.request.match("/dizest/server/check") is not None:
    try:
        uweb = uWebClass()
        status = uweb.status()
    except:
        status = 'stop'
    wiz.response.status(200, status)

if wiz.request.match("/dizest/server/start") is not None:
    try:
        uweb = uWebClass()
        kernelspec = wiz.request.query()
        uWebClass = wiz.model("portal/dizest/uweb")
        uweb = uWebClass()
        uweb.kernel(kernelspec)
        uweb.start()
    except Exception as e:
        wiz.response.status(500, uweb.status())
    wiz.response.status(200, uweb.status())

if wiz.request.match("/dizest/server/stop") is not None:
    try:
        uweb = uWebClass()
        uWebClass = wiz.model("portal/dizest/uweb")
        uweb = uWebClass()
        uweb.stop()
    except:
        wiz.response.status(500, uweb.status())
    wiz.response.status(200, uweb.status())

if wiz.request.match("/dizest/server/kernels") is not None:
    data = dconfig.kernel()
    wiz.response.status(200, data)

wiz.response.status(404)