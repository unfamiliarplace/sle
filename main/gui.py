# Python 2.7.3
import wx, os, sys
from library import *

DIR = 'SLE_arguments/'

ABOUT_MESSAGE = '''The Symbolic Logic Evaluator (SLE)
allows you to input premises and conclusions
in modern symbolic logic and analyze the argument.
You can also save and open arguments across sessions.

v 1.00, 16/02/2013
Created by Luke Sawczak, 2013
site: unfamiliarplace/sle.html
email: luke@unfamiliarplace.com'''

HELP_MESSAGE = '''Just input premises and a conclusion
in the fields labelled as such, and the result field
will update with the analysis of the argument.
Currently, only sentential logic is supported.

Enter everything in symbolic logic. Here are the options:
## Negation:  ~  -  ~
## Conjunction:  ^  &  +
## Disjunction:  v  /
## Conditional:  >
## Biconditional:  =
## Brackets:  ( )
## Propositions: P - Z

As you type, the result and info will update:
## None (nothing to evaluate)
## Error + what type and where
## Valid + whether it's circular or the premises contradict themselves
## Invalid + a counterexample of truth value assignments

You can also save and open arguments from the File menu.
(Note that you will not be prompted to save your argument
every time you quit or open a new argument.)'''


class Mainframe(wx.Frame):
    
    def __init__(self, parent, title):
        
        #-------------------------------------------
        # Initialize
        #-------------------------------------------
        
        # Create no-resize style; initialize a frame and panel
        
        no_resize = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent, title = title, size = (420, 400), style = no_resize)
        panel = wx.Panel(self, -1)
        
        # Status bar
        
        self.statusbar = self.CreateStatusBar()
        
        # Core variables
        
        self.premises = ''
        self.conclusion = ''
        self.dir = DIR
        self.filename = ''
        
        #-------------------------------------------
        # Menu bar
        #-------------------------------------------        
        
        # File menu
        
        file_menu = wx.Menu()
        
        # File menu buttons and separators
        
        new_button = file_menu.Append(wx.ID_NEW, "&New argument", "Start a new argument")        
        open_button = file_menu.Append(wx.ID_OPEN, "&Open argument", "Open a saved argument file")
        save_button = file_menu.Append(wx.ID_SAVE, "&Save argument", "Save argument")
        saveas_button = file_menu.Append(wx.ID_SAVEAS, "Sa&ve argument as", "Save argument as")
        
        file_menu.AppendSeparator()
        
        about_button = file_menu.Append(wx.ID_ABOUT, "&About SLE", "Information about SLE")
        help_button = file_menu.Append(wx.ID_HELP, '&Help', 'How to use SLE')
        
        file_menu.AppendSeparator()
        
        exit_button = file_menu.Append(wx.ID_EXIT, "E&xit", "Quit SLE")
        
        # Menu bar
        
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)
        
        #-------------------------------------------
        # Labels and fields
        #-------------------------------------------
        
        # Initialize labels
        
        self.label_premises = wx.StaticText(panel, label = 'Premises', style = wx.RAISED_BORDER)
        self.label_conclusion = wx.StaticText(panel, label = 'Conclusion', style = wx.RAISED_BORDER)
        self.label_result = wx.StaticText(panel, label = 'Result', style = wx.RAISED_BORDER)
        self.label_info = wx.StaticText(panel, label = 'Info', style = wx.RAISED_BORDER)

        # Initialize fields
        
        self.field_premises = wx.TextCtrl(panel, style = wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_NO_VSCROLL)
        self.field_conclusion = wx.TextCtrl(panel)
        self.field_result = wx.TextCtrl(panel, style = wx.TE_READONLY | wx.TE_NO_VSCROLL)
        self.field_info = wx.TextCtrl(panel, style = wx. TE_MULTILINE | wx.TE_READONLY | wx.TE_NO_VSCROLL)
        
        self.field_result.ChangeValue('None')
        self.field_info.ChangeValue('no argument')
        
        #-------------------------------------------
        # Sizers
        #-------------------------------------------
        
        # Left sizer
        
        self.sizer_vert_left = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_vert_left.Add(self.label_premises, 5, wx.EXPAND)
        self.sizer_vert_left.Add(self.field_premises, 48, wx.EXPAND)
        self.sizer_vert_left.Add((1,1), 4, wx.EXPAND)
        self.sizer_vert_left.Add(self.label_conclusion, 5, wx.EXPAND)
        self.sizer_vert_left.Add(self.field_conclusion, 4, wx.EXPAND)
        self.sizer_vert_left.Add((1,1), 1, wx.EXPAND)
        
        # Right sizer
        
        self.sizer_vert_right = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_vert_right.Add(self.label_result, 5, wx.EXPAND)
        self.sizer_vert_right.Add(self.field_result, 4, wx.EXPAND)
        self.sizer_vert_right.Add((1,1), 4, wx.EXPAND)
        self.sizer_vert_right.Add(self.label_info, 5, wx.EXPAND)
        self.sizer_vert_right.Add(self.field_info, 48, wx.EXPAND) 
        self.sizer_vert_right.Add((1,1), 1, wx.EXPAND)
        
        # Main sizer
        
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizer_main.Add((1,1), 1, wx.EXPAND)
        self.sizer_main.Add(self.sizer_vert_left, 65, wx.EXPAND)
        self.sizer_main.Add((1,1), 5, wx.EXPAND)
        self.sizer_main.Add(self.sizer_vert_right, 45, wx.EXPAND)
        self.sizer_main.Add((1,1), 1, wx.EXPAND)
        
        #-------------------------------------------
        # Bindings
        #-------------------------------------------
        
        # Menu buttons
        
        self.Bind(wx.EVT_MENU, self.on_new, new_button)
        self.Bind(wx.EVT_MENU, self.on_open, open_button)
        self.Bind(wx.EVT_MENU, self.on_save, save_button)
        self.Bind(wx.EVT_MENU, self.on_saveas, saveas_button)
        self.Bind(wx.EVT_MENU, self.on_about, about_button)
        self.Bind(wx.EVT_MENU, self.on_help, help_button)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_button)
        
        # Premises or conclusion field updates
        
        self.field_premises.Bind(wx.EVT_TEXT, self.evaluate)
        self.field_conclusion.Bind(wx.EVT_TEXT, self.evaluate)
        
        #-------------------------------------------
        # Accelerators
        #-------------------------------------------
        
        # Ctrl + S = save
        
        self.ctrl_s_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_save, id=self.ctrl_s_id)
        ctrl_s_combo = (wx.ACCEL_CTRL, ord('S'), self.ctrl_s_id)
        
        # Sum up combos and initialize table
        
        combos = [ctrl_s_combo]
        self.accelerator_table = wx.AcceleratorTable(combos)
        self.SetAcceleratorTable(self.accelerator_table)
        
        #-------------------------------------------
        # Show
        #-------------------------------------------
        
        self.SetSizer(self.sizer_main)
        self.SetAutoLayout(True)
        self.Show(True)
        
    
    #-------------------------------------------
    # Event handlers
    #-------------------------------------------
    
    # Update result field
    
    def evaluate(self, event):
        
        self.premises = self.field_premises.GetValue().strip()
        self.conclusion = self.field_conclusion.GetValue().strip()
        
        result, info = get_result_text(self.premises, self.conclusion)
        self.field_result.ChangeValue(result)
        self.field_info.ChangeValue(info)
        
    # Menu buttons
        
    def on_about(self, event):
        
        message = wx.MessageDialog(self, ABOUT_MESSAGE, "About SLE", wx.OK)
        message.ShowModal()
        message.Destroy()
        
    def on_help(self, event):
        
        message = wx.MessageDialog(self, HELP_MESSAGE, "SLE help", wx.OK)
        message.ShowModal()
        message.Destroy()
        
    def on_exit(self, event):
        
        self.Close(True)
        
    def on_new(self, event):
        
        self.premises = ''
        self.conclusion = ''
        self.field_premises.ChangeValue(self.premises)
        self.field_conclusion.ChangeValue(self.conclusion)
        self.evaluate(None)
        self.filename = ''
        self.dir = DIR
        self.statusbar.SetStatusText('Cleared fields')
        
    def on_open(self, event):
        
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)        
        
        dialogue = wx.FileDialog(self, "Choose an argument file", self.dir, '', '*.sle', wx.OPEN)
        
        if dialogue.ShowModal() == wx.ID_OK:
            self.filename = dialogue.GetFilename()
            self.dir = dialogue.GetDirectory()
            
            file = open(os.path.join(self.dir, self.filename), 'r')
            lines = file.readlines()
            self.premises = ''.join(lines[:-2]).strip()
            self.conclusion = lines[-1].strip()
            file.close()
            
            self.field_premises.ChangeValue(self.premises)
            self.field_conclusion.ChangeValue(self.conclusion)
            self.evaluate(None)
            
            self.statusbar.SetStatusText('Opened argument: {}'.format(self.filename))
            
        dialogue.Destroy()
        
    def on_save(self, event):
        
        if self.filename:
            
            file = open(os.path.join(self.dir, self.filename), 'w')
            file.write('{}\n'.format(self.premises))
            file.write('\n{}'.format(self.conclusion))
            file.close()
            
            self.statusbar.SetStatusText('Saved argument: {}'.format(self.filename))
            
        else:
            self.on_saveas(event)
            
    def on_saveas(self, event):
        
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
                
        dialogue = wx.FileDialog(self, "Choose a filename", self.dir, '', '*.sle', wx.SAVE)
        
        if dialogue.ShowModal() == wx.ID_OK:
            self.filename = dialogue.GetFilename()
            self.dir = dialogue.GetDirectory()
            
            file = open(os.path.join(self.dir, self.filename), 'w')
            file.write('{}\n'.format(self.premises))
            file.write('\n{}'.format(self.conclusion))            
            file.close()
            
            self.statusbar.SetStatusText('Saved argument as: {}'.format(self.filename))
            
        dialogue.Destroy()


#-------------------------------------------
# Running the actual program
#-------------------------------------------

SLE = wx.App(False)
frame = Mainframe(None, 'Symbolic Logic Evaluator')
SLE.MainLoop()