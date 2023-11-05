#!/bin/python3

import os
import sys
import solution
from typing import List, Tuple
from shutil import copyfile
from utils import ask_yes_no_question, bcolors

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR_PATH = os.path.dirname(SCRIPT_PATH)
TEMPLATES_DIR_PATH = os.path.join(SCRIPT_DIR_PATH, "templates/")
VCXPROJ_EXT = ".vcxproj"
VCXPROJ_FILTER_EXT = VCXPROJ_EXT + ".filters"
VCXPROJ_TEMPLATE_PATH = os.path.join(
    TEMPLATES_DIR_PATH, "template" + VCXPROJ_EXT
)
VCXPROJ_FILTERS_TEMPLATE_PATH = os.path.join(
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

MAIN_PY = 'main.py'
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

Examples:
    Shortened Usage:
        python main.py DataStructures
'''

def get_filenames(path: str) -> List[str]:
    """Returns a list of supported filenames in the given directory."""
    filenames = []
    for filename in os.listdir(path):
        if any(filename.endswith(extension) for extension in SOURCE_EXTENSIONS + HEADER_EXTENSIONS + RESOURCE_EXTENSIONS):
            filenames.append(filename)
    return filenames


def remove_extension(filename: str) -> str:
    """Removes the source file extension (.c, .cpp, ...) from the filename."""
    return os.path.splitext(filename)[0]

def to_items(files: List[str], item_type: str) -> str:
    """Converts a list of files, into `item_type` items for .vcxproj"""
    convert = lambda file: f'<{item_type} Include="{file}" />'
    return "\n".join(map(convert, files))

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


def main(source_dir: str, output_dir: str, solution_name: str, flags: list):
    # Get a list of .c files in the source directory
    filenames = get_filenames(source_dir)
    print(
        f"Found {bcolors.BOLD}{bcolors.OKCYAN}{len(filenames)}{bcolors.ENDC}{bcolors.ENDC} files in {bcolors.BOLD}{bcolors.OKCYAN}{source_dir}{bcolors.ENDC}{bcolors.ENDC}."
    )

    # Select files
    # Accept All flag or Ask the user which files to include in the build
    selected_filenames = []
    for filename in filenames:
        if (ACCEPT_ALL_FLAG in flags or
                ask_yes_no_question(f"Include {bcolors.BOLD}{bcolors.OKCYAN}{filename}{bcolors.ENDC}{bcolors.ENDC} in the build?", default_answer=True)):
            selected_filenames.append(filename)

    print(f"Selected {bcolors.BOLD}{bcolors.OKCYAN}{len(selected_filenames)}{bcolors.ENDC}{bcolors.ENDC} files for the build.")

    # Generate the solution file using solution.generate_sln
    sln_str, project_guid, _ = solution.generate_sln(solution_name)
    project_name = solution_name

    print("Generated solution file.")

    # Write the solution file to the output directory
    output_path = os.path.join(output_dir, f"{solution_name}.sln")
    with open(output_path, "w") as f:
        f.write(sln_str)
    print(f"Wrote solution file to {bcolors.BOLD}{bcolors.OKCYAN}{output_path}{bcolors.ENDC}{bcolors.ENDC}.")

    project_vcxproj_path = os.path.join(output_dir, project_name + VCXPROJ_EXT)

    project_vcxproj_filter_path = os.path.join(
        output_dir, project_name + VCXPROJ_FILTER_EXT
    )

    if (source_dir != output_dir):
        for filename in selected_filenames:
            file_path = os.path.join(source_dir, filename)
            prog_path = os.path.join(output_dir, filename)
            copyfile(file_path, prog_path)

    sources, headers, resources = split_filenames_by_their_type(
        selected_filenames
    )

    with open(VCXPROJ_FILTERS_TEMPLATE_PATH, "r") as template, open(
        project_vcxproj_filter_path, "w"
    ) as f:
        f.write(
            template.read().replace(
                "$FILTER_ITEMS",
                to_filter_items(sources, headers, resources),
            )
        )
    with open(VCXPROJ_TEMPLATE_PATH, "r") as template, open(
        project_vcxproj_path, "w"
    ) as f:
        f.write(
            template.read()
            .replace("$GUID", str(project_guid))
            .replace("$NAME", project_name)
            .replace("$COMPILE_ITEMS", to_compile_items(sources))
            .replace("$INCLUDE_ITEMS", to_include_items(headers))
        )

    print(f"{bcolors.OKGREEN}Done!{bcolors.ENDC}")


if __name__ == "__main__":
    # Get flags
    flags = [i for i in sys.argv if FLAG_PREFIX in i and len(i) == len(FLAG_PREFIX) + FLAG_LEN]

    # Remove flags from argv
    argv = list(filter(lambda i: i not in flags, sys.argv))
    # Remove FLAG_PREFIX from flags
    flags = list(map(lambda i: i.replace(FLAG_PREFIX, ''), flags))

    # Show help message if HELP_FLAG
    if (HELP_FLAG in flags):
        print(HELP_MESSAGE)
        sys.exit(0)

    if len(argv) == 2:
        # shortened version
        if (os.path.exists(argv[1])):
            source_dir = argv[1]
            output_dir = argv[1]
            solution_name = argv[1]
        else:
            print(HELP_MESSAGE)
            sys.exit(1)
    else:
        if len(argv) != 4:
            print(
                HELP_MESSAGE
            )
            sys.exit(1)

        source_dir = argv[1]
        output_dir = argv[2]
        solution_name = argv[3]

    main(source_dir, output_dir, solution_name, flags)
