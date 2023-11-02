from typing import Optional

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def ask_yes_no_question(
    prompt: str, *, default_answer: Optional[bool] = None
) -> bool:
    """
    Asks the user a yes/no question using the given prompt.

    As an example, for prompt="Do you love python?";
    will ask the user 'Do you love python? y/n ', without ''.
    Will continue asking until the user answers a valid answer.

    :param prompt: The prompt to ask the user.
    :param default_answer:
                    Specifies what happens when user doesn't input anything or
                        inputs spaces.
                    True=>'Y', False=>'N'.
                    Capitalizes the default choice.
                    When none specified (default), will not capitalize.
    :return: True if yes, False if no

    :raises TypeError: When default_answer is not bool and not None.

    :type prompt: str
    :type default_answer: Optional[bool]
    :rtype: bool
    """

    # Will be used as not case sensitive
    VALID_YES = {"yes", "ye", "y", "true", "t", "1"}
    VALID_NO = {"no", "n", "false", "f", "0"}

    POSSIBLE_DISPLAYED_CHOICES = {True: "Y/n", False: "y/N", None: "y/n"}

    if default_answer not in POSSIBLE_DISPLAYED_CHOICES:
        raise TypeError(f"default_answer expected to be bool/None, but got {type(default_answer)}.")

    displayed_choice = POSSIBLE_DISPLAYED_CHOICES[default_answer]

    full_prompt = f"{prompt} {bcolors.BOLD}[{displayed_choice}]{bcolors.ENDC} "

    while True:
        user_answer = input(full_prompt).lower().strip()

        if not user_answer and default_answer is not None:
            return default_answer

        if user_answer in VALID_YES:
            return True
        elif user_answer in VALID_NO:
            return False
