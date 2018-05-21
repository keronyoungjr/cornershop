from .algorithms import Ebay, Amazon


class Global:
    def __init__(self):
        self.algorithms = [Amazon(), Ebay()]

    def search(self, item):
        for algorithm in self.algorithms:
            try:
                pages, curr = algorithm.search(item)
                # min((item for item in algorithm.extract(curr))
                yield min((min((item for page in pages for item in algorithm.extract(algorithm.getDOM(page))),
                               key=lambda x: x[2]),
                           min((item for item in algorithm.extract(curr)), key=lambda x: x[2]))), \
                      algorithm.name
            except Exception:
                pass
