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

'''
Terminologies:
--------------
cas: Contrast Adaptive Sharpening
dls: Denoised Luma Sharpening
fxaa: Fast Approximate Anti-Aliasing
smaa: Subpixel Morphological Anti-Aliasing
clut (or lut): Color LookUp Table
'''

import os
from gi.repository import Gtk, GLib, Adw, Gdk
from bottles.backend.utils.vkbasalt import parse, ParseConfig
from bottles.backend.utils.manager import ManagerUtils
from bottles.dialogs.filechooser import FileChooser  # pyright: reportMissingImports=false
import logging

class vkbasalt_settings:
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
    switch_default = Gtk.Template.Child()
    expander_cas = Gtk.Template.Child()
    dls = Gtk.Template.Child()
    fxaa = Gtk.Template.Child()
    smaa = Gtk.Template.Child()
    spin_cas_sharpness = Gtk.Template.Child()
    dls_sharpness = Gtk.Template.Child()
    dls_denoise = Gtk.Template.Child()
    fxaa_subpixel_quality = Gtk.Template.Child()
    fxaa_quality_edge_threshold = Gtk.Template.Child()
    fxaa_quality_edge_threshold_min = Gtk.Template.Child()
    luma = Gtk.Template.Child()
    color = Gtk.Template.Child()
    smaa_threshold = Gtk.Template.Child()
    smaa_max_search_steps = Gtk.Template.Child()
    smaa_max_search_steps_diagonal = Gtk.Template.Child()
    smaa_corner_rounding = Gtk.Template.Child()
    clut = Gtk.Template.Child()
    lut_file_path = Gtk.Template.Child()
    btn_save = Gtk.Template.Child()
    btn_lut_reset = Gtk.Template.Child()

    # endregion
    __default_lut_msg = _("Choose a file.")

    def __init__(self, parent_window, config, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(parent_window)

        # common variables and references
        self.window = parent_window
        self.manager = parent_window.manager
        self.config = config
        conf = os.path.join(ManagerUtils.get_bottle_path(self.config), "vkBasalt.conf")

        # connect signals
        self.expander_cas.connect("notify::enable-expansion", self.__check_state)
        self.dls.connect("notify::enable-expansion", self.__check_state)
        self.fxaa.connect("notify::enable-expansion", self.__check_state)
        self.smaa.connect("notify::enable-expansion", self.__check_state)
        self.btn_save.connect("clicked", self.__save)
        self.switch_default.connect("state-set", self.__default)
        self.luma.connect("toggled", self.__change_edge_detection_type, "luma")
        self.color.connect("toggled", self.__change_edge_detection_type, "color")
        self.lut_file_path.connect("clicked", self.__import_clut)
        self.btn_lut_reset.connect("clicked", self.__reset_clut)

        if os.path.isfile(conf):
            vkbasalt_settings = ParseConfig(conf)

            # Check if effects are used.
            if "cas" not in vkbasalt_settings.effects:
                self.expander_cas.set_enable_expansion(False)
            if "dls" not in vkbasalt_settings.effects:
                self.dls.set_enable_expansion(False)
            if "fxaa" not in vkbasalt_settings.effects:
                self.fxaa.set_enable_expansion(False)
            if "smaa" not in vkbasalt_settings.effects:
                self.smaa.set_enable_expansion(False)
            # Check if clut is used.
            if vkbasalt_settings.lut_file_path is None:
                self.lut_file_path = False
            else:
                self.clut.set_subtitle(vkbasalt_settings.lut_file_path)
                self.lut_file_path = vkbasalt_settings.lut_file_path
                self.btn_lut_reset.show()

            if vkbasalt_settings.cas_sharpness != None:
                self.spin_cas_sharpness.set_value(float(vkbasalt_settings.cas_sharpness))
            if vkbasalt_settings.dls_sharpness != None:
                self.dls_sharpness.set_value(float(vkbasalt_settings.dls_sharpness))
            if vkbasalt_settings.dls_denoise != None:
                self.dls_denoise.set_value(float(vkbasalt_settings.dls_denoise))
            if vkbasalt_settings.fxaa_subpixel_quality != None:
                self.fxaa_subpixel_quality.set_value(float(vkbasalt_settings.fxaa_subpixel_quality))
            if vkbasalt_settings.fxaa_quality_edge_threshold != None:
                self.fxaa_quality_edge_threshold.set_value(float(vkbasalt_settings.fxaa_quality_edge_threshold))
            if vkbasalt_settings.fxaa_quality_edge_threshold_min != None:
                self.fxaa_quality_edge_threshold_min.set_value(float(vkbasalt_settings.fxaa_quality_edge_threshold_min))
            if vkbasalt_settings.smaa_threshold != None:
                self.smaa_threshold.set_value(float(vkbasalt_settings.smaa_threshold))
            if vkbasalt_settings.smaa_max_search_steps != None:
                self.smaa_max_search_steps.set_value(float(vkbasalt_settings.smaa_max_search_steps))
            if vkbasalt_settings.smaa_max_search_steps_diagonal != None:
                self.smaa_max_search_steps_diagonal.set_value(float(vkbasalt_settings.smaa_max_search_steps_diagonal))
            if vkbasalt_settings.smaa_corner_rounding != None:
                self.smaa_corner_rounding.set_value(float(vkbasalt_settings.smaa_corner_rounding))
            if vkbasalt_settings.smaa_edge_detection != None:
                if vkbasalt_settings.smaa_edge_detection == "color":
                    self.color.set_active(True)
                    self.smaa_edge_detection = "color"
                else:
                    self.smaa_edge_detection = "luma"
            else:
                self.smaa_edge_detection = "luma"
        else:
            self.switch_default.set_state(True)
            self.smaa_edge_detection = "luma"
            self.expander_cas.set_enable_expansion(False)
            self.dls.set_enable_expansion(False)
            self.fxaa.set_enable_expansion(False)
            self.smaa.set_enable_expansion(False)
            # self.clut.set_enable_expansion(False)
            self.lut_file_path = False

    def __idle_save(self, *args):

        conf = ManagerUtils.get_bottle_path(self.config)

        # Applies default settings and closes dialog.
        if self.switch_default.get_state() is True:
            vkbasalt_settings.default = True
            vkbasalt_settings.output = False
            conf = os.path.join(conf, "vkBasalt.conf")
            if os.path.isfile(conf):
                logging.info(f"Removing file: {conf}")
                os.remove(conf)
            parse(vkbasalt_settings)
            self.close()
            return GLib.SOURCE_REMOVE

        # Checks filter settings.
        if True in [
            self.expander_cas.get_enable_expansion(),
            self.dls.get_enable_expansion(),
            self.fxaa.get_enable_expansion(),
            self.smaa.get_enable_expansion(),
        ]:
            vkbasalt_settings.default = False
            effects = []
            if self.expander_cas.get_enable_expansion() is True:
                effects.append("cas")
                vkbasalt_settings.cas_sharpness = Gtk.Adjustment.get_value(self.spin_cas_sharpness)
            if self.dls.get_enable_expansion() is True:
                effects.append("dls")
                vkbasalt_settings.dls_sharpness = Gtk.Adjustment.get_value(self.dls_sharpness)
                vkbasalt_settings.dls_denoise = Gtk.Adjustment.get_value(self.dls_denoise)
            if self.fxaa.get_enable_expansion() is True:
                effects.append("fxaa")
                vkbasalt_settings.fxaa_subpixel_quality = Gtk.Adjustment.get_value(self.fxaa_subpixel_quality)
                vkbasalt_settings.fxaa_quality_edge_threshold = Gtk.Adjustment.get_value(self.fxaa_quality_edge_threshold)
                vkbasalt_settings.fxaa_quality_edge_threshold_min = Gtk.Adjustment.get_value(self.fxaa_quality_edge_threshold_min)
            if self.smaa.get_enable_expansion() is True:
                effects.append("smaa")
                vkbasalt_settings.smaa_threshold = Gtk.Adjustment.get_value(self.smaa_threshold)
                vkbasalt_settings.smaa_edge_detection = self.smaa_edge_detection
                vkbasalt_settings.smaa_corner_rounding = Gtk.Adjustment.get_value(self.smaa_corner_rounding)
                vkbasalt_settings.smaa_max_search_steps = Gtk.Adjustment.get_value(self.smaa_max_search_steps)
                vkbasalt_settings.smaa_max_search_steps_diagonal = Gtk.Adjustment.get_value(self.smaa_max_search_steps_diagonal)
            if self.lut_file_path:
                vkbasalt_settings.lut_file_path = self.lut_file_path

        vkbasalt_settings.effects = tuple(effects)

        vkbasalt_settings.output = conf

        parse(vkbasalt_settings)
        self.close()
        return GLib.SOURCE_REMOVE

    def __save(self, *args):
        GLib.idle_add(self.__idle_save)

    def __check_state(self, widget, state):
        if True in [
            self.expander_cas.get_enable_expansion(),
            self.dls.get_enable_expansion(),
            self.fxaa.get_enable_expansion(),
            self.smaa.get_enable_expansion(),
        ] or self.lut_file_path is not False:
            self.btn_save.set_sensitive(True)
        else:
            self.btn_save.set_sensitive(False)

    def __default(self, widget, state):
        self.expander_cas.set_sensitive(not state)
        self.dls.set_sensitive(not state)
        self.fxaa.set_sensitive(not state)
        self.smaa.set_sensitive(not state)
        self.clut.set_sensitive(not state)
        if state is False:
            if self.expander_cas.get_enable_expansion() is False and self.dls.get_enable_expansion() is False and self.fxaa.get_enable_expansion() is False and self.smaa.get_enable_expansion() is False and self.lut_file_path is False:
                self.btn_save.set_sensitive(False)
        else:
            self.btn_save.set_sensitive(True)

    def __change_edge_detection_type(self, widget, edge_detection_type):
        self.smaa_edge_detection = edge_detection_type
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
                self.lut_file_path = _file_dialog.get_file().get_path()

                if self.lut_file_path.split(".")[-1] == "png":

                    def error_dialog(title, message):
                        dialog = Adw.MessageDialog.new(self.window, title, message)
                        dialog.add_response("cancel", "Close")
                        dialog.present()

                    try:
                        texture = Gdk.Texture.new_from_filename(self.lut_file_path)

                        width = texture.get_width()
                        height = texture.get_height()

                        def set_lut_file_path():
                            if self.clut.get_subtitle():
                                self.lut_file_path = self.clut.get_subtitle()
                            else:
                                self.lut_file_path = False

                        if " " in self.lut_file_path:
                            error_dialog(_("Spaces in File Name"), _("Color Lookup Table path must not contain any spaces. Please rename the file to remove all spaces."))
                            set_lut_file_path()
                        elif width != height:
                            error_dialog(_("Invalid Image Dimension"), _("The height and width of the image must be equal."))
                            set_lut_file_path()
                        else:
                            self.clut.set_subtitle(self.lut_file_path)
                            self.btn_lut_reset.show()

                    except GLib.Error:
                        error_dialog(_("File not Found"), _("The given file does not exist. Please choose an appropriate file."))

        FileChooser(
            parent=self.window,
            title=_("Choose a configuration file"),
            action=Gtk.FileChooserAction.OPEN,
            buttons=(_("Cancel"), _("Import")),
            filters=["png", "CUBE"],
            callback=set_path
        )

    def __reset_clut(self, *args):
        self.lut_file_path = False
        vkbasalt_settings.lut_file_path = False
        self.btn_lut_reset.hide()
        self.clut.set_subtitle(self.__default_lut_msg)
        # TODO: execute __check_state
