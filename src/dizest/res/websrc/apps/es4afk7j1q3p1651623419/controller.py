if wiz.request.segment.mode is None:
    wiz.response.redirect("/hub/drive/local")

MODE = wiz.request.segment.mode
kwargs['mode'] = MODE