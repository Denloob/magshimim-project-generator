"""
Visual Studio Solution Generator; With love by den@denloob.tk

WARNING: a lot of hardcoded stuff, please forgive me, at least I documented it :D

NamingNotationConventions:
---
Every global _SLN var with _TEMPLATE suffix has some variable to replace for
 example all occurrences of $NAME should be replaced with project name.

Global _SLN variables explained:
----
_SLN_HEADER - the thing that comes first
_SLN_PROJECT_TEMPLATE - declaration for each of the projects
    $NAME - project name
    $GUID - project GUID
_SLN_GLOBAL_HEADER - comes after the project declarations
_SLN_GLOBAL_PROJECT_CONFIG_TEMPLATE - config for each of the projects
    $GUID - project GUID
_SLN_GLOBAL_END_TEMPLATE - the footer of the whole SLN file
    $SOLUTION_GUID - GUID for this solution
"""

from typing import Iterable, Dict, Tuple
import uuid


_SLN_HEADER = """\
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 16
VisualStudioVersion = 16.0.31702.278
MinimumVisualStudioVersion = 10.0.40219.1
"""

# The hardcoded GUID (8BC9CE...C942) is project type GUID (Magshimim_EX)
_SLN_PROJECT_TEMPLATE = """\
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "$NAME", "$NAME.vcxproj", "{$GUID}"
EndProject
"""
_SLN_GLOBAL_HEADER = """\
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|x64 = Debug|x64
		Debug|x86 = Debug|x86
		Release|x64 = Release|x64
		Release|x86 = Release|x86
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
"""
_SLN_GLOBAL_PROJECT_CONFIG_TEMPLATE = """\
		{$GUID}.Debug|x64.ActiveCfg = Debug|x64
		{$GUID}.Debug|x64.Build.0 = Debug|x64
		{$GUID}.Debug|x86.ActiveCfg = Debug|Win32
		{$GUID}.Debug|x86.Build.0 = Debug|Win32
		{$GUID}.Release|x64.ActiveCfg = Release|x64
		{$GUID}.Release|x64.Build.0 = Release|x64
		{$GUID}.Release|x86.ActiveCfg = Release|Win32
		{$GUID}.Release|x86.Build.0 = Release|Win32
"""
_SLN_GLOBAL_END_TEMPLATE = """\
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
	GlobalSection(ExtensibilityGlobals) = postSolution
		SolutionGuid = {$SOLUTION_GUID}
	EndGlobalSection
EndGlobal
"""

def filenames_to_uuids(filenames: Iterable[str]) -> Dict[str, uuid.UUID]:
    """
    Generates a dictionary of filename:UUID from the given filenames.

    @param filenames list of file names for which to generate the dictionary.
    @return a dictionary of filename:UUID.
    """

    return {filename: uuid.uuid4() for filename in filenames}

def generate_sln(
    solution_name
) -> Tuple[str, uuid.UUID, uuid.UUID]:
    """
    Generates a VisualStudio sln file for a project in the same dir as the sln.

    @param solution_name the name of the whole solution. This will be the name of the project.
    @return the generated sln file as a string,
           project GUID,
           and solution GUID.

    @todo maybe instead of .replace use something better than just text juggling.
    """

    project_name = solution_name
    project_guid = uuid.uuid4()

    solution = _SLN_HEADER
    solution_guid = uuid.uuid4()

    solution += _SLN_PROJECT_TEMPLATE.replace(
        "$NAME", project_name
    ).replace("$GUID", str(project_guid))

    solution += _SLN_GLOBAL_HEADER

    solution += _SLN_GLOBAL_PROJECT_CONFIG_TEMPLATE.replace(
        "$GUID", str(project_guid)
    )

    solution += _SLN_GLOBAL_END_TEMPLATE.replace(
        "$SOLUTION_GUID", str(solution_guid)
    )

    return (solution, project_guid, solution_guid)


def main():
    print("Example sln generation for the files q1.c q2.c q3.c and the functions upper() and replace('.c', ''):")
    sln, projects, sln_guid = generate_sln(
        filename.replace(".c", "").upper() for filename in ["q1.c", "q2.c", "q3.c"]
    )
    print(f"{projects=}")
    print(f"{sln_guid=}")
    print(sln)


if __name__ == "__main__":
    main()
