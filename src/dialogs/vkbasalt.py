# vkbasalt.py
#
# Copyright 2022 Bottles
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from gi.repository import Gtk, GLib, Adw


@Gtk.Template(resource_path='/com/usebottles/bottles/dialog-vkbasalt.ui')
class vkBasaltDialog(Adw.Window):
    __gtype_name__ = 'vkBasaltDialog'

    # region Widgets
    arg_w = Gtk.Template.Child()
    arg_h = Gtk.Template.Child()
    arg_W = Gtk.Template.Child()
    arg_H = Gtk.Template.Child()
    arg_fps = Gtk.Template.Child()
    arg_fps_no_focus = Gtk.Template.Child()
    switch_scaling = Gtk.Template.Child()
    toggle_borderless = Gtk.Template.Child()
    toggle_fullscreen = Gtk.Template.Child()
    btn_save = Gtk.Template.Child()
    btn_cancel = Gtk.Template.Child()

    # endregion

    def __init__(self, window, config, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(window)

        # common variables and references
        self.window = window
        self.manager = window.manager
        self.config = config

        # connect signals
        self.btn_save.connect("clicked", self.__save)
        self.btn_cancel.connect("clicked", self.__close_window)


    def __change_wtype(self, widget, wtype):
        self.toggle_borderless.handler_block_by_func(self.__change_wtype)
        self.toggle_fullscreen.handler_block_by_func(self.__change_wtype)
        if wtype == "b":
            self.toggle_fullscreen.set_active(False)
            self.toggle_borderless.set_active(True)
        elif wtype == "f":
            self.toggle_fullscreen.set_active(True)
            self.toggle_borderless.set_active(False)

        self.toggle_borderless.handler_unblock_by_func(self.__change_wtype)
        self.toggle_fullscreen.handler_unblock_by_func(self.__change_wtype)

    def __update(self, config):
        self.toggle_borderless.handler_block_by_func(self.__change_wtype)
        self.toggle_fullscreen.handler_block_by_func(self.__change_wtype)

        parameters = config["Parameters"]

    def __idle_save(self, *args):
        settings = {"vkbasalt_game_width": int(self.arg_w.get_text()),
                    "vkbasalt_game_height": int(self.arg_h.get_text()),
                    "vkbasalt_window_width": int(self.arg_W.get_text()),
                    "vkbasalt_window_height": int(self.arg_H.get_text()),
                    "vkbasalt_fps": int(self.arg_fps.get_text()),
                    "vkbasalt_fps_no_focus": int(self.arg_fps_no_focus.get_text()),
                    "vkbasalt_scaling": self.switch_scaling.get_state(),
                    "vkbasalt_borderless": self.toggle_borderless.get_active(),
                    "vkbasalt_fullscreen": self.toggle_fullscreen.get_active()}

        for setting in settings.keys():
            self.manager.update_config(
                config=self.config,
                key=setting,
                value=settings[setting],
                scope="Parameters"
            )

        self.destroy()

    def __save(self, *args):
        GLib.idle_add(self.__idle_save)

    def __close_window(self, *args):
        self.destroy()


