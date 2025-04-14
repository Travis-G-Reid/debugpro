from debug_pro.excepthook import install_custom_excepthook

def test_IndexError():
    my_list = [1, 2, 3]
    my_list[4]

if __name__ == "__main__":
    install_custom_excepthook()
    test_IndexError()
