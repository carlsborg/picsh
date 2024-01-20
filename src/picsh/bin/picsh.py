#!/usr/bin/env python3
import logging
import warnings

warnings.filterwarnings("ignore", module="asyncssh\.crypto.*")
import sys
import os
import colorama
import argparse
from picsh.controllers.root_controller import RootController
from picsh.util import get_logo, get_tagline
import glob
import yaml
from picsh.app import App


if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
    print('Picsh only works with Python 3.6 and up. Your version is %s.x Exiting.' % sys.version_info.major)
    sys.exit(1)

if 'posix' not in os.name:
    print('Picsh has only been tested with on Linux/posix systems. Exiting')
    sys.exit(1)

def _get_picsh_dir():
    user_dir = os.path.expanduser("~")
    picsh_dir = os.path.join(user_dir, ".picsh")
    return picsh_dir

def _get_cluster_specs(picsh_dir):
    if not os.path.exists(picsh_dir):
        os.mkdir(picsh_dir)
    wildcardpath = os.path.join(picsh_dir, "*.yaml")
    cluster_specs = glob.glob(wildcardpath)
    ret = []
    for cluster_file in cluster_specs:
        if os.path.isfile(cluster_file):
            ret.append(cluster_file)
    return ret


def _no_clusters_usage(picsh_dir):
    print(
        "No cluster definitions found in [%s%s%s]"
        % (colorama.Fore.GREEN, picsh_dir, colorama.Style.RESET_ALL)
    )
    sample_defn = """
    cluster_name: kubedev
    login_user: root
    ssh_key_path: /home/devuser/keys/k8skey
    nodes:
    - ip: "10.0.0.1"
    - ip: "10.0.0.2"
    - ip: "10.0.0.3"
    """
    print(
        "%s%sSample cluster spec .yaml file:\n%s \nSee documentation for spec yaml.%s"
        % (
            colorama.Style.DIM,
            colorama.Fore.WHITE,
            sample_defn,
            colorama.Style.RESET_ALL,
        )
    )

def _build_cluster_spec_from_args(args):
    spec = {
        "cluster_name": "(from command line args)",
        "login_user": args.login_name or "",
        "ssh_key_path": args.identity_file or "",
        "nodes" : []
    }
    for host in args.hosts:
        spec["nodes"].append({"ip": host})
    logging.info(f"spec from args: {str(spec)}")
    return spec


def main():
    parser = argparse.ArgumentParser(description='Parallel Interactive Cluster Shell', add_help=False)
    parser.add_argument('-v', '--verbose', help='Log verbosely to ~/picsh.log', action='store_true', default=False)
    parser.add_argument('-i', '--identity_file', help='ssh private key file for login')
    parser.add_argument('-l', '--login_name', help='login user name')
    parser.add_argument('-h', '--hosts', help='space separated host ips', nargs='*')
    args = parser.parse_args()

    picsh_dir = _get_picsh_dir()

    if args.verbose:
        logging.basicConfig(
            filename=os.path.join(picsh_dir, "picsh.log"),
            #encoding="utf-8",
            level=logging.INFO,
            format='%(asctime)s | %(levelname)8s | %(module)s : %(message)s',
            filemode="w"
        )
        logging.info("\n==> picsh started")

    cluster_spec = {}
    cluster_spec_paths = []
    if args.hosts:
        cluster_spec = _build_cluster_spec_from_args(args)
    else:
        cluster_spec_paths = _get_cluster_specs(picsh_dir)
        if len(cluster_spec_paths) == 0:
            _no_clusters_usage(picsh_dir)
            sys.exit(0)

    App(cluster_spec_paths, cluster_spec).run()

    print(get_logo())
    print(colorama.Fore.CYAN)
    print(get_tagline())
    print(colorama.Fore.RESET)


if __name__ == "__main__":
    main()
