# VisualStudio project generator

Set of util scripts for creating Magshimim Exercises (Homework questions)
into VisualStudio Solutions and Projects.

> [!NOTE]
> This version was tailored for the C++ course. You might be interested in the [C course version](https://github.com/Denloob/magshimim-project-generator/tree/1.0.0).

## Quick Start

### Basic usage: 
```sh
python main.py <source_dir> <output_dir> <solution_name>
```

Say you have
```sh
/home/Magshimim/week1/
- Stack.cpp
- Stack.h
- main.cpp
- final_answer/
```

You can run
```sh
python main.py /home/Magshimim/week1/ /home/Magshimim/week1/final_answer/ DataStructures
```
This will create a VisualStudio solution with the name DataStructures in the directory `final_answer/`

<br>

### Shortened usage:
```sh
python main.py <source_dir>
```

Say you have
```sh
/home/Magshimim/week1/
- /DataStructures
  - Stack.cpp
  - Stack.h
  - main.cpp
```
You can run
```bash
python main.py DataStructures
```
This will create a VisualStudio solution with the name DataStructures in the directory `DataStructures/`

<br>

```bash
Visual Studio Project Generator

Basic Usage:
    python main.py <source_dir> <output_dir> <solution_name>
Shortened Usage:
    python main.py <source_dir>

*Note*: In Shortened Usage, source_dir = output_dir, and the .sln file name is the <source_dir> name.

Flags:
    -h    Show this help message
    -y    Accept all files
    -o    Overwrite project if already exists

Examples:
    Shortened Usage:
        python main.py DataStructures
```

## Contributing

Any help is appreciated!

## License

This project is licensed under the **GNU General Public License v3**.

See [LICENSE](LICENSE) for more information.
