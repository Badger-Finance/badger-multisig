import glob
import os


def module_path_to_class_name(module_path):
    class_name = module_path.split(".")[-1].capitalize()
    if "_" in class_name:
        # e.g: Uni_v3 should be UniV3
        i = class_name.index("_") + 1
        class_name = class_name[:i] + class_name[i:].capitalize()
        class_name = class_name.replace("_", "")
    return class_name


files = glob.glob("great_ape_safe/ape_api/[!_]*.py")
ape_apis = {}
for file in files:
    module_path = os.path.splitext(file)[0].replace("/", ".")
    module = __import__(module_path, fromlist=[module_path.capitalize()])
    class_name = module_path_to_class_name(module_path)
    ape_apis[module_path.split(".")[-1]] = getattr(module, class_name)
