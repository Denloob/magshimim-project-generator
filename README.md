# VisualStudio project generator

Set of util scripts for creating Magshimim Exercises (Homework questions)
into VisualStudio Solutions and Projects.

## Quick Start

### Basic usage: 
```sh
python main.py source_dir output_dir solution_name
```

Say you have
```sh
/home/Magshimim/week1/
- q1.c
- q2.c
- q3.c
- final_answer/
```

You can run
```sh
python main.py /home/Magshimim/week1/ /home/Magshimim/week1/final_answer/ week1
```
This will create a VisualStudio solution with the name week1 in the directory `final_answer/`
