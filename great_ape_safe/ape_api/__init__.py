import glob
import os


files = glob.glob("great_ape_safe/ape_api/[!_]*.py")
ape_apis = {}
for file in files:
    module_path = os.path.splitext(file)[0].replace("/", ".")
    module = __import__(module_path, fromlist=[module_path.capitalize()])
    class_name = module_path.split(".")[-1].title().replace("_", "")
    ape_apis[module_path.split(".")[-1]] = getattr(module, class_name)
