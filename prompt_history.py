#Created by 0xChaitanya, on 22nd July
#for issue #2

stack_of_prompts = [] #this list stores all prompts
number_of_prompts = 0
stack_pointer = 0

def add(prompt) -> None:
    global stack_of_prompts, number_of_prompts, stack_pointer
    stack_of_prompts.append(prompt)
    number_of_prompts += 1
    stack_pointer = number_of_prompts

def current_prompt_number() -> int:
    return stack_pointer

def undo() -> int:
    global stack_pointer, number_of_prompts
    if (stack_pointer > 0):
        stack_pointer -= 1
        return stack_pointer
    return -1

def redo() -> int:
    global stack_pointer, number_of_prompts
    if (stack_pointer < number_of_prompts):
        stack_pointer += 1
        return stack_pointer
    return -1

def show_prompts():
    global stack_of_prompts
    return stack_of_prompts