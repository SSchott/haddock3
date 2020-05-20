import os
from haddock.config import HaddockConfiguration


data_path = os.path.dirname(os.path.abspath(__file__))


class Topology:

    @staticmethod
    def get_supported():
        """Read the topology file and identify which data is supported"""
        supported = []
        haddock_conf = HaddockConfiguration()
        topology_file = os.path.join(data_path, haddock_conf.conf.topology.top_file)
        with open(topology_file) as input_handler:
            for line in input_handler:
                if 'resi' in line[:4].casefold():
                    res = line.split()[1]
                    supported.append(res)
        return supported
