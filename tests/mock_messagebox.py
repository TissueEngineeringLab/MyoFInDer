# coding: utf-8

def askyesno(*_, **__) -> bool:
    """Mocks a call to tkinter.messagebox.askyesno().
    
    Normally returns the choice of the user between a "yes" and a "no" option.
    """

    return True
