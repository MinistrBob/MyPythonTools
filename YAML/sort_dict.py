def sort_keys_recursive(d):
    if isinstance(d, dict):
        sorted_dict = {}
        for key in sorted(d.keys()):
            sorted_dict[key] = sort_keys_recursive(d[key])
        return sorted_dict
    else:
        return d

# Example usage:
complex_dict = {
    'b': {'d': 4, 'c': 3, 'a': 1},
    'e': {'g': {'i': 9, 'h': 8}, 'f': 6},
    'j': 10,
    'k': [5, 4, 3],
    'l': 'string'
}

sorted_dict = sort_keys_recursive(complex_dict)
print(sorted_dict)
