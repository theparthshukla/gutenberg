#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from path import Path as path

from gutenbergtozim import logger
from gutenbergtozim.utils import exec_cmd, get_project_id
from gutenbergtozim.iso639 import ISO_MATRIX
from gutenbergtozim.export import export_skeleton


def build_zimfile(static_folder, zim_path=None,
                  languages=[], formats=[],
                  title=None, description=None,
                  only_books=[],
                  create_index=True, force=False):

    # revert HTML/JS/CSS to zim-compatible versions
    export_skeleton(static_folder=static_folder, dev_mode=False,
                    languages=languages, formats=formats,
                    only_books=only_books)

    if not languages:
        languages = ['mul']

    languages.sort()
    formats.sort()

    if title is None:
        if len(languages) > 5:
            title = ("Project Gutenberg Library with {formats}"
                     .format(formats=",".join(formats)))
        else:
            title = ("Project Gutenberg Library ({langs}) with {formats}"
                     .format(langs=",".join(languages),
                             formats=",".join(formats)))

    logger.info("\tWritting ZIM for {}".format(title))

    if description is None:
        description = "The first producer of free ebooks"

    project_id = get_project_id(languages, formats, only_books)

    if zim_path is None:
        zim_path = "{}.zim".format(project_id)

    if path(zim_path).exists() and not force:
        logger.info("ZIM file `{}` already exist.".format(zim_path))
        return

    languages = [ISO_MATRIX.get(lang, lang) for lang in languages]
    languages.sort()

    cmd = ['zimwriterfs',
           '--welcome', "Home.html",
           '--favicon', "favicon.png",
           '--language', ','.join(languages),
           '--name', project_id,
           '--title', title,
           '--description', description,
           '--creator', "gutenberg.org",
           '--publisher', "Kiwix",
           static_folder, zim_path]

    if create_index:
        cmd.insert(1, '--withFullTextIndex')
    if exec_cmd(cmd) == 0:
        logger.info("Successfuly created ZIM file at {}".format(zim_path))
    else:
        logger.error("Unable to create ZIM file :(")
