import os
import glob
from haddock.config import HaddockConfiguration
from haddock.pdbutil import PDBFactory
from haddock.mathutil import RandomNumberGenerator


def generate_topology(input_pdb, course_path, recipe_str, defaults, protonation=None):
    """Generate a HADDOCK topology string"""
    haddock_conf = HaddockConfiguration()

    general_param = load_recipe_params(defaults)

    forcefield_parameters = haddock_conf.conf.parameters.param_file
    param = load_ff_parameters(forcefield_parameters)

    forcefield_topology = haddock_conf.conf.topology.top_file
    top = load_ff_topology(forcefield_topology)

    molecule_linkage = haddock_conf.conf.link.link
    link = load_link(molecule_linkage)

    topology_protonation = load_protonation_state(protonation)

    translation_vectors = dict([(i, getattr(haddock_conf.conf.translation_vectors, f'trans_vector_{i}')) for i in range(51)])
    trans_vec = load_trans_vectors(translation_vectors)

    tensor_options = ['tensor_psf', 'tensor_pdb', 'tensor_para_psf', 'tensor_para_pdb', 'tensor_dani_psf']
    tensor_params = dict([(e, getattr(haddock_conf.conf.tensor, e)) for e in tensor_options])
    tensor = load_tensor(tensor_params)

    scatter_lib = haddock_conf.conf.scatter.scatter_lib
    scatter = load_scatter(scatter_lib)

    axis_options = ['top_axis', 'par_axis', 'top_axis_dani']
    axis_params = dict([(e, getattr(haddock_conf.conf.axis, e)) for e in axis_options])
    axis = load_axis(axis_params)

    waterbox_param = haddock_conf.conf.water_box.boxtyp20
    water_box = load_waterbox(waterbox_param)

    basename = os.path.basename(input_pdb)
    filename, extension = os.path.splitext(basename)
    abs_path = os.path.dirname(os.path.abspath(input_pdb))
    output_pdb_filename = os.path.join('.', f'{filename}_haddock{extension}')
    output_psf_filename = os.path.join('.', f'{filename}_haddock.psf')
    output = prepare_output(output_psf_filename, output_pdb_filename)
    
    input_str = prepare_input(input_pdb, course_path)

    inp = general_param + param + top + input_str + output + link + topology_protonation \
          + trans_vec + tensor + scatter + axis + water_box + recipe_str

    return inp


def load_recipe_params(default_params):
    """Writes the values at the header section"""
    param_header = f'{os.linesep}! Parameters{os.linesep}'

    for param in default_params['params']:

        v = default_params['params'][param]

        if isinstance(v, bool):
            v = str(v).lower()
            param_header += f'eval (${param}={v}){os.linesep}'

        elif isinstance(v, str):
            param_header += f'eval (${param}="{v}"){os.linesep}'

        elif isinstance(v, int):
            param_header += f'eval (${param}={v}){os.linesep}'

        elif isinstance(v, float):
            param_header += f'eval (${param}={v}){os.linesep}'

        elif not v:
            # either 0 or empty string
            if isinstance(v, str):
                v = '\"\"'
                param_header += f'eval (${param}={v}){os.linesep}'
            if isinstance(v, int):
                v = 0.0
                param_header += f'eval (${param}={v}){os.linesep}'

    if 'chain' in default_params:
        # load molecule specific things
        for mol in default_params['chain']:
            for param in default_params['chain'][mol]:
                v = default_params['chain'][mol][param]
                # this are LOGICAL, which means no quotes
                param_header += f'eval (${param}_{mol}={v}){os.linesep}'

    return param_header


def prepare_input(pdb_input, course_path, psf_input=None):
    """Input of the CNS file.
    
    This section will be written for any recipe even if some CNS variables 
    are not used, it should not be an issue.
    """

    input_str = f'{os.linesep}! Input structure{os.linesep}'

    ncomp = None

    if psf_input:
        if type(psf_input) == str:
            input_str += f'structure{os.linesep}'
            input_str += f'  @@{psf_input}{os.linesep}'
            input_str += f'end{os.linesep}'
        if type(psf_input) == list:
            input_str += f'structure{os.linesep}'
            for psf in psf_input:
                input_str += f'  @@{psf}{os.linesep}'
            input_str += f'end{os.linesep}'

    if type(pdb_input) == str:
        ncomp = 1
        if psf_input:
            input_str += f'coor @@{pdb_input}{os.linesep}'

        # $file variable is still used by some CNS recipes, need refactoring!
        input_str += f'eval ($file=\"{pdb_input}\"){os.linesep}'

    if type(pdb_input) == list or type(pdb_input) == tuple:
        ncomp = len(pdb_input)
        for pdb in pdb_input:
            input_str += f'coor @@{pdb}{os.linesep}'

    chainsegs = PDBFactory.identify_chainseg(pdb_input)

    ncomponents = len(chainsegs)

    input_str += f'eval ($ncomponents={ncomponents}){os.linesep}'

    for i, segid in enumerate(chainsegs):
        input_str += f'eval ($prot_segid_mol{i+1}="{segid}"){os.linesep}'

    try:
        ambig_fname = glob.glob(os.path.join(course_path, 'ambig.tbl'))[0]
        input_str += f'eval ($ambig_fname="{ambig_fname}"){os.linesep}'
    except IndexError:
        input_str += f'eval ($ambig_fname=""){os.linesep}'

    try:
        unambig_fname = glob.glob(os.path.join(course_path, 'unambig.tbl'))[0]
        input_str += f'eval ($unambig_fname="{unambig_fname}"){os.linesep}'
    except IndexError:
        input_str += f'eval ($unambig_fname=""){os.linesep}'

    try:
        hbond_fname = glob.glob(os.path.join(course_path, 'hbond.tbl'))[0]
        input_str += f'eval ($hbond_fname="{hbond_fname}"){os.linesep}'
    except IndexError:
        input_str += f'eval ($hbond_fname=""){os.linesep}'

    try:
        dihe_fname = glob.glob(os.path.join(course_path, 'dihe.tbl'))[0]
        input_str += f'eval ($dihe_fname="{dihe_fname}"){os.linesep}'
    except IndexError:
        input_str += f'eval ($dihe_fname=""){os.linesep}'

    try:
        tensor_fname = glob.glob(os.path.join(course_path, 'tensor.tbl'))[0]
        input_str += f'eval ($tensor_tbl="{tensor_fname}"){os.linesep}'
    except IndexError:
        input_str += f'eval ($tensor_fname=""){os.linesep}'

    rnd = RandomNumberGenerator()
    seed = rnd.randint(100, 999)
    input_str += f'eval ($seed={seed}){os.linesep}'

    return input_str


def prepare_output(output_psf_filename, output_pdb_filename):
    """Output of the CNS file"""
    output = f'{os.linesep}! Output structure{os.linesep}'
    output += f"eval ($output_psf_filename= \"{output_psf_filename}\"){os.linesep}"
    output += f"eval ($output_pdb_filename= \"{output_pdb_filename}\"){os.linesep}"
    return output


def load_protonation_state(protononation):
    """Prepare the CNS protononation"""
    protonation_header = ''
    if protononation and isinstance(protononation, dict):
        protonation_header += f'{os.linesep}! Protonation states{os.linesep}'

        for i, chain in enumerate(protononation):
            hise_l = [0] * 10
            hisd_l = [0] * 10
            hisd_counter = 0
            hise_counter = 0
            for res in protononation[chain]:
                state = protononation[chain][res].lower()
                if state == 'hise':
                    hise_l[hise_counter] = res
                    hise_counter += 1
                if state == 'hisd':
                    hisd_l[hisd_counter] = res
                    hisd_counter += 1

            hise_str = ''
            for e in [(i+1, c+1, r) for c, r in enumerate(hise_l)]:
                hise_str += f'eval ($toppar.hise_resid_{e[0]}_{e[1]} = {e[2]}){os.linesep}'
            hisd_str = ''
            for e in [(i+1, c+1, r) for c, r in enumerate(hisd_l)]:
                hisd_str += f'eval ($toppar.hisd_resid_{e[0]}_{e[1]} = {e[2]}){os.linesep}'

            protonation_header += hise_str
            protonation_header += hisd_str

    return protonation_header


def load_ff_parameters(forcefield_parameters):
    """Add force-field specific parameters to its appropriate places"""
    ff_param_header = f'{os.linesep}! FF parameters{os.linesep}'
    ff_param_header += f'parameter{os.linesep}'
    ff_param_header += f'  @@{forcefield_parameters}{os.linesep}'
    ff_param_header += f'end{os.linesep}'

    return ff_param_header


def load_ff_topology(forcefield_topology):
    """Add force-field specific topology to its appropriate places"""
    ff_top_header = f'{os.linesep}! Toplogy{os.linesep}'
    ff_top_header += f'topology{os.linesep}'
    ff_top_header += f'  @@{forcefield_topology}{os.linesep}'
    ff_top_header += f'end{os.linesep}'

    return ff_top_header


def load_link(mol_link):
    """Add the link header"""
    link_header = f'{os.linesep}! Link file{os.linesep}'
    link_header += f'eval ($link_file = "{mol_link}" ){os.linesep}'

    return link_header


def load_trans_vectors(trans_vectors):
    """Add translation vectors"""
    trans_header = f'{os.linesep}! Translation vectors{os.linesep}'
    for vector_id in trans_vectors:
        vector_file = trans_vectors[vector_id]
        trans_header += f'eval ($trans_vector_{vector_id} = "{vector_file}" ){os.linesep}'

    return trans_header


def load_tensor(tensor):
    """Add tensor information"""
    tensor_header = f'{os.linesep}! Tensors{os.linesep}'
    for tensor_id in tensor:
        tensor_file = tensor[tensor_id]
        tensor_header += f'eval (${tensor_id} = "{tensor_file}" ){os.linesep}'

    return tensor_header


def load_axis(axis):
    """Add axis"""
    axis_header = f'{os.linesep}! Axis{os.linesep}'
    for axis_id in axis:
        axis_file = axis[axis_id]
        axis_header += f'eval (${axis_id} = "{axis_file}" ){os.linesep}'

    return axis_header


def load_scatter(scatter_lib):
    """Add scatter library"""
    scatter_header = f'{os.linesep}! Scatter lib{os.linesep}'
    scatter_header += f'eval ($scatter_lib = "{scatter_lib}" ){os.linesep}'

    return scatter_header


def load_waterbox(waterbox_param):
    """Add waterbox information"""
    water_header = f'{os.linesep}! Water box{os.linesep}'
    water_header += f'eval ($boxtyp20 = "{waterbox_param}" ){os.linesep}'

    return water_header
