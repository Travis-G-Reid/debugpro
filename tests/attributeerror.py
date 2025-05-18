from debugpro import install_custom_excepthook

def test_AttributeError():
    my_dict = {'a': 1, 'b': 2, 'c': 3}
    my_dict.grab_item('a')  # This will raise an AttributeError

if __name__ == "__main__":
    install_custom_excepthook()
    test_AttributeError()
