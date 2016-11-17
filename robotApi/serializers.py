#import dill
import cloudpickle

#dill.settings['recurse'] = True

class Serializer:
    def dumps(self, data):
        return cloudpickle.dumps(data)
    def loads(self, data):
        return cloudpickle.loads(data)
