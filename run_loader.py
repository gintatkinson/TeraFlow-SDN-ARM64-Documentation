import logging
from common.tools.descriptor.Loader import DescriptorLoader

logging.basicConfig(level=logging.INFO)

def load():
    print("Starting Descriptor Loader...")
    try:
        loader = DescriptorLoader(descriptors_file='/tmp/descriptors.json')
        results = loader.process()
        print("Results:", results)
    except Exception as e:
        print("Error during loading:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    load()
