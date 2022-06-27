# vkbasalt.py
#
# Copyright 2022 Hari Rana <theevilskeleton@riseup.net>
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

import os
from gi.repository import Gtk, GLib, Adw
from bottles.backend.utils.vkbasalt import parse
from bottles.backend.utils.manager import ManagerUtils

class VkBasaltSettings:
    default = False
    effects = False
    output = False
    disable_on_launch = False
    toggle_key = False
    cas_sharpness = False
    dls_sharpness = False
    dls_denoise = False
    fxaa_subpixel_quality = False
    fxaa_quality_edge_threshold = False
    fxaa_quality_edge_threshold_min = False
    smaa_edge_detection = False
    smaa_threshold = False
    smaa_max_search_steps = False
    smaa_max_search_steps_diagonal = False
    smaa_corner_rounding = False
    lut_file_path = False
    exec = False

@Gtk.Template(resource_path='/com/usebottles/bottles/dialog-vkbasalt.ui')
class VkBasaltDialog(Adw.Window):
    __gtype_name__ = 'VkBasaltDialog'

    # region Widgets
    default = Gtk.Template.Child()
    cas = Gtk.Template.Child()
    dls = Gtk.Template.Child()
    fxaa = Gtk.Template.Child()
    smaa = Gtk.Template.Child()

    # disable_on_launch = Gtk.Template.Child()
    # toggle_key = Gtk.Template.Child()
    cas_sharpness = Gtk.Template.Child()
    # dls_sharpness = Gtk.Template.Child()
    # dls_denoise = Gtk.Template.Child()
    # fxaa_subpixel_quality = Gtk.Template.Child()
    # fxaa_quality_edge_threshold = Gtk.Template.Child()
    # fxaa_quality_edge_threshold_min = Gtk.Template.Child()
    # smaa_edge_detection = Gtk.Template.Child()
    # smaa_threshold = Gtk.Template.Child()
    # smaa_max_search_steps = Gtk.Template.Child()
    # smaa_max_search_steps_diagonal = Gtk.Template.Child()
    # smaa_corner_rounding = Gtk.Template.Child()
    # lut_file_path = Gtk.Template.Child()
    # output = Gtk.Template.Child()
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


    def __update(self, config):

        parameters = config["Parameters"]
        self.default.set_text(str(parameters["default"]))

    def __idle_save(self, *args):

        config = ManagerUtils.get_bottle_path(self.config)

        print(self.cas.get_enable_expansion())
        print(Gtk.Adjustment.get_value(self.cas_sharpness))

        # Applies default settings and closes dialog.
        if self.default.get_state() is True:
            VkBasaltSettings.default = True
            config = os.path.join(config, "vkBasalt.conf")
            if os.path.isfile(config):
                os.remove(config)
            parse(VkBasaltSettings)
            self.destroy()
            return

        # Checks filter settings.
        if self.cas.get_state() is True or self.dls.get_state() is True or self.fxaa.get_state() is True or self.smaa.get_state() is True:
            effects = []
            if self.cas.get_state() is True:
                effects.append("cas")
            if self.dls.get_state() is True:
                effects.append("dls")
            if self.fxaa.get_state() is True:
                effects.append("fxaa")
            if self.smaa.get_state() is True:
                effects.append("smaa")

        VkBasaltSettings.effects = tuple(effects)

        VkBasaltSettings.output = config

        parse(VkBasaltSettings)
        self.destroy()

    def __save(self, *args):
        GLib.idle_add(self.__idle_save)

    def __close_window(self, *args):
        self.destroy()


