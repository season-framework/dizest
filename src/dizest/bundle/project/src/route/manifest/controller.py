fs = wiz.workspace("service").fs("config")
config = fs.read.json("config.json", {})

if 'title' not in config:
    config['title'] = "DIZEST"

manifest = dict()
manifest['name'] = config['title']
manifest['short_name'] = config['title']
manifest['start_url'] = '/'
manifest['icons'] = [
    {
        "src": "/brand/icon",
        "sizes": "192x192",
        "type": "image/png"
    },
    {
        "src": "/brand/icon",
        "sizes": "512x512",
        "type": "image/png"
    }
]

manifest['theme_color'] = '#3843d0'
manifest['background_color'] = '#3843d0'
manifest['display'] = 'standalone'
manifest['orientation'] = 'any'

wiz.response.json(manifest)