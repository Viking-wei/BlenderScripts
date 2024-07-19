bl_info = {
    "name" : "Useful Utilites",
    "author" : "VikingWei",
    "description" : "",
    "blender" : (4, 1, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "3D View"
}

if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "ui"
        ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

from . import (ui)

def register():
    ui.register()

def unregister():
    ui.unregister()

if __name__ == "__main__":
    register()