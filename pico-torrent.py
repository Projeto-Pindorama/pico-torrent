#!/usr/bin/env python

'''
pico-torrent 1.0

A fast and small torrent client, initially made for Otto-PKG.
Developed by: Jazz_Man (alias).
Applied from the following example: https://www.libtorrent.org/python_binding.html

License:
Copyright © 2020 Projeto Pindorama.
pico-torrent is under the Caldera license.

Dependencies:
 > python 3.4=<
 > libtorrent-rasterbar

Syntax:
python3.? pico-torrent -f <file> -d <directory> (-s| )
or python3.? pico-torrent -L <file>


To-do list:
 > Manually set up the download bandwidth priority;
 > Create .torrent files;
 > Cryptography support (perhaps).
'''

import libtorrent as lt
import argparse
import os


argument = argparse.ArgumentParser()
exclusive = argument.add_mutually_exclusive_group(required=True)
exclusive.add_argument("--file", "-f",help="Torrent file or magnet link to download")
argument.add_argument("--seeding", "-S", action="store_true",help="Keep seeding after the download is complete")
argument.add_argument("--infos", "-i",help="Show torrent info")
argument.add_argument("--output", "-O", action="store_true",help="File output; filename")
# argument.add_argument("--download-priority", "-P", default=lt.pri,
#                       help="Set download priority")
exclusive.add_argument("--link", "-L",help="Create a magnet link through a file")
argument.add_argument("--dir", "-d",help="Specify the download save directory")
arguments = argument.parse_args()

session = lt.session({'listen_interfaces': '0.0.0.0:10881'})


def get_save_dir():
    if arguments.dir:
        if os.path.isdir(arguments.dir):
            return arguments.dir
        print(">>> Invalid Directory")
    else:
        return os.getcwd()


def show_status(local):
    torrent = local.status()
    print("\r{:.2f}% complete (down: {:.1f} kB/s up: {:.1f} kB/s peers: {:d}) {}".format(
        torrent.progress * 100, torrent.download_rate / 1000, torrent.upload_rate / 1000,
        torrent.num_peers, torrent.state), end=" ")


def start_download(filename):
    try:
        if os.path.isfile(filename):
            params = {'save_path': get_save_dir(
            ), 'ti': lt.torrent_info(filename)}
        else:
            params = lt.parse_magnet_uri(filename)
            params.save_path = get_save_dir()
        local = session.add_torrent(params)
        torrent = local.status()
        if arguments.file and arguments.seeding:
            while True:
                show_status(local)
            print("\n>>> Download complete.\n>>>Seeding")
        elif arguments.file:
            while not torrent.is_seeding:
                show_status(local)
        print("\n>>> Download complete!")
    except KeyboardInterrupt:
        print("\n>>> Exiting...\n")
    except Exception as error:
        print(">>> There was an error: {}".format(error))


def create_magnet(filename):
    return lt.make_magnet_uri(lt.torrent_info(filename))


if arguments.link:
    print(create_magnet(arguments.link))
elif arguments.file:
    start_download(arguments.file)
