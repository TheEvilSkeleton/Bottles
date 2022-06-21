# vkbasalt.py: library supplying the logics and functions to generate configs
#
# Copyright 2022 Hari Rana
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import path, environ, system, remove
from sys import exit
from shutil import copyfile

def parse(args):
    # Apply default settings if possible
    if args.default:
        install_paths = [
            "/usr/lib/extensions/vulkan/vkBasalt/etc/vkBasalt",
            "/usr/local",
            "/usr/share/vkBasalt"
        ]
        for i in range(len(install_paths)):
            if path.exists(f"{install_paths[i]}/vkBasalt.conf"):
                if args.output:
                    copyfile(os.path.join(install_paths[i], "vkBasalt.conf"), os.path.join(args.output, "vkBasalt.conf"))
                if args.exec:
                    environ["ENABLE_VKBASALT"] = "1"
                    environ["VKBASALT_CONFIG_FILE"] = os.path.join(install_paths[i], "vkBasalt.conf")
                    system(f"{args.exec}")
                return
            else:
                exit(1)

    # Generate config and check for errors
    if args.effects:
        file = []

        # --disable-on-launch
        file.append("enableOnLaunch = ")
        if args.disable_on_launch:
            file.append("False\n")
        else:
            file.append("True\n")

        # --toggle-key
        file.append("toggleKey = ")
        if args.toggle_key:
            file.append(f"{args.toggle_key[0]}\n")
        else:
            file.append("Home\n")

        # --cas-sharpness
        if args.cas_sharpness:
            if -1 <= args.cas_sharpness <= 1:
                file.append(f"casSharpness = {args.cas_sharpness}\n")
            else:
                print("Error: CAS sharpness must be above -1 and below 1")
                exit(1)

        # --dls-sharpness
        if args.dls_sharpness:
            if 0 <= args.dls_sharpness <= 1:
                file.append(f"dlsSharpness = {args.dls_sharpness}\n")
            else:
                print("Error: DLS sharpness must be above 0 and below 1")
                exit(1)

        # --dls-denoise
        if args.dls_denoise:
            if 0 <= args.dls_denoise <= 1:
                file.append(f"dlsDenoise = {args.dls_denoise}\n")
            else:
                print("Error: DLS denoise must be above 0 and below 1")
                exit(1)

        # --fxaa-subpixel-quality
        if args.fxaa_subpixel_quality:
            if 0 <= args.fxaa_subpixel_quality <= 1:
                file.append(f"fxaaQualitySubpix = {args.fxaa_subpixel_quality}\n")
            else:
                print("Error: FXAA subpixel quality must be above 0 and below 1")
                exit(1)

        # --fxaa-edge-quality-threshold
        if args.fxaa_quality_edge_threshold:
            if 0 <= args.fxaa_quality_edge_threshold <= 1:
                file.append(f"fxaaQualityEdgeThreshold = {args.fxaa_quality_edge_threshold}\n")
            else:
                print("Error: FXAA edge quality threshold must be above 0 and below 1")
                exit(1)

        # --fxaa-quality-edge-threshold-min
        if args.fxaa_quality_edge_threshold_min:
            if 0 <= args.fxaa_quality_edge_threshold_min <= 0.1:
                file.append(f"fxaaQualityEdgeThresholdMin = {args.fxaa_quality_edge_threshold_min}\n")
            else:
                print("Error: FXAA edge quality threshold minimum must be above 0 and below 0.1")
                exit(1)

        # --smaa-edge-detection
        if args.smaa_edge_detection:
            file.append(f"smaaEdgeDetection = {args.smaa_edge_detection}\n")

        # --smaa-threshold
        if args.smaa_threshold:
            if 0 <= args.smaa_threshold <= 0.5:
                file.append(f"smaaThreshold = {args.smaa_threshold}\n")
            else:
                print("Error: SMAA threshold must be above 0 and below 0.5")
                exit(1)

        # --smaa-max-search-steps
        if args.smaa_max_search_steps:
            if 0 <= args.smaa_max_search_steps <= 112:
                file.append(f"smaaMaxSearchSteps = {args.smaa_max_search_steps}\n")
            else:
                print("Error: SMAA max search steps must be above 0 and below 112")
                exit(1)

        # --smaa-max-search-steps-diagonal
        if args.smaa_max_search_steps_diagonal:
            if 0 <= args.smaa_max_search_steps_diagonal <= 20:
                file.append(f"smaaMaxSearchStepsDiag = {args.smaa_max_search_steps_diagonal}\n")
            else:
                print("Error: SMAA max search steps diagonal must be above 0 and below 20")
                exit(1)

        # --smaa-corner-rounding
        if args.smaa_corner_rounding:
            if 0 <= args.smaa_corner_rounding <= 100:
                file.append(f"smaaCornerRounding = {args.smaa_corner_rounding}\n")
            else:
                print("Error: SMAA corner rounding must be above 0 and below 100")
                exit(1)

        # --lut-file-path
        if args.lut_file_path:
            file.append(f"lutFile = {args.lut_file_path}\n")

        # Output file
        if args.output:
            if path.isdir(args.output):
                f = open(f"{args.output}/vkBasalt.conf", "w")
            else:
                print("Error: No such directory")
                exit(1)
        else:
            tmp_dir = "/tmp/vkBasalt.conf"
            f = open(tmp_dir, "w")
        output = len(args.effects)
        if output > 0:
            file.append(f"effects = {':'.join(args.effects)}\n")

        # Write and close file
        f.write("".join(file))
        f.close()

        # --exec
        if args.exec:
            environ["ENABLE_VKBASALT"] = "1"
            if args.output:
                environ["VKBASALT_CONFIG_FILE"] = os.path.join(args.output, "vkBasalt.conf")
            else:
                environ["VKBASALT_CONFIG_FILE"] = tmp_dir
            system(f"{args.exec}")

            if environ["VKBASALT_CONFIG_FILE"] == tmp_dir:
                remove(tmp_dir)

    else:
        exit(1)

