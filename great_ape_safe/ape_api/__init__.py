import glob
import os


files = glob.glob("great_ape_safe/ape_api/[!_]*.py")
module_names = [os.path.splitext(file)[0].replace("/", ".") for file in files]

ape_apis = {}
for module_path in module_names:
    module = __import__(module_path, fromlist=[module_path.capitalize()])
    class_name = module_path.split(".")[-1].capitalize()
    init_name = module_path.split(".")[-1]
    if "_" in class_name:
        # e.g: Uni_v3 should be UniV3
        i = class_name.index("_") + 1
        class_name = class_name[:i] + class_name[i:].capitalize()
        class_name = class_name.replace("_", "")
    ape_apis[init_name] = getattr(module, class_name)
