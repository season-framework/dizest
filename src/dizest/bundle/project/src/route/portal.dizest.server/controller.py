config = wiz.model("portal/dizest/config")
KernelClass = wiz.model("portal/dizest/kernel")

kernel_id = config.kernel_id()

if wiz.request.match("/dizest/server/check") is not None:
    kernel = KernelClass.getInstance(kernel_id)
    if kernel is None:
        wiz.response.status(200, 'stop')
    wiz.response.status(200, kernel.status())

if wiz.request.match("/dizest/server/start") is not None:
    spec = wiz.request.query()

    kernelConfig = dict()
    kernelConfig['kernel_id'] = kernel_id
    kernelConfig['spec'] = spec
    kernelConfig['cwd'] = config.cwd()
    kernelConfig['user'] = config.user()
    kernelConfig['socket'] = config.socket()
    
    kernel = KernelClass.createInstance(**kernelConfig)
    kernel.set(spec=spec)
    kernel.start()
    wiz.response.status(200, kernel.status())

if wiz.request.match("/dizest/server/stop") is not None:
    kernel = KernelClass.getInstance(kernel_id)
    if kernel is None:
        wiz.response.status(200, 'stop')
    kernel.stop()
    wiz.response.status(200, kernel.status())

if wiz.request.match("/dizest/server/kernels") is not None:
    specs = KernelClass.specs()
    wiz.response.status(200, specs)

wiz.response.status(404)