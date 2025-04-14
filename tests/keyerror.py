from debugpro import install_custom_excepthook

def test_KeyError():
    my_dict = {'a': 1, 'b': 2, 'c': 3}
    my_dict[5]

if __name__ == "__main__":
    install_custom_excepthook()
    test_KeyError()
