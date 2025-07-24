#Created by 0xChaitanya, on 22nd July
#for issue #2

stack_of_prompts = ["Describe what you'd like to change...\n\nExample: Make the header purple, add a contact form, or change the font to something more modern"]
code_of_prompts = []
number_of_prompts = 0
stack_pointer = 0

def push_prompt(prompt) -> None:
    global stack_of_prompts, number_of_prompts, stack_pointer
    stack_of_prompts.append(prompt)
    number_of_prompts += 1
    stack_pointer = number_of_prompts

def pop_prompt():
    global stack_of_prompts, number_of_prompts, stack_pointer
    number_of_prompts -= 1
    stack_pointer = number_of_prompts
    return stack_of_prompts.pop()

def push_code(code):
    global code_of_prompts, number_of_prompts, stack_pointer
    code_of_prompts.append(code)

def pop_code():
    return code_of_prompts.pop()

def current_prompt_number() -> int:
    return stack_pointer

def undo():
    global stack_pointer, number_of_prompts, stack_of_prompts
    if (stack_pointer > 0):
        stack_pointer -= 1
        return stack_pointer
    return 1

def redo():
    global stack_pointer, number_of_prompts
    if (stack_pointer < number_of_prompts):
        stack_pointer += 1
        return stack_pointer
    return number_of_prompts

def show_prompts():
    global stack_of_prompts
    return stack_of_prompts

def get_current_prompt():
    return stack_of_prompts[stack_pointer]

def get_current_code():
    return code_of_prompts[stack_pointer]