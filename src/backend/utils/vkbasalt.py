# vkbasalt.py: library supplying the logics and functions to generate configs
#
# Copyright 2022 vkbasalt-cli Contributors
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
import configparser
import logging


def parse(args):
    # Apply default settings if possible
    if args.default:
        install_paths = [
            "/usr/lib/extensions/vulkan/vkBasalt/etc/vkBasalt",
            "/usr/local",
            "/usr/share/vkBasalt",
        ]
        for i in range(len(install_paths)):
            if path.isfile(path.join(install_paths[i], "vkBasalt.conf")):
                if args.output:
                    copyfile(path.join(install_paths[i], "vkBasalt.conf"), path.join(args.output, "vkBasalt.conf"))
                if args.exec:
                    environ["ENABLE_VKBASALT"] = "1"
                    environ["VKBASALT_CONFIG_FILE"] = path.join(install_paths[i], "vkBasalt.conf")
                    system(f"{args.exec}")
                return
        logging.error(f"No such path for vkBasalt exists")
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
                file.append(f"casSharpness = {round(args.cas_sharpness, 2)}\n")
            else:
                logging.error(f"Error: CAS sharpness must be above -1 and below 1")
                exit(1)

        # --dls-sharpness
        if args.dls_sharpness:
            if 0 <= args.dls_sharpness <= 1:
                file.append(f"dlsSharpness = {round(args.dls_sharpness, 2)}\n")
            else:
                logging.error(f"Error: DLS sharpness must be above 0 and below 1")
                exit(1)

        # --dls-denoise
        if args.dls_denoise:
            if 0 <= args.dls_denoise <= 1:
                file.append(f"dlsDenoise = {round(args.dls_denoise, 2)}\n")
            else:
                logging.error(f"Error: DLS denoise must be above 0 and below 1")
                exit(1)

        # --fxaa-subpixel-quality
        if args.fxaa_subpixel_quality:
            if 0 <= args.fxaa_subpixel_quality <= 1:
                file.append(f"fxaaQualitySubpix = {round(args.fxaa_subpixel_quality, 2)}\n")
            else:
                logging.error(f"Error: FXAA subpixel quality must be above 0 and below 1")
                exit(1)

        # --fxaa-edge-quality-threshold
        if args.fxaa_quality_edge_threshold:
            if 0 <= args.fxaa_quality_edge_threshold <= 1:
                file.append(f"fxaaQualityEdgeThreshold = {round(args.fxaa_quality_edge_threshold, 2)}\n")
            else:
                logging.error(f"Error: FXAA edge quality threshold must be above 0 and below 1")
                exit(1)

        # --fxaa-quality-edge-threshold-min
        if args.fxaa_quality_edge_threshold_min:
            if 0 <= args.fxaa_quality_edge_threshold_min <= 0.1:
                file.append(f"fxaaQualityEdgeThresholdMin = {round(args.fxaa_quality_edge_threshold_min, 3)}\n")
            else:
                logging.error(f"Error: FXAA edge quality threshold minimum must be above 0 and below 0.1")
                exit(1)

        # --smaa-edge-detection
        if args.smaa_edge_detection:
            file.append(f"smaaEdgeDetection = {args.smaa_edge_detection}\n")

        # --smaa-threshold
        if args.smaa_threshold:
            if 0 <= args.smaa_threshold <= 0.5:
                file.append(f"smaaThreshold = {round(args.smaa_threshold, 3)}\n")
            else:
                logging.error(f"Error: SMAA threshold must be above 0 and below 0.5")
                exit(1)

        # --smaa-max-search-steps
        if args.smaa_max_search_steps:
            if 0 <= args.smaa_max_search_steps <= 112:
                file.append(f"smaaMaxSearchSteps = {round(args.smaa_max_search_steps)}\n")
            else:
                logging.error(f"Error: SMAA max search steps must be above 0 and below 112")
                exit(1)

        # --smaa-max-search-steps-diagonal
        if args.smaa_max_search_steps_diagonal:
            if 0 <= args.smaa_max_search_steps_diagonal <= 20:
                file.append(f"smaaMaxSearchStepsDiag = {round(args.smaa_max_search_steps_diagonal)}\n")
            else:
                logging.error(f"Error: SMAA max search steps diagonal must be above 0 and below 20")
                exit(1)

        # --smaa-corner-rounding
        if args.smaa_corner_rounding:
            if 0 <= args.smaa_corner_rounding <= 100:
                file.append(f"smaaCornerRounding = {round(args.smaa_corner_rounding)}\n")
            else:
                logging.error(f"Error: SMAA corner rounding must be above 0 and below 100")
                exit(1)

        # --lut-file-path
        if args.lut_file_path:
            file.append(f"lutFile = {args.lut_file_path}\n")

        # Output file
        if args.output:
            if path.isdir(args.output):
                vkbasalt_conf = path.join(args.output, "vkBasalt.conf")
            else:
                logging.error(f"Error: No such directory")
                exit(1)
        else:
            vkbasalt_conf = "/tmp/vkBasalt.conf"
            tmp = True

        # Write and close file
        with open(vkbasalt_conf, "w") as f:
            if args.effects:
                file.append(f"effects = {':'.join(args.effects)}\n")
            f.write("".join(file))

        # --exec
        if args.exec:
            environ["ENABLE_VKBASALT"] = "1"
            environ["VKBASALT_CONFIG_FILE"] = vkbasalt_conf
            system(f"{args.exec}")

            if tmp:
                remove(vkbasalt_conf)

    else:
        logging.error(f"Please specify one or more effects.")
        exit(1)

def getConfigValue(config, value):
    with open(config, "r") as f:
        file = "[config]\n"+f.read()
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(file)
        return config['config'].get(value)

def ParseConfig(config):
    class args:
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
    args.effects = getConfigValue(config, 'effects')
    args.toggle_key = getConfigValue(config, 'toggleKey')
    args.disable_on_launch = "True" if getConfigValue(config, 'enableOnLaunch') == "False" else "False"
    args.cas_sharpness = getConfigValue(config, 'casSharpness')
    args.dls_sharpness = getConfigValue(config, 'dlsSharpness')
    args.dls_denoise = getConfigValue(config, 'dlsDenoise')
    args.fxaa_subpixel_quality = getConfigValue(config, 'fxaaQualitySubpix')
    args.fxaa_quality_edge_threshold = getConfigValue(config, 'fxaaQualityEdgeThreshold')
    args.fxaa_quality_edge_threshold_min = getConfigValue(config, 'fxaaQualityEdgeThresholdMin')
    args.smaa_edge_detection = getConfigValue(config, 'smaaEdgeDetection')
    args.smaa_threshold = getConfigValue(config, 'smaaThreshold')
    args.smaa_max_search_steps = getConfigValue(config, 'smaaMaxSearchSteps')
    args.smaa_max_search_steps_diagonal = getConfigValue(config, 'smaaMaxSearchStepsDiag')
    args.smaa_corner_rounding = getConfigValue(config, 'smaaCornerRounding')
    args.lut_file_path = getConfigValue(config, 'lutFile')

    return(args)

