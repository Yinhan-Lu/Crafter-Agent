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

# Example usage
if __name__ == "__main__":
    # Test with the example matrix
    test_matrix = [[1, 2, 3], [4, 5, 6]]
    result = matrix_to_string(test_matrix)
    print("Input matrix:", test_matrix)
    print("Output string:")
    print(result) 