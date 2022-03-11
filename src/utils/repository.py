import os
from src.utils.file_control import FileControl
from src.utils.resolver import resolve_once
from src.models.route import Route
from src.models.route_collection import RouteCollection


class Repository:

    def __init__(self, file_path, file_control=FileControl()):
        self.file_control = file_control
        self.routes = self.generate(file_path)

    def _set_from_file(self, collection, file):
        content = self.file_control.load_dict_from_file(file)
        if 'paths' not in content or len(content['paths']) == 0:
            return
        if len([val for key, val in content['paths'].items() if '$' in key]) > 0:
            for value in content['paths']:
                if '$' in value and 'group' in value:
                    absolute_path = os.path.join(
                        os.path.dirname(file), content['paths'][value]['$ref'])
                    ref_content = self.file_control.load_dict_from_file(
                        absolute_path)
                    spec = resolve_once(
                        absolute_path, ref_content, self.file_control)
                    for path in spec:
                        method = list(spec[path].keys())
                        collection.add(
                            Route(
                                method[0].upper(),
                                path,
                                absolute_path,
                                spec[path][method[0]]
                            ))
                else:
                    spec = resolve_once(
                        file, content['paths'][value], self.file_control)
                    for method in spec:
                        collection.add(
                            Route(
                                method.upper(),
                                value,
                                file,
                                spec[method]
                            ))
        else:
            for path, spec in content['paths'].items():
                spec = resolve_once(file, spec, self.file_control)
                for method in spec:
                    collection.add(
                        Route(
                            method.upper(),
                            path,
                            file,
                            spec[method]
                        ))

    def generate(self, file_path):
        collection = RouteCollection()
        files = [p for p in file_path if os.path.isfile(p)]
        for file in files:
            try:
                self._set_from_file(collection, file)
            except Exception as e:
                raise Exception(e)
        collection.sort()
        return collection
