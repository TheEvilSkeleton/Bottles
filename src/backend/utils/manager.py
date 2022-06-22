# manager.py
#
# Copyright 2020 brombinmirko <send@mirko.pm>
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
import shlex
import shutil
import gi
import os
import subprocess
from glob import glob
from typing import NewType, Union
from datetime import datetime
from gi.repository import GLib

from bottles.backend.logger import Logger  # pyright: reportMissingImports=false
from bottles.backend.globals import Paths, user_apps_dir
from bottles.backend.utils.imagemagick import ImageMagickUtils
from bottles.backend.utils.generic import get_mime

logging = Logger()


class ManagerUtils:
    """
    This class contains methods (tools, utilities) that are not
    directly related to the Manager.
    """

    @staticmethod
    def open_filemanager(
            config: dict = dict,
            path_type: str = "bottle",
            component: str = "",
            custom_path: str = ""
    ):
        logging.info("Opening the file manager in the path …")
        path = ""

        if path_type == "bottle":
            bottle_path = ManagerUtils.get_bottle_path(config)
            if config.get("Environment") == "Steam":
                bottle_path = config.get("Path")
            path = f"{bottle_path}/drive_c"
        elif component != "":
            if path_type in ["runner", "runner:proton"]:
                path = ManagerUtils.get_runner_path(component)
            elif path_type == "dxvk":
                path = ManagerUtils.get_dxvk_path(component)
            elif path_type == "vkd3d":
                path = ManagerUtils.get_vkd3d_path(component)
            elif path_type == "nvapi":
                path = ManagerUtils.get_nvapi_path(component)
            elif path_type == "latencyflex":
                path = ManagerUtils.get_latencyflex_path(component)
            elif path_type == "runtime":
                path = Paths.runtimes
            elif path_type == "winebridge":
                path = Paths.winebridge

        if path_type == "custom" and custom_path != "":
            path = custom_path

        command = f"xdg-open '{path}'"
        subprocess.Popen(command, shell=True).communicate()

    @staticmethod
    def get_layer_path(layer: str) -> str:
        return f"{Paths.layers}/{layer}"

    @staticmethod
    def get_bottle_path(config: dict) -> str:
        if config.get("IsLayer"):
            return ManagerUtils.get_layer_path(config["Path"])
        if config.get("Environment") == "Steam":
            return os.path.join(Paths.steam, config.get("CompatData"))
        return os.path.join(Paths.bottles, config.get("Path"))

    @staticmethod
    def get_runner_path(runner: str) -> str:
        if runner.startswith("sys-"):
            return runner
        return f"{Paths.runners}/{runner}"

    @staticmethod
    def get_dxvk_path(dxvk: str) -> str:
        return f"{Paths.dxvk}/{dxvk}"

    @staticmethod
    def get_vkd3d_path(vkd3d: str) -> str:
        return f"{Paths.vkd3d}/{vkd3d}"

    @staticmethod
    def get_nvapi_path(nvapi: str) -> str:
        return f"{Paths.nvapi}/{nvapi}"

    @staticmethod
    def get_latencyflex_path(latencyflex: str) -> str:
        return f"{Paths.latencyflex}/{latencyflex}"

    @staticmethod
    def get_temp_path(dest: str) -> str:
        return f"{Paths.temp}/{dest}"

    @staticmethod
    def get_template_path(template: str) -> str:
        return f"{Paths.templates}/{template}"

    @staticmethod
    def move_file_to_bottle(
            file_path: str,
            config: dict,
            fn_update: callable = None
    ) -> Union[str, bool]:
        logging.info(f"Adding file {file_path} to the bottle …")
        bottle_path = ManagerUtils.get_bottle_path(config)

        if not os.path.exists(f"{bottle_path}/storage"):
            '''
            If the storage folder does not exist for the bottle,
            create it before moving the file.
            '''
            os.makedirs(f"{bottle_path}/storage")

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_new_path = f"{bottle_path}/storage/{file_name}"

        logging.info(f"Copying file {file_path} to the bottle …")
        try:
            with open(file_path, "rb") as f_in:
                with open(file_new_path, "wb") as f_out:
                    for i in range(file_size):
                        f_out.write(f_in.read(1))
                        _size = i / file_size

                        if fn_update:
                            if _size % 0.1 == 0:
                                GLib.idle_add(fn_update, _size)
                    GLib.idle_add(fn_update, 1)
            return file_new_path
        except (OSError, IOError):
            logging.error(f"Could not copy file {file_path} to the bottle.")
            return False

    @staticmethod
    def get_exe_parent_dir(config, executable_path):
        """Get parent directory of the executable."""
        if "\\" in executable_path:
            p = "\\".join(executable_path.split("\\")[:-1])
            p = p.replace("C:\\", "\\drive_c\\").replace("\\", "/")
            return ManagerUtils.get_bottle_path(config) + p

        p = "\\".join(executable_path.split("/")[:-1])
        p = f"/drive_c/{p}"
        return p.replace("\\", "/")

    @staticmethod
    def extract_icon(config: dict, program_name: str, program_path: str) -> str:
        from bottles.backend.wine.winepath import WinePath
        winepath = WinePath(config)
        icon = "com.usebottles.bottles-program"
        bottle_icons_path = os.path.join(ManagerUtils.get_bottle_path(config), "icons")

        try:
            import icoextract
            if winepath.is_windows(program_path):
                program_path = winepath.to_unix(program_path)

            ico_dest_temp = os.path.join(bottle_icons_path, f"_{program_name}.png")
            ico_dest = os.path.join(bottle_icons_path, f"{program_name}.png")
            ico = icoextract.IconExtractor(program_path)
            os.makedirs(bottle_icons_path, exist_ok=True)

            if os.path.exists(ico_dest_temp):
                os.remove(ico_dest_temp)

            if os.path.exists(ico_dest):
                os.remove(ico_dest)

            ico.export_icon(ico_dest_temp)
            if get_mime(ico_dest_temp) == "image/vnd.microsoft.icon":
                if not ico_dest_temp.endswith(".ico"):
                    shutil.move(ico_dest_temp, f"{ico_dest_temp}.ico")
                    ico_dest_temp = f"{ico_dest_temp}.ico"
                im = ImageMagickUtils(ico_dest_temp)
                im.convert(ico_dest)
                icon = ico_dest
            else:
                shutil.move(ico_dest_temp, ico_dest)
                icon = ico_dest
        except:
            pass

        return icon

    @staticmethod
    def create_desktop_entry(config, program: dict, skip_icon: bool = False, custom_icon: str = "",
                             use_xdp: bool = False) -> bool:
        if not user_apps_dir and not use_xdp:
            return False

        cmd_legacy = "bottles"
        cmd_cli = "bottles-cli"
        icon = "com.usebottles.bottles-program"

        if "FLATPAK_ID" in os.environ:
            cmd_legacy = "flatpak run com.usebottles.bottles"
            cmd_cli = "flatpak run --command=bottles-cli com.usebottles.bottles"

        if not skip_icon and not custom_icon:
            icon = ManagerUtils.extract_icon(config, program.get("name"), program.get("path"))
        elif custom_icon:
            icon = custom_icon

        if not use_xdp:
            file_name_template = "%s/%s--%s--%s.desktop"
            existing_files = glob(file_name_template % (
                Paths.applications,
                config.get('Name'),
                program.get("name"),
                "*"
            ))
            desktop_file = file_name_template % (
                Paths.applications,
                config.get('Name'),
                program.get("name"),
                datetime.now().timestamp()
            )

            if existing_files:
                for file in existing_files:
                    os.remove(file)

            with open(desktop_file, "w") as f:
                f.write(f"[Desktop Entry]\n")
                f.write(f"Name={program.get('name')}\n")
                f.write(f"Exec={cmd_cli} run -p {shlex.quote(program.get('name'))} -b '{config.get('Path')}'\n")
                f.write(f"Type=Application\n")
                f.write(f"Terminal=false\n")
                f.write(f"Categories=Application;\n")
                f.write(f"Icon={icon}\n")
                f.write(f"Comment=Launch {program.get('name')} using Bottles.\n")
                # Actions
                f.write("Actions=Configure;\n")
                f.write("[Desktop Action Configure]\n")
                f.write("Name=Configure in Bottles\n")
                f.write(f"Exec={cmd_legacy} -b '{config.get('Name')}'\n")

            return True

        '''
        WIP: the following code is not working yet, it raises an error:
             GDBus.Error:org.freedesktop.DBus.Error.UnknownMethod
        import uuid
        from gi.repository import Gio, Xdp

        portal = Xdp.Portal()
        if icon == "com.usebottles.bottles-program":
            _icon = Gio.BytesIcon.new(icon.encode("utf-8"))
        else:
            _icon = Gio.FileIcon.new(Gio.File.new_for_path(icon))
        icon_v = _icon.serialize()
        token = portal.dynamic_launcher_request_install_token(program.get("name"), icon_v)
        portal.dynamic_launcher_install(
            token,
            f"com.usebottles.bottles.{config.get('Name')}.{program.get('name')}.{str(uuid.uuid4())}.desktop",
            """
            [Desktop Entry]
            Exec={}
            Type=Application
            Terminal=false
            Categories=Application;
            Comment=Launch {} using Bottles.
            Actions=Configure;
            [Desktop Action Configure]
            Name=Configure in Bottles
            Exec={}
            """.format(
                f"{cmd_cli} run -p {shlex.quote(program.get('name'))} -b '{config.get('Path')}'",
                program.get("name"),
                f"{cmd_legacy} -b '{config.get('Name')}'"
            ).encode("utf-8")
        )
        '''

    @staticmethod
    def browse_wineprefix(wineprefix: dict):
        """Presents a dialog to browse the wineprefix."""
        ManagerUtils.open_filemanager(
            path_type="custom",
            custom_path=wineprefix.get("Path")
        )
