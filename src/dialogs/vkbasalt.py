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
    expander_dls = Gtk.Template.Child()
    expander_fxaa = Gtk.Template.Child()
    expander_smaa = Gtk.Template.Child()
    spin_cas_sharpness = Gtk.Template.Child()
    spin_dls_sharpness = Gtk.Template.Child()
    spin_dls_denoise = Gtk.Template.Child()
    spin_fxaa_subpixel_quality = Gtk.Template.Child()
    spin_fxaa_quality_edge_threshold = Gtk.Template.Child()
    spin_fxaa_quality_edge_threshold_min = Gtk.Template.Child()
    toggle_luma = Gtk.Template.Child()
    toggle_color = Gtk.Template.Child()
    spin_smaa_threshold = Gtk.Template.Child()
    spin_smaa_max_search_steps = Gtk.Template.Child()
    spin_smaa_max_search_steps_diagonal = Gtk.Template.Child()
    spin_smaa_corner_rounding = Gtk.Template.Child()
    action_clut = Gtk.Template.Child()
    btn_lut_file_path = Gtk.Template.Child()
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
        self.expander_dls.connect("notify::enable-expansion", self.__check_state)
        self.expander_fxaa.connect("notify::enable-expansion", self.__check_state)
        self.expander_smaa.connect("notify::enable-expansion", self.__check_state)
        self.btn_save.connect("clicked", self.__save)
        self.switch_default.connect("state-set", self.__default)
        self.toggle_luma.connect("toggled", self.__change_edge_detection_type, "luma")
        self.toggle_color.connect("toggled", self.__change_edge_detection_type, "color")
        self.btn_lut_file_path.connect("clicked", self.__import_clut)
        self.btn_lut_reset.connect("clicked", self.__reset_clut)

        if os.path.isfile(conf):
            vkbasalt_settings = ParseConfig(conf)

            # Check if effects are used.
            if vkbasalt_settings.effects:
                if "cas" not in vkbasalt_settings.effects:
                    self.expander_cas.set_enable_expansion(False)
                if "dls" not in vkbasalt_settings.effects:
                    self.expander_dls.set_enable_expansion(False)
                if "fxaa" not in vkbasalt_settings.effects:
                    self.expander_fxaa.set_enable_expansion(False)
                if "smaa" not in vkbasalt_settings.effects:
                    self.expander_smaa.set_enable_expansion(False)
            else:
                vkbasalt_settings.effects = False
                self.expander_cas.set_enable_expansion(False)
                self.expander_dls.set_enable_expansion(False)
                self.expander_fxaa.set_enable_expansion(False)
                self.expander_smaa.set_enable_expansion(False)

            # Check if clut is used.
            if vkbasalt_settings.lut_file_path is None:
                self.btn_lut_file_path = False
            else:
                self.action_clut.set_subtitle(vkbasalt_settings.lut_file_path)
                self.btn_lut_file_path = vkbasalt_settings.lut_file_path
                self.btn_lut_reset.show()

            if vkbasalt_settings.cas_sharpness != None:
                self.spin_cas_sharpness.set_value(float(vkbasalt_settings.cas_sharpness))
            if vkbasalt_settings.dls_sharpness != None:
                self.spin_dls_sharpness.set_value(float(vkbasalt_settings.dls_sharpness))
            if vkbasalt_settings.dls_denoise != None:
                self.spin_dls_denoise.set_value(float(vkbasalt_settings.dls_denoise))
            if vkbasalt_settings.fxaa_subpixel_quality != None:
                self.spin_fxaa_subpixel_quality.set_value(float(vkbasalt_settings.fxaa_subpixel_quality))
            if vkbasalt_settings.fxaa_quality_edge_threshold != None:
                self.spin_fxaa_quality_edge_threshold.set_value(float(vkbasalt_settings.fxaa_quality_edge_threshold))
            if vkbasalt_settings.fxaa_quality_edge_threshold_min != None:
                self.spin_fxaa_quality_edge_threshold_min.set_value(float(vkbasalt_settings.fxaa_quality_edge_threshold_min))
            if vkbasalt_settings.smaa_threshold != None:
                self.spin_smaa_threshold.set_value(float(vkbasalt_settings.smaa_threshold))
            if vkbasalt_settings.smaa_max_search_steps != None:
                self.spin_smaa_max_search_steps.set_value(float(vkbasalt_settings.smaa_max_search_steps))
            if vkbasalt_settings.smaa_max_search_steps_diagonal != None:
                self.spin_smaa_max_search_steps_diagonal.set_value(float(vkbasalt_settings.smaa_max_search_steps_diagonal))
            if vkbasalt_settings.smaa_corner_rounding != None:
                self.spin_smaa_corner_rounding.set_value(float(vkbasalt_settings.smaa_corner_rounding))
            if vkbasalt_settings.smaa_edge_detection != None:
                if vkbasalt_settings.smaa_edge_detection == "color":
                    self.toggle_color.set_active(True)
                    self.smaa_edge_detection = "color"
                else:
                    self.smaa_edge_detection = "luma"
            else:
                self.smaa_edge_detection = "luma"
        else:
            self.switch_default.set_state(True)
            self.smaa_edge_detection = "luma"
            self.expander_cas.set_enable_expansion(False)
            self.expander_dls.set_enable_expansion(False)
            self.expander_fxaa.set_enable_expansion(False)
            self.expander_smaa.set_enable_expansion(False)
            # self.action_clut.set_enable_expansion(False)
            self.btn_lut_file_path = False

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
        else:
            vkbasalt_settings.default = False

        # Checks filter settings.
        if True in [
            self.expander_cas.get_enable_expansion(),
            self.expander_dls.get_enable_expansion(),
            self.expander_fxaa.get_enable_expansion(),
            self.expander_smaa.get_enable_expansion(),
        ]:
            effects = []
            if self.expander_cas.get_enable_expansion() is True:
                effects.append("cas")
                vkbasalt_settings.cas_sharpness = Gtk.Adjustment.get_value(self.spin_cas_sharpness)
            if self.expander_dls.get_enable_expansion() is True:
                effects.append("dls")
                vkbasalt_settings.dls_sharpness = Gtk.Adjustment.get_value(self.spin_dls_sharpness)
                vkbasalt_settings.dls_denoise = Gtk.Adjustment.get_value(self.spin_dls_denoise)
            if self.expander_fxaa.get_enable_expansion() is True:
                effects.append("fxaa")
                vkbasalt_settings.fxaa_subpixel_quality = Gtk.Adjustment.get_value(self.spin_fxaa_subpixel_quality)
                vkbasalt_settings.fxaa_quality_edge_threshold = Gtk.Adjustment.get_value(self.spin_fxaa_quality_edge_threshold)
                vkbasalt_settings.fxaa_quality_edge_threshold_min = Gtk.Adjustment.get_value(self.spin_fxaa_quality_edge_threshold_min)
            if self.expander_smaa.get_enable_expansion() is True:
                effects.append("smaa")
                vkbasalt_settings.smaa_threshold = Gtk.Adjustment.get_value(self.spin_smaa_threshold)
                vkbasalt_settings.smaa_edge_detection = self.smaa_edge_detection
                vkbasalt_settings.smaa_corner_rounding = Gtk.Adjustment.get_value(self.spin_smaa_corner_rounding)
                vkbasalt_settings.smaa_max_search_steps = Gtk.Adjustment.get_value(self.spin_smaa_max_search_steps)
                vkbasalt_settings.smaa_max_search_steps_diagonal = Gtk.Adjustment.get_value(self.spin_smaa_max_search_steps_diagonal)

            vkbasalt_settings.effects = tuple(effects)

        else:
            vkbasalt_settings.effects = False

        if self.btn_lut_file_path:
            vkbasalt_settings.lut_file_path = self.btn_lut_file_path

        vkbasalt_settings.output = conf

        parse(vkbasalt_settings)
        self.close()
        return GLib.SOURCE_REMOVE

    def __save(self, *args):
        GLib.idle_add(self.__idle_save)

    def __check_state(self, *args):
        if True in [
            self.expander_cas.get_enable_expansion(),
            self.expander_dls.get_enable_expansion(),
            self.expander_fxaa.get_enable_expansion(),
            self.expander_smaa.get_enable_expansion(),
        ] or self.btn_lut_file_path is not False:
            self.btn_save.set_sensitive(True)
        else:
            self.btn_save.set_sensitive(False)

    def __default(self, widget, state):
        self.expander_cas.set_sensitive(not state)
        self.expander_dls.set_sensitive(not state)
        self.expander_fxaa.set_sensitive(not state)
        self.expander_smaa.set_sensitive(not state)
        self.action_clut.set_sensitive(not state)
        if state is False:
            if self.expander_cas.get_enable_expansion() is False \
                and self.expander_dls.get_enable_expansion() is False\
                and self.expander_fxaa.get_enable_expansion() is False\
                and self.expander_smaa.get_enable_expansion() is False\
                and self.btn_lut_file_path is False:

                self.btn_save.set_sensitive(False)
        else:
            self.btn_save.set_sensitive(True)

    def __change_edge_detection_type(self, widget, edge_detection_type):
        self.smaa_edge_detection = edge_detection_type
        self.toggle_luma.handler_block_by_func(self.__change_edge_detection_type)
        self.toggle_color.handler_block_by_func(self.__change_edge_detection_type)
        if edge_detection_type == "luma":
            self.toggle_color.set_active(False)
            self.toggle_luma.set_active(True)
        elif edge_detection_type == "color":
            self.toggle_color.set_active(True)
            self.toggle_luma.set_active(False)

        self.toggle_luma.handler_unblock_by_func(self.__change_edge_detection_type)
        self.toggle_color.handler_unblock_by_func(self.__change_edge_detection_type)

    def __import_clut(self, *args):
        def set_path(_dialog, response, _file_dialog):
            if response == -3:
                self.btn_lut_file_path = _file_dialog.get_file().get_path()

                if self.btn_lut_file_path.split(".")[-1] == "png":

                    def error_dialog(title, message):
                        dialog = Adw.MessageDialog.new(self.window, title, message)
                        dialog.add_response("cancel", "Close")
                        dialog.present()

                    try:
                        texture = Gdk.Texture.new_from_filename(self.btn_lut_file_path)

                        width = texture.get_width()
                        height = texture.get_height()

                        def set_lut_file_path():
                            if self.action_clut.get_subtitle():
                                self.btn_lut_file_path = self.action_clut.get_subtitle()
                            else:
                                self.btn_lut_file_path = False

                        if " " in self.btn_lut_file_path:
                            error_dialog(
                                _("Spaces in File Name"),
                                _("Color Lookup Table path must not contain any spaces. Please rename the file to remove all spaces.")
                                )
                            set_lut_file_path()
                        elif width != height:
                            error_dialog(
                                _("Invalid Image Dimension"),
                                _("The height and width of the image must be equal.")
                                )
                            set_lut_file_path()
                        else:
                            self.action_clut.set_subtitle(self.btn_lut_file_path)
                            self.btn_lut_reset.show()

                        self.__check_state()

                    except GLib.Error:
                        error_dialog(
                            _("File not Found"),
                            _("The given file does not exist. Please choose an appropriate file.")
                            )

        FileChooser(
            parent=self.window,
            title=_("Choose a configuration file"),
            action=Gtk.FileChooserAction.OPEN,
            buttons=(_("Cancel"), _("Import")),
            filters=["png", "CUBE"],
            callback=set_path
        )

    def __reset_clut(self, *args):
        self.btn_lut_file_path = False
        vkbasalt_settings.lut_file_path = False
        self.btn_lut_reset.hide()
        self.action_clut.set_subtitle(self.__default_lut_msg)
        self.__check_state()
