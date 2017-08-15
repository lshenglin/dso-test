#! /usr/bin/env python

import os,sys

version = sys.hexversion
if version >= 0x020600F0 and version < 0x03000000 :
    py2 = True    # Python 2.6 or 2.7                                                                                                                                                                                                                             
    from Tkinter import *
    import ttk
elif version >= 0x03000000 and version < 0x03010000 :
    py30 = True
    from tkinter import *
    import ttk
elif version >= 0x03010000:
    py31 = True
    from tkinter import *
    import tkinter.ttk as ttk
else:
    print ("""                                                                                                                                                                                                                                                    
    You do not have a version of python supporting ttk widgets..                                                                                                                                                                                                  
    You need a version >= 2.6 to execute PAGE modules.                                                                                                                                                                                                            
    """)
    sys.exit()

class New_Toplevel_1:
    def __init__(self, master=None):
        # Set background of toplevel window to match
        # current style
        style = ttk.Style()
        theme = style.theme_use()
        default = style.lookup(theme, 'background')
        master.configure(background='orange')
        self.state = 'begin'

        self.label = Label(master)
        self.label.place(relx=0.01+0.315, rely=0.04+0.22, relheight=.50,relwidth=0.50)
        self.label.configure(activebackground="#f9f9f9")
        self.label.configure(activeforeground="black")
        self.label.configure(background="beige")
        self.label.configure(foreground="black")
        self.label.configure(highlightbackground="#d9d9d9")
        self.label.configure(highlightcolor="black")

        # Configure Text here.
        self.label.configure(text="Place my reading here...")
        self.label.configure(justify="center")


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global root
    root = Tk()
    root.title('R1  Demo')
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    #root.protocol('WM_DELETE_WINDOW', windowClose)
    root.lift()
    root.focus_set()
    root.attributes('-topmost', True) # Bring it always to front
    root.attributes('-topmost', False) # Allows user to access other windows
    #root.protocol('WM_TAKE_FOCUS', windowFocus)
    hMsg = msg = "R1 Demo"
    root.title(' %s' % hMsg)
    w = New_Toplevel_1 (root)
    w.state = 'begin'
    while w.state != 'exit':
        if w.state == 'begin' : w.state = 'exit'
        root.mainloop()
        #print w.state


vp_start_gui()
