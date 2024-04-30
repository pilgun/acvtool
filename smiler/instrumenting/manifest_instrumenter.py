from .android_manifest import AndroidManifest


def instrument_manifest(manifest_path):
    manifest = AndroidManifest(manifest_path)
    manifest.add_instrumentation_tag()
    manifest.add_broadcast_receiver()
    manifest.add_write_permission()
    manifest.save_xml()
