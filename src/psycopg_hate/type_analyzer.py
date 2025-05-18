import pytest
from typing import Any, Union, get_origin, get_args

def get_complex_type_annotation(data):
    """Return a proper typing annotation for an arbitrarily complex Python object using PEP 585 syntax."""
    if data is None:
        return type(None)
    
    if isinstance(data, dict):
        if not data:
            return dict[Any, Any]
        
        # Get key and value types
        key_types = set(get_complex_type_annotation(k) for k in data.keys())
        value_types = set(get_complex_type_annotation(v) for v in data.values())
        
        # Create union types if necessary
        key_type = key_types.pop() if len(key_types) == 1 else Union[tuple(key_types)]
        value_type = value_types.pop() if len(value_types) == 1 else Union[tuple(value_types)]
        
        return dict[key_type, value_type]
    
    elif isinstance(data, list):
        if not data:
            return list[Any]
        
        # Get element types
        element_types = set(get_complex_type_annotation(item) for item in data)
        element_type = element_types.pop() if len(element_types) == 1 else Union[tuple(element_types)]
        
        return list[element_type]
    
    elif isinstance(data, tuple):
        if not data:
            return tuple[()]
        
        # For tuples, we preserve the exact types in order
        return tuple[tuple(get_complex_type_annotation(item) for item in data)]
    
    elif isinstance(data, set):
        if not data:
            return set[Any]
        
        element_types = set(get_complex_type_annotation(item) for item in data)
        element_type = element_types.pop() if len(element_types) == 1 else Union[tuple(element_types)]
        
        return set[element_type]
    
    else:
        return type(data)

def type_to_string(type_anno):
    """Convert a type annotation to a readable string using PEP 585 syntax."""
    origin = get_origin(type_anno)
    
    if origin is None:
        if type_anno is Any:
            return "Any"
        return type_anno.__name__
    
    args = get_args(type_anno)
    
    if origin is Union:
        return f"Union[{', '.join(type_to_string(arg) for arg in args)}]"
    
    if origin is dict:
        return f"dict[{type_to_string(args[0])}, {type_to_string(args[1])}]"
    
    if origin is list:
        return f"list[{type_to_string(args[0])}]"
    
    if origin is tuple:
        return f"tuple[{', '.join(type_to_string(arg) for arg in args)}]"
    
    if origin is set:
        return f"set[{type_to_string(args[0])}]"
    
    return str(type_anno)


class TestTypeAnnotation:
    """Test cases for the type annotation functions."""
    
    def test_primitive_types(self):
        """Test handling of primitive types."""
        assert type_to_string(get_complex_type_annotation(None)) == "NoneType"
        assert type_to_string(get_complex_type_annotation(42)) == "int"
        assert type_to_string(get_complex_type_annotation("hello")) == "str"
        assert type_to_string(get_complex_type_annotation(3.14)) == "float"
        assert type_to_string(get_complex_type_annotation(True)) == "bool"
    
    def test_empty_collections(self):
        """Test handling of empty collections."""
        assert type_to_string(get_complex_type_annotation([])) == "list[Any]"
        assert type_to_string(get_complex_type_annotation({})) == "dict[Any, Any]"
        assert type_to_string(get_complex_type_annotation(())) == "tuple[]"
        assert type_to_string(get_complex_type_annotation(set())) == "set[Any]"
    
    def test_homogeneous_collections(self):
        """Test handling of homogeneous collections."""
        assert type_to_string(get_complex_type_annotation([1, 2, 3])) == "list[int]"
        assert type_to_string(get_complex_type_annotation({"a": 1, "b": 2, "c": 3})) == "dict[str, int]"
        assert type_to_string(get_complex_type_annotation((1, 2, 3))) == "tuple[int, int, int]"
        assert type_to_string(get_complex_type_annotation({1, 2, 3})) == "set[int]"
    
    def test_heterogeneous_collections(self):
        """Test handling of heterogeneous collections."""
        # For list with mixed types
        mixed_list_result = type_to_string(get_complex_type_annotation([1, "two", 3.0, True]))
        assert "list[Union[" in mixed_list_result
        assert "bool" in mixed_list_result
        assert "float" in mixed_list_result
        assert "int" in mixed_list_result
        assert "str" in mixed_list_result
        
        # For dict with mixed value types
        mixed_dict_result = type_to_string(get_complex_type_annotation({"a": 1, "b": "two", "c": 3.0}))
        assert "dict[str, Union[" in mixed_dict_result
        assert "float" in mixed_dict_result
        assert "int" in mixed_dict_result
        assert "str" in mixed_dict_result
        
        # For tuple with mixed types
        # Since tuples maintain order, we can check exact string
        assert type_to_string(get_complex_type_annotation((1, "two", 3.0))) == "tuple[int, str, float]"
        
        # For set with mixed types
        mixed_set_result = type_to_string(get_complex_type_annotation({1, "two", 3.0}))
        assert "set[Union[" in mixed_set_result
        assert "float" in mixed_set_result
        assert "int" in mixed_set_result
        assert "str" in mixed_set_result
    
    def test_mixed_key_types(self):
        """Test handling of dictionaries with mixed key types."""
        mixed_keys_result = type_to_string(get_complex_type_annotation({1: "one", "two": 2, 3.0: "three"}))
        assert "dict[Union" in mixed_keys_result
        assert "int" in mixed_keys_result
        assert "str" in mixed_keys_result
        assert "float" in mixed_keys_result
    
    def test_nested_collections(self):
        """Test handling of nested collections."""
        assert type_to_string(get_complex_type_annotation([[1, 2], [3, 4]])) == "list[list[int]]"
        assert type_to_string(get_complex_type_annotation({"a": [1, 2], "b": [3, 4]})) == "dict[str, list[int]]"
        assert type_to_string(get_complex_type_annotation(([1, 2], [3, 4]))) == "tuple[list[int], list[int]]"
    
    def test_mixed_nested_collections(self):
        """Test handling of mixed nested collections."""
        assert type_to_string(get_complex_type_annotation([1, {"a": 2}])) == "list[Union[int, dict[str, int]]]"
        assert type_to_string(get_complex_type_annotation({"a": 1, "b": [2, 3]})) == "dict[str, Union[int, list[int]]]"
        assert type_to_string(get_complex_type_annotation((1, [2, 3], {"a": 4}))) == "tuple[int, list[int], dict[str, int]]"
    
    def test_deeply_nested_collections(self):
        """Test handling of deeply nested collections."""
        users_data = {
            "users": [
                {"name": "Alice", "scores": [98, 95], "metadata": {"joined": "2023-01-01"}},
                {"name": "Bob", "scores": [85, 90], "metadata": {"joined": "2023-02-15"}}
            ]
        }
        result = type_to_string(get_complex_type_annotation(users_data))
        assert "dict[str, list[dict[str" in result
        assert "name" not in result  # We only care about types, not field names
        assert "str" in result
        assert "int" in result
    
    def test_complex_hierarchical_structures(self):
        """Test handling of complex hierarchical structures."""
        complex_data = {
            "id": 1,
            "name": "Project X",
            "tasks": [
                {"id": 101, "status": "complete", "subtasks": [{"id": 1001}, {"id": 1002}]},
                {"id": 102, "status": "pending", "assignees": ["Alice", "Bob"]}
            ],
            "metadata": {
                "created": "2023-01-01",
                "tags": ["urgent", "development"],
                "stats": {"completion": 0.75, "hours": 120}
            }
        }
        result = type_to_string(get_complex_type_annotation(complex_data))
        assert "dict[str, Union" in result
        assert "float" in result
        assert "int" in result
        assert "str" in result
        assert "list" in result
    
    def test_edge_cases(self):
        """Test handling of unusual edge cases."""
        assert type_to_string(get_complex_type_annotation([[[[[]]]]])) == "list[list[list[list[list[Any]]]]]"
        assert type_to_string(get_complex_type_annotation({"a": {"b": {"c": {"d": {}}}}})) == "dict[str, dict[str, dict[str, dict[str, dict[Any, Any]]]]]"
        assert type_to_string(get_complex_type_annotation([1, [2, [3, [4]]]])) == "list[Union[int, list[Union[int, list[Union[int, list[int]]]]]]]"
        
        mixed_empty_result = type_to_string(get_complex_type_annotation([{}, [], (), set()]))
        assert "list[Union" in mixed_empty_result
        assert "dict[Any, Any]" in mixed_empty_result
        assert "list[Any]" in mixed_empty_result
        assert "tuple[]" in mixed_empty_result
        assert "set[Any]" in mixed_empty_result

# For running with pytest
if __name__ == "__main__":
    pytest.main(["-v", __file__])