import season
import datetime
import json
import os

class Controller(wiz.controller("view")):
    def __startup__(self, wiz):
        super().__startup__(wiz)
        if wiz.session.has("id") == False:
            wiz.response.redirect("/")

        wiz.response.data.set(session=wiz.session.get())
        
        menu = []
        if wiz.session.get("role") == "admin":
            menu.append({ 'title': 'Admin', 'url': '/admin' })
        menu.append({ 'title': 'Logout', 'url': '/auth/logout' })
        self.set_menu(profile=menu)

        menu = []
        menu.append({ 'title': 'Apps', 'url': '/hub/apps', 'icon': 'fa-solid fa-cube' })
        menu.append({ 'title': 'Workflow', 'url': '/hub/workflow', 'icon': 'fa-solid fa-cubes' })
        menu.append({ 'title': 'Dataset', 'url': '/hub/dataset', 'icon': 'fa-solid fa-database' })
        menu.append({ 'title': 'Storage', 'url': '/hub/storage', 'icon': 'fa-solid fa-folder-tree' })
        menu.append({ 'title': 'Kernels', 'url': '/hub/kernels', 'icon': 'fa-solid fa-microchip' })
        self.set_menu(main=menu)
        