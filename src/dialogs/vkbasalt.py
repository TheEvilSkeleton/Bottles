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

    disable_on_launch = Gtk.Template.Child()
    # toggle_key = Gtk.Template.Child()
    cas_sharpness = Gtk.Template.Child()
    dls_sharpness = Gtk.Template.Child()
    dls_denoise = Gtk.Template.Child()
    fxaa_subpixel_quality = Gtk.Template.Child()
    fxaa_quality_edge_threshold = Gtk.Template.Child()
    fxaa_quality_edge_threshold_min = Gtk.Template.Child()
    # smaa_edge_detection = Gtk.Template.Child()
    smaa_threshold = Gtk.Template.Child()
    smaa_max_search_steps = Gtk.Template.Child()
    smaa_max_search_steps_diagonal = Gtk.Template.Child()
    smaa_corner_rounding = Gtk.Template.Child()
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

        config = os.path.join(ManagerUtils.get_bottle_path(self.config), "vkBasalt.conf")

        if os.path.isfile(config):
            VkBasaltSettings = ParseConfig(config)

            if "cas" not in VkBasaltSettings.effects:
                self.cas.set_enable_expansion(False)
            if "dls" not in VkBasaltSettings.effects:
                self.dls.set_enable_expansion(False)
            if "fxaa" not in VkBasaltSettings.effects:
                self.fxaa.set_enable_expansion(False)
            if "smaa" not in VkBasaltSettings.effects:
                self.smaa.set_enable_expansion(False)

            try:
                if VkBasaltSettings.casSharpness:
                    self.cas_sharpness.set_value(float(VkBasaltSettings.casSharpness))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.dlsSharpness:
                    self.dls_sharpness.set_value(float(VkBasaltSettings.dlsSharpness))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.dlsDenoise:
                    self.dls_denoise.set_value(float(VkBasaltSettings.dlsDenoise))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.fxaaQualitySubpix:
                    self.fxaa_subpixel_quality.set_value(float(VkBasaltSettings.fxaaQualitySubpix))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.fxaaQualityEdgeThreshold:
                    self.fxaa_quality_edge_threshold.set_value(float(VkBasaltSettings.fxaaQualityEdgeThreshold))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.fxaaQualityEdgeThresholdMin:
                    self.fxaa_quality_edge_threshold_min.set_value(float(VkBasaltSettings.fxaaQualityEdgeThresholdMin))
            except AttributeError:
                pass
            # try:
            #     if VkBasaltSettings.smaaEdgeDetection:
            #         self.smaa_edge_detection.set_value(float(VkBasaltSettings.smaaEdgeDetection))
            # except AttributeError:
            #     pass
            try:
                if VkBasaltSettings.smaaThreshold:
                    self.smaa_threshold.set_value(float(VkBasaltSettings.smaaThreshold))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.smaaMaxSearchSteps:
                    self.smaa_max_search_steps.set_value(float(VkBasaltSettings.smaaMaxSearchSteps))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.smaaMaxSearchStepsDiag:
                    self.smaa_max_search_steps_diagonal.set_value(float(VkBasaltSettings.smaaMaxSearchStepsDiag))
            except AttributeError:
                pass
            try:
                if VkBasaltSettings.smaaCornerRounding:
                    self.smaa_corner_rounding.set_value(float(VkBasaltSettings.smaaCornerRounding))
            except AttributeError:
                pass
            if VkBasaltSettings.enableOnLaunch == "False":
                self.disable_on_launch.set_state(True)
        else:
            self.default.set_state(True)

    def __update(self, config):

        parameters = config["Parameters"]
        # self.default.set_text(str(parameters["default"]))

    def __idle_save(self, *args):

        config = ManagerUtils.get_bottle_path(self.config)

        # Applies default settings and closes dialog.
        if self.default.get_state() is True:
            VkBasaltSettings.default = True
            VkBasaltSettings.output = False
            config = os.path.join(config, "vkBasalt.conf")
            if os.path.isfile(config):
                os.remove(config)
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
                # VkBasaltSettings.smaa_edge_detection = Gtk.Adjustment.get_value(self.smaa_edge_detection)
                VkBasaltSettings.smaa_corner_rounding = Gtk.Adjustment.get_value(self.smaa_corner_rounding)
                VkBasaltSettings.smaa_max_search_steps = Gtk.Adjustment.get_value(self.smaa_max_search_steps)
                VkBasaltSettings.smaa_max_search_steps_diagonal = Gtk.Adjustment.get_value(self.smaa_max_search_steps_diagonal)

            VkBasaltSettings.disable_on_launch = self.disable_on_launch.get_state()

        VkBasaltSettings.effects = tuple(effects)

        VkBasaltSettings.output = config

        parse(VkBasaltSettings)
        self.destroy()

    def __save(self, *args):
        GLib.idle_add(self.__idle_save)

    def __close_window(self, *args):
        self.destroy()

