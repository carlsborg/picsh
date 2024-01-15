# Copyright (c) Ran Dugal 2023
#
# This file is part of picsh
#
# Licensed under the GNU Affero General Public License v3, which is available at
# http://www.gnu.org/licenses/agpl-3.0.html
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero GPL for more details.
#

""" utility functions """

import logging
import colorama


def setup_logger(sname):
    logger = logging.getLogger(sname)

    console = logging.FileHandler("picsh.log")

    formatter = logging.Formatter("\rpicsh:%(asctime)s | %(message)s", "%H:%M:%S")
    console.setFormatter(formatter)

    logger.addHandler(console)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger


def get_logo():
    s_logo = """
                            ┌─┐@s╦╔═╗@e┌─┐┬ ┬
                            ├─┘@s║║  @e└─┐├─┤
                            ┴  @s╩╚═╝@e└─┘┴ ┴
    """
    s_logo = s_logo.replace("@s", colorama.Fore.CYAN)
    s_logo = s_logo.replace("@e", colorama.Fore.RESET)
    return s_logo


def get_tagline():
    s_github = """
                [.. Parallel Interactive Cluster Shell ..]
                    https://github.com/carlsborg/picsh 
    """
    return s_github
