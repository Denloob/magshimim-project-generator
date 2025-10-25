#!/bin/python3

import os
import sys
import uuid
import solution
from typing import Iterable, List, NoReturn, Optional, Tuple, TextIO, Union
from shutil import copyfile
from utils import ask_yes_no_question, bcolors
from pathlib import Path

TEMPLATES_DIR_PATH = Path(__file__).parent / "templates"

VCXPROJ_EXT = ".vcxproj"
VCXPROJ_FILTER_EXT = VCXPROJ_EXT + ".filters"

VCXPROJ_TEMPLATE_PATH = Path(TEMPLATES_DIR_PATH, "template" + VCXPROJ_EXT)
VCXPROJ_FILTERS_TEMPLATE_PATH = Path(
    TEMPLATES_DIR_PATH, "template" + VCXPROJ_FILTER_EXT
)

SOURCE_EXTENSIONS = [
    "cpp",
    "c",
    "cc",
    "cxx",
    "def",
    "odl",
    "idl",
    "hpj",
    "bat",
    "asm",
    "asmx",
]
HEADER_EXTENSIONS = [
    "h",
    "hh",
    "hpp",
    "hxx",
    "hm",
    "inl",
    "inc",
    "ipp",
    "xsd",
]
RESOURCE_EXTENSIONS = [
    "rc",
    "ico",
    "cur",
    "bmp",
    "dlg",
    "rc2",
    "rct",
    "bin",
    "rgs",
    "gif",
    "jpg",
    "jpeg",
    "jpe",
    "resx",
    "tiff",
    "tif",
    "png",
    "wav",
    "mfcribbon-ms",
]

FLAG_PREFIX = '-'
FLAG_LEN = 1
ACCEPT_ALL_FLAG = 'y'
HELP_FLAG = 'h'
OVERWRITE_FLAG = 'o'
RECURSE_SUBDIRS_FLAG = 'r'

MAIN_PY = 'main.py'
USAGE_MESSAGE = f"usage: python {MAIN_PY} <source_dir> [(<dest_dir> <solution_name>)] [-h -y -r -o]"

BASIC_USAGE_MESSAGE = "Basic Usage:\n    python %s <source_dir> <output_dir> <solution_name>"
SHORT_USAGE_MESSAGE = "Shortened Usage:\n    python %s <source_dir>"
HELP_MESSAGE = f'''
{bcolors.BOLD}{bcolors.WARNING}Visual Studio Project Generator{bcolors.ENDC}{bcolors.ENDC}


{BASIC_USAGE_MESSAGE % MAIN_PY}
{SHORT_USAGE_MESSAGE % MAIN_PY}

*Note*: In Shortened Usage, source_dir = output_dir, and the .sln file name is the <source_dir> name.

Flags:
    -h    Show this help message
    -y    Accept all files
    -r    Recursively add source files within subdirs
    -o    Overwrite project if already exists

Examples:
    Shortened Usage:
        python main.py DataStructures
'''


def get_filepaths(base_path: Union[str, os.PathLike], flags: list) -> List[str]:
    """Returns a list of supported filenames in the given directory."""
    is_src_file = lambda extension: extension in SOURCE_EXTENSIONS + HEADER_EXTENSIONS + RESOURCE_EXTENSIONS

    strip_start = lambda _path: _path.removeprefix(str(base_path)).removeprefix('/')
    def add_files_in_dir(path: Union[str, os.PathLike], recursive: bool) -> List[str]:
        """Adds all source file paths to local filepaths"""
        filepaths = []

        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)

            if os.path.isdir(full_path) and recursive:
                dir = strip_start(full_path)

                if ACCEPT_ALL_FLAG in flags or \
                        ask_yes_no_question(f"Include subdir {bcolors.BOLD}{bcolors.OKCYAN}{dir}{bcolors.ENDC}{bcolors.ENDC} in the build?", default_answer=True):
                    filepaths.extend(add_files_in_dir(os.path.join(path, filename), recursive))
                continue

            extension = Path(full_path).suffix.removeprefix('.')
            if os.path.isfile(full_path) and is_src_file(extension):
                filepaths.append(strip_start(full_path))

        return filepaths

    return add_files_in_dir(base_path, RECURSE_SUBDIRS_FLAG in flags)


def remove_extension(filename: str) -> str:
    """Removes the source file extension (.c, .cpp, ...) from the filename."""
    return os.path.splitext(filename)[0]


def to_items(files: List[str], item_type: str) -> str:
    """Converts a list of files, into `item_type` items for .vcxproj"""
    convert = lambda file: f'<{item_type} Include="{file}" />'
    return "\n".join(map(convert, files))


def to_include_dirs(include_dirs: Iterable[str]) -> str:
    """Converts a list of include directories into AdditionalIncludeDirectories tag in .vcxproj"""
    return "<AdditionalIncludeDirectories>" + ';'.join(f'$(SolutionDir){dir}' for dir in include_dirs if dir != "") + "</AdditionalIncludeDirectories>"


def to_compile_items(files: List[str]) -> str:
    """Converts a list of files, into ClCompile items for .vcxproj"""
    return to_items(files, "ClCompile")


def to_include_items(files: List[str]) -> str:
    """Converts a list of files, into ClInclude items for .vcxproj"""
    return to_items(files, "ClInclude")


def to_filter_items(
    sources: List[str] = [], headers: List[str] = [], resources: List[str] = []
) -> str:
    """Converts a list of sources, headers and resources into ClCompile and ClInclude with filter for .vcxproj.filter"""

    if resources:
        raise NotImplementedError("Resources are not yet supported")

    convert = (
        lambda file, filter_type, include_type: f"""<{include_type} Include="{file}">
      <Filter>{filter_type}</Filter>
    </{include_type}>"""
    )

    convert_files = lambda files, filter_type, include_type: "\n".join(
        convert(file, filter_type, include_type) for file in files
    )

    return "\n".join(
        convert_files(files, filter_type, include_type)
        for files, filter_type, include_type in [
            (sources, "Source Files", "ClCompile"),
            (headers, "Header Files", "ClInclude"),
            (resources, "Resource Files", ""), # Not implemented
        ]
    )


def split_filenames_by_their_type(
    filenames: List[str],
) -> Tuple[List[str], List[str], List[str]]:
    """Splits filenames by their extension into a tuple of (sources, headers, resources)"""

    check_type = lambda extensions, filename: any(
        filename.endswith(extension) for extension in extensions
    )

    sources = [
        filename
        for filename in filenames
        if check_type(SOURCE_EXTENSIONS, filename)
    ]
    headers = [
        filename
        for filename in filenames
        if check_type(HEADER_EXTENSIONS, filename)
    ]
    resources = [
        filename
        for filename in filenames
        if check_type(RESOURCE_EXTENSIONS, filename)
    ]

    return (sources, headers, resources)


def get_solution(solution_path: Union[str, os.PathLike], always_overwrite: bool) -> Tuple[str, uuid.UUID, uuid.UUID]:
    """
    Wrapper around solution.load_sln and solution.generate_sln.
    If possible, and always_overwrite is False

    @param solution_path Path to the sln file to get (load/generate).
    @param always_overwrite If True, always overwrite the sln file.

    @return sln information (see referenced functions).

    @see solution.load_sln
    @see solution.generate_sln
    """

    update_sln = not always_overwrite and Path(solution_path).exists()
    if update_sln and (sln := solution.load_sln(solution_path)) is not None:
        return sln

    return solution.generate_sln(solution_name)


def main(source_dir: Path, output_dir: Path, solution_name: str, flags: list):
    # Get a list of .c files in the source directory
    filepaths = get_filepaths(source_dir, flags)
    print(
        f"Found {bcolors.BOLD}{bcolors.OKCYAN}{len(filepaths)}{bcolors.ENDC}{bcolors.ENDC} files in {bcolors.BOLD}{bcolors.OKCYAN}{source_dir}{bcolors.ENDC}{bcolors.ENDC}."
    )

    # Select files
    # Accept All flag or Ask the user which files to include in the build
    selected_filepaths = []
    for filepath in filepaths:
        if (ACCEPT_ALL_FLAG in flags or
                ask_yes_no_question(f"Include {bcolors.BOLD}{bcolors.OKCYAN}{filepath}{bcolors.ENDC}{bcolors.ENDC} in the build?", default_answer=True)):
            selected_filepaths.append(filepath)

    print(f"Selected {bcolors.BOLD}{bcolors.OKCYAN}{len(selected_filepaths)}{bcolors.ENDC}{bcolors.ENDC} files for the build.")

    include_dirs = set(os.path.dirname(fp) for fp in selected_filepaths if (fp.endswith('.h') or fp.endswith('.hpp')))

    solution_path = output_dir / f"{solution_name}.sln"

    sln_str, project_guid, _ = get_solution(
        solution_path, always_overwrite=(OVERWRITE_FLAG in flags)
    )

    project_name = solution_name

    if not output_dir.exists():
        output_dir.mkdir(parents=True) # create the directory if it doesn't exists (same for parent directories)
        print(f"Created output directory {bcolors.BOLD}{bcolors.OKCYAN}{output_dir}{bcolors.ENDC}{bcolors.ENDC}.")

    solution_path.write_text(sln_str)
    print(f"Wrote solution file to {bcolors.BOLD}{bcolors.OKCYAN}{solution_path}{bcolors.ENDC}{bcolors.ENDC}.")

    project_vcxproj_path = output_dir / (project_name + VCXPROJ_EXT)

    project_vcxproj_filter_path = output_dir / (project_name + VCXPROJ_FILTER_EXT)

    if not source_dir.samefile(output_dir):
        for filepath in selected_filepaths:
            os.makedirs(os.path.dirname(output_dir / filepath), exist_ok=True)
            copyfile(source_dir / filepath, output_dir / filepath)

    sources, headers, resources = split_filenames_by_their_type(
        selected_filepaths
    )

    project_vcxproj_filter_path.write_text(
        VCXPROJ_FILTERS_TEMPLATE_PATH.read_text().replace(
            "$FILTER_ITEMS", to_filter_items(sources, headers, resources)
        )
    )

    project_vcxproj_path.write_text(
        VCXPROJ_TEMPLATE_PATH.read_text()
        .replace("$GUID", str(project_guid))
        .replace("$NAME", project_name)
        .replace("$INCLUDE_DIRS",  to_include_dirs(include_dirs))
        .replace("$COMPILE_ITEMS", to_compile_items(sources))
        .replace("$INCLUDE_ITEMS", to_include_items(headers))
    )

    print(f"{bcolors.OKGREEN}Done!{bcolors.ENDC}")

def help(
    *,
    return_code: int = 0,
    file: TextIO = sys.stdout,
) -> NoReturn:
    print(HELP_MESSAGE, file=file)
    sys.exit(return_code)


def usage(
    *,
    return_code: int = 1,
    message: Optional[str] = None,
    file: TextIO = sys.stderr,
) -> NoReturn:
    if message is not None:
        print(message, file=file, end="\n\n")

    print(USAGE_MESSAGE, file=file)

    sys.exit(return_code)


if __name__ == "__main__":
    # Get flags
    flags = [i for i in sys.argv if FLAG_PREFIX in i and len(i) == len(FLAG_PREFIX) + FLAG_LEN]

    # Remove flags from argv
    argv = list(filter(lambda i: i not in flags, sys.argv))
    # Remove FLAG_PREFIX from flags
    flags = list(map(lambda i: i.replace(FLAG_PREFIX, ''), flags))

    # Show help message if HELP_FLAG
    if (HELP_FLAG in flags):
        help()

    if len(argv) == 2:
        # shortened version
        source_dir = argv[1]
        output_dir = argv[1]
        solution_name = argv[1]
    elif len(argv) == 4:
        source_dir = argv[1]
        output_dir = argv[2]
        solution_name = argv[3]
    else:
        help(return_code=1, file=sys.stderr)

    if not Path(source_dir).exists():
        usage(message=f"Directory {source_dir} must exist.")

    main(Path(source_dir), Path(output_dir), solution_name, flags)
