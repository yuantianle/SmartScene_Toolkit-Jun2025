# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Tianle Yuan

# ***** BEGIN GPL LICENSE BLOCK ****
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK ****

bl_info = {
    "name": "🧩 SmartScene Toolkit",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "3D View > Object Context Menu / Edit Mode Menu",
    "description": "Scene structure utilities: parenting, duplication, mirroring, collection management",
    "category": "Object",
}

import importlib

# Import all modules
from . import (
    parent_to_cursor,
    move_hierarchy_to_new_collection,
    hierarchy_duplicate,
    mirror_to_cursor,
    mirror_to_cursor_edit,
)

modules = [
    parent_to_cursor,
    move_hierarchy_to_new_collection,
    hierarchy_duplicate,
    mirror_to_cursor,
    mirror_to_cursor_edit,
]

def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()

def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
