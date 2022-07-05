# vkbasalt.py
#
# Copyright 2022 Hari Rana / TheEvilSkeleton <theevilskeleton@riseup.net>
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
from bottles.backend.utils.vkbasalt import parse, ParseConfig
from bottles.backend.utils.manager import ManagerUtils
from bottles.dialogs.filechooser import FileChooser  # pyright: reportMissingImports=false

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

    row_disable_on_launch = Gtk.Template.Child()
    switch_disable_on_launch = Gtk.Template.Child()
    # toggle_key = Gtk.Template.Child()
    cas_sharpness = Gtk.Template.Child()
    dls_sharpness = Gtk.Template.Child()
    dls_denoise = Gtk.Template.Child()
    fxaa_subpixel_quality = Gtk.Template.Child()
    fxaa_quality_edge_threshold = Gtk.Template.Child()
    fxaa_quality_edge_threshold_min = Gtk.Template.Child()
    # smaa_edge_detection = Gtk.Template.Child()
    luma = Gtk.Template.Child()
    color = Gtk.Template.Child()
    smaa_threshold = Gtk.Template.Child()
    smaa_max_search_steps = Gtk.Template.Child()
    smaa_max_search_steps_diagonal = Gtk.Template.Child()
    smaa_corner_rounding = Gtk.Template.Child()
    clut = Gtk.Template.Child()
    lut_file_path = Gtk.Template.Child()
    # output = Gtk.Template.Child()
    btn_save = Gtk.Template.Child()
    btn_cancel = Gtk.Template.Child()

    # endregion

    def __init__(self, parent_window, config, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(parent_window)

        # common variables and references
        self.window = parent_window
        self.manager = parent_window.manager
        self.config = config
        conf = os.path.join(ManagerUtils.get_bottle_path(self.config), "vkBasalt.conf")
        global smaa_edge_detection

        # connect signals
        self.btn_save.connect("clicked", self.__save)
        self.btn_cancel.connect("clicked", self.__close_window)
        self.default.connect("state-set", self.__default)
        self.luma.connect("toggled", self.__change_edge_detection_type, "luma")
        self.color.connect("toggled", self.__change_edge_detection_type, "color")
        self.lut_file_path.connect("clicked", self.__import_clut)

        if os.path.isfile(conf):
            VkBasaltSettings = ParseConfig(conf)

            if "cas" not in VkBasaltSettings.effects:
                self.cas.set_enable_expansion(False)
            if "dls" not in VkBasaltSettings.effects:
                self.dls.set_enable_expansion(False)
            if "fxaa" not in VkBasaltSettings.effects:
                self.fxaa.set_enable_expansion(False)
            if "smaa" not in VkBasaltSettings.effects:
                self.smaa.set_enable_expansion(False)
            if VkBasaltSettings.lut_file_path is None:
                self.clut.set_enable_expansion(False)

            if VkBasaltSettings.cas_sharpness != None:
                self.cas_sharpness.set_value(float(VkBasaltSettings.cas_sharpness))
            if VkBasaltSettings.dls_sharpness != None:
                self.dls_sharpness.set_value(float(VkBasaltSettings.dls_sharpness))
            if VkBasaltSettings.dls_denoise != None:
                self.dls_denoise.set_value(float(VkBasaltSettings.dls_denoise))
            if VkBasaltSettings.fxaa_subpixel_quality != None:
                self.fxaa_subpixel_quality.set_value(float(VkBasaltSettings.fxaa_subpixel_quality))
            if VkBasaltSettings.fxaa_quality_edge_threshold != None:
                self.fxaa_quality_edge_threshold.set_value(float(VkBasaltSettings.fxaa_quality_edge_threshold))
            if VkBasaltSettings.fxaa_quality_edge_threshold_min != None:
                self.fxaa_quality_edge_threshold_min.set_value(float(VkBasaltSettings.fxaa_quality_edge_threshold_min))
            if VkBasaltSettings.smaa_threshold != None:
                self.smaa_threshold.set_value(float(VkBasaltSettings.smaa_threshold))
            if VkBasaltSettings.smaa_max_search_steps != None:
                self.smaa_max_search_steps.set_value(float(VkBasaltSettings.smaa_max_search_steps))
            if VkBasaltSettings.smaa_max_search_steps_diagonal != None:
                self.smaa_max_search_steps_diagonal.set_value(float(VkBasaltSettings.smaa_max_search_steps_diagonal))
            if VkBasaltSettings.smaa_corner_rounding != None:
                self.smaa_corner_rounding.set_value(float(VkBasaltSettings.smaa_corner_rounding))
            if VkBasaltSettings.disable_on_launch == "True":
                self.switch_disable_on_launch.set_state(True)
            if VkBasaltSettings.smaa_edge_detection != None:
                if VkBasaltSettings.smaa_edge_detection == "color":
                    self.color.set_active(True)
                    smaa_edge_detection = "color"
                else:
                    smaa_edge_detection = "luma"
            else:
                smaa_edge_detection = "luma"
        else:
            self.default.set_state(True)
            smaa_edge_detection = "luma"
            self.cas.set_enable_expansion(False)
            self.dls.set_enable_expansion(False)
            self.fxaa.set_enable_expansion(False)
            self.smaa.set_enable_expansion(False)
            self.clut.set_enable_expansion(False)

    def __idle_save(self, *args):

        conf = ManagerUtils.get_bottle_path(self.config)

        # Applies default settings and closes dialog.
        if self.default.get_state() is True:
            VkBasaltSettings.default = True
            VkBasaltSettings.output = False
            conf = os.path.join(conf, "vkBasalt.conf")
            if os.path.isfile(conf):
                os.remove(conf)
            parse(VkBasaltSettings)
            self.destroy()
            return

        # Checks filter settings.
        if self.cas.get_enable_expansion() is True or self.dls.get_enable_expansion() is True or self.fxaa.get_enable_expansion() is True or self.smaa.get_enable_expansion() is True:
            VkBasaltSettings.default = False
            effects = []
            if self.cas.get_enable_expansion() is True:
                effects.append("cas")
                VkBasaltSettings.cas_sharpness = Gtk.Adjustment.get_value(self.cas_sharpness)
            if self.dls.get_enable_expansion() is True:
                effects.append("dls")
                VkBasaltSettings.dls_sharpness = Gtk.Adjustment.get_value(self.dls_sharpness)
                VkBasaltSettings.dls_denoise = Gtk.Adjustment.get_value(self.dls_denoise)
            if self.fxaa.get_enable_expansion() is True:
                effects.append("fxaa")
                VkBasaltSettings.fxaa_subpixel_quality = Gtk.Adjustment.get_value(self.fxaa_subpixel_quality)
                VkBasaltSettings.fxaa_quality_edge_threshold = Gtk.Adjustment.get_value(self.fxaa_quality_edge_threshold)
                VkBasaltSettings.fxaa_quality_edge_threshold_min = Gtk.Adjustment.get_value(self.fxaa_quality_edge_threshold_min)
            if self.smaa.get_enable_expansion() is True:
                effects.append("smaa")
                VkBasaltSettings.smaa_threshold = Gtk.Adjustment.get_value(self.smaa_threshold)
                VkBasaltSettings.smaa_edge_detection = smaa_edge_detection
                VkBasaltSettings.smaa_corner_rounding = Gtk.Adjustment.get_value(self.smaa_corner_rounding)
                VkBasaltSettings.smaa_max_search_steps = Gtk.Adjustment.get_value(self.smaa_max_search_steps)
                VkBasaltSettings.smaa_max_search_steps_diagonal = Gtk.Adjustment.get_value(self.smaa_max_search_steps_diagonal)

            VkBasaltSettings.disable_on_launch = self.switch_disable_on_launch.get_state()

        VkBasaltSettings.effects = tuple(effects)

        VkBasaltSettings.output = conf

        parse(VkBasaltSettings)
        self.destroy()

    def __save(self, *args):
        GLib.idle_add(self.__idle_save)

    def __close_window(self, *args):
        self.destroy()

    def __default(self, widget, state):
        self.cas.set_sensitive(not state)
        self.dls.set_sensitive(not state)
        self.fxaa.set_sensitive(not state)
        self.smaa.set_sensitive(not state)
        self.row_disable_on_launch.set_sensitive(not state)
        self.clut.set_sensitive(not state)

    def __change_edge_detection_type(self, widget, edge_detection_type):
        global smaa_edge_detection
        smaa_edge_detection = edge_detection_type
        self.luma.handler_block_by_func(self.__change_edge_detection_type)
        self.color.handler_block_by_func(self.__change_edge_detection_type)
        if edge_detection_type == "luma":
            self.color.set_active(False)
            self.luma.set_active(True)
        elif edge_detection_type == "color":
            self.color.set_active(True)
            self.luma.set_active(False)

        self.luma.handler_unblock_by_func(self.__change_edge_detection_type)
        self.color.handler_unblock_by_func(self.__change_edge_detection_type)

    def __import_clut(self, *args):
        def set_path(_dialog, response, _file_dialog):
            if response == -3:
                global file_path
                file_path = _file_dialog.get_file()
                # print(file_path.get_path())


        FileChooser(
            parent=self.window,
            title=_("Choose a configuration file"),
            action=Gtk.FileChooserAction.OPEN,
            buttons=(_("Cancel"), _("Import")),
            filters=["png", "CUBE"],
            callback=set_path
        )
