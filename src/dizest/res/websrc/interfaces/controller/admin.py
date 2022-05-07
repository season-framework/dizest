import season
import datetime
import json
import os

class Controller(wiz.controller("user")):
    def __startup__(self, wiz):
        super().__startup__(wiz)
        if wiz.session.get("role") != 'admin':
            wiz.response.redirect("/")

        wiz.response.data.set(session=wiz.session.get())
        
        menu = []
        menu.append({ 'title': 'Hub', 'url': '/hub' })
        menu.append({ 'title': 'Logout', 'url': '/auth/logout' })
        self.set_menu(profile=menu)

        menu = []
        menu.append({ 'title': 'Dashboard', 'url': '/admin/dashboard', 'icon': 'fa-solid fa-gauge-simple' })
        menu.append({ 'title': 'Setting', 'url': '/admin/setting', 'icon': 'fa-solid fa-cogs' })
        menu.append({ 'title': 'Users', 'url': '/admin/users', 'icon': 'fa-solid fa-users' })
        menu.append({ 'title': 'Kernel', 'url': '/admin/kernel', 'icon': 'fa-solid fa-microchip' })
        menu.append({ 'title': 'Packages', 'url': '/admin/packages', 'icon': 'fa-solid fa-boxes-packing' })
        self.set_menu(main=menu)
        