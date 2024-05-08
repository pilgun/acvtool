from .axml_manifest import AxmlBinManifest
from .android_manifest import XMLManifest

def instrument_manifest(manifest_path):
    manifest = None
    if is_xml(manifest_path):
        manifest = XMLManifest(manifest_path)
    else:
        manifest =  AxmlBinManifest(manifest_path)
    manifest.add_instrumentation_tag()
    manifest.add_broadcast_receiver()
    manifest.add_write_permission()
    manifest.save_xml()

def is_xml(file_path):
    with open(file_path, 'rb') as file:
        first_byte = file.read(1)
        return first_byte == b'<'

if __name__ == "__main__":
    # $ acvtool/ python3 -m smiler.instrumenting.manifest_instrumenter path_to/AndroidManifest.xml
    import sys
    manifest_path = sys.argv[1]
    instrument_manifest(manifest_path)