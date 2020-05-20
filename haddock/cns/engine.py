import subprocess
import os
from haddock.config import HaddockConfiguration, haddock_path
from haddock.error import CNSRunningError
from haddock.parallel import Captain


class CNSJob:
    def __init__(self, input_file, output_file, cns_folder='', cns_exec=''):
        self.input_file = input_file
        self.output_file = output_file
        self.cns_folder = cns_folder
        self.cns_exec = cns_exec

    def set_cns(self, cns_folder, cns_exec):
        self.cns_folder = cns_folder
        self.cns_exec = cns_exec

    def run(self):
        """Run this job"""
        with open(self.input_file) as inp:
            with open(self.output_file, 'w+') as outf:
                env = {'RUN':self.cns_folder}
                p = subprocess.Popen(self.cns_exec, stdin=inp, stdout=outf, close_fds=True, env=env)
                out, error = p.communicate()
                p.kill()
                if error:
                    raise CNSRunningError(error)
        return out


class CNSEngine:
    def __init__(self, cns_exec, jobs, cns_folder, num_cores):
        self.cns_exec = cns_exec
        self.jobs = jobs
        self.cns_folder = cns_folder
        self.num_cores = num_cores

    def run(self):
        raise NotImplentedError()
        

class ParallelCNSEngine(CNSEngine):
    """CNSEngine for parallel execution"""
    def run(self):
        captain = Captain(self.jobs, self.num_cores)
        captain.drink()


class SerialCNSEngine(ParallelCNSEngine):
    """CNSEngine for serial execution"""
    def run(self):
        captain = Captain(self.jobs, 1)
        captain.drink()


class CNSEngineFactory:
    """CNS wrapper"""
    __running_schemes = {'serial': SerialCNSEngine,
                         'parallel': ParallelCNSEngine}

    @staticmethod
    def get(jobs, cns_folder, scheme='serial', num_cores=1):
        haddock_conf = HaddockConfiguration()
        cns_exec = os.path.join(haddock_path, haddock_conf.conf.default.cns_exe)
        if scheme not in CNSEngineFactory.__running_schemes:
            raise CNSRunningError('Run scheme not recognized')
        # Add necessary information to jobs
        for job in jobs:
            job.set_cns(cns_folder, cns_exec)
        return CNSEngineFactory.__running_schemes[scheme](cns_exec, jobs, cns_folder, num_cores)
