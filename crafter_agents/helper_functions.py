def matrix_to_string(matrix):
    """
    Convert a matrix to a string with newlines between rows.
    
    Args:
        matrix: A list of lists representing a matrix
        
    Returns:
        str: A string representation of the matrix with newlines between rows
    """
    # Convert each row to a string and join them with newlines
    return '\n'.join(str(row) for row in matrix)


def add_newlines(text: str, words_per_line: int = 10) -> str:
    if text!=None:
        # Split the text into words
        words = text.split()
        
        # Initialize an empty list to store the result
        result = []
        
        # Iterate through the words, adding newlines after every 'words_per_line' words
        for i in range(0, len(words), words_per_line):
            line = ' '.join(words[i:i+words_per_line])
            result.append(line)
        
        # Join the lines with newline characters
        return '\n        '.join(result)
    return None

def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])


def target_material_prompt(agent):
            if agent.game_state.target_material!=None:
                return f"the material in front of you is {agent.game_state.target_material}\n"
            else:
                return "there is no material in front of you\n"
def target_obj_prompt(agent):
    if agent.game_state.target_obj!=None:
        return f"the object in front of you is {agent.game_state.target_obj}\n"
    else:
        return "there is no object in front of you\n"