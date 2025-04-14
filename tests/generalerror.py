from debugpro.excepthook import install_custom_excepthook

if __name__ == "__main__":
    install_custom_excepthook()
    raise Exception("This is a general exception. Verify that the error is as expected.")
