
class JsonSerialiser:
    def __init__(self, package, granularity):
        self.package = package
        self.granularity = granularity

    def get_json_data(self, all_class_methods_data):
        import json
        # Convert the smalitree to a JSON-serializable format
        data = dict({})
        all_class_methods_data.update(data)
        return json.dumps(all_class_methods_data)

    def get_executed_methods_by_class(self, smalitree):
        classes = dict()
        for cl in smalitree.classes:
            if cl.is_coverable():
                methods = [m.descriptor for m in cl.methods if m.called]
                if methods:
                    classes[cl.name] = methods
        return classes
