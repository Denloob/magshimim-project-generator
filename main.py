#!/bin/python3

import os
import sys
import solution
from typing import List
from shutil import copyfile
from utils import ask_yes_no_question

PROJECT_PROGRAM_NAME = "prog.c"
SOURCE_FILE_EXTENTIONS = ".c"
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


def get_filenames(path: str) -> List[str]:
    """Returns a list of .c file names in the given directory."""
    filenames = []
    for filename in os.listdir(path):
        if filename.endswith(SOURCE_FILE_EXTENTIONS):
            filenames.append(filename)
    return filenames


def remove_extension(filename: str) -> str:
    """Removes the .c extension from the filename."""
    return os.path.splitext(filename)[0]


def main(source_dir: str, output_dir: str, solution_name: str):
    # Get a list of .c files in the source directory
    filenames = get_filenames(source_dir)
    print(
        f"Found {len(filenames)} {SOURCE_FILE_EXTENTIONS} files in {source_dir}."
    )

    # Ask the user which files to include in the build
    selected_filenames = [
        filename
        for filename in filenames
        if ask_yes_no_question(
            f"Include {filename} in the build?", default_answer=True
        )
    ]
    print(f"Selected {len(selected_filenames)} files for the build.")

    filename_modifier = (
        str.capitalize
        if ask_yes_no_question(
            "Should the project names be Capitalized?", default_answer=True
        )
        else lambda x: x
    )

    # Generate the solution file using solution.generate_sln
    sln_str, projects, _ = solution.generate_sln(
        map(remove_extension, selected_filenames), filename_modifier
    )
    print("Generated solution file.")

    # Write the solution file to the output directory
    output_path = os.path.join(output_dir, f"{solution_name}.sln")
    with open(output_path, "w") as f:
        f.write(sln_str)
    print(f"Wrote solution file to {output_path}.")

    for (project_name, project_guid), filename in zip(
        projects.items(), selected_filenames
    ):
        file_path = os.path.join(source_dir, filename)
        project_path = os.path.join(output_dir, project_name)
        prog_path = os.path.join(project_path, PROJECT_PROGRAM_NAME)
        project_vcxproj_path = os.path.join(
            project_path, project_name + VCXPROJ_EXT
        )
        project_vcxproj_filter_path = os.path.join(
            project_path, project_name + VCXPROJ_FILTER_EXT
        )
        os.mkdir(project_path)
        copyfile(file_path, prog_path)
        copyfile(VCXPROJ_FILTERS_TEMPLATE_PATH, project_vcxproj_filter_path)
        with open(VCXPROJ_TEMPLATE_PATH, "r") as template, open(
            project_vcxproj_path, "w"
        ) as f:
            f.write(
                template.read()
                .replace("$GUID", str(project_guid))
                .replace("$NAME", project_name)
            )

        print(f"Project {project_name} built.")

    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            f"Usage: python {sys.argv[0]} source_dir output_dir solution_name"
        )
        sys.exit(1)

    source_dir = sys.argv[1]
    output_dir = sys.argv[2]
    solution_name = sys.argv[3]

    main(source_dir, output_dir, solution_name)
