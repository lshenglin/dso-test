# -*- coding: utf-8 -*-
# Created on 9/15/16
# By rtaglieri

import prompt_toolkit as pt
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import containers, controls, dimension
from prompt_toolkit.token import Token
from prompt_toolkit.contrib import completers
import re
import cPickle
import os


manager = pt.key_binding.manager.KeyBindingManager()
registry = manager.registry


def fix_path(path):
    return os.path.abspath(os.path.normcase(os.path.expanduser(path)))


def eng_fmt(basefmt=".1f", unit="Hz"):
    fmt = u"{{base:{basefmt}}} {{prefix}}{unit}".format(basefmt=basefmt,unit=unit)
    def formatting_function(x):
        prefixes = ["a","f","p","n","µ","m","","k","M","G","P","E"]
        index = 6
        negative = x < 0
        x = abs(x)
        while x > 0  and x < 1 and index > 0:
            x *= 1000
            index -= 1
        while x >= 1000 and index < len(prefixes)-1:
            x /= 1000.
            index += 1
        if negative: x *= -1
        return fmt.format(base=x,prefix=prefixes[index])
    return formatting_function


class CommandCompleter(pt.completion.Completer):
    def __init__(self, valid_command_dict):
        self.valid_commands = valid_command_dict
        pt.completion.Completer.__init__(self)
        self.path_completer = completers.PathCompleter()
    def get_completions(self, document, complete_event):
        if complete_event.completion_requested:
            for cmd in self.valid_commands.keys():
                if document.text.upper() == cmd[:len(document.text)]:
                    yield pt.completion.Completion(cmd+' ', start_position=-1*len(document.text))
            m = re.match("^SAVELOC (.+)",document.text)
            if m:
                path = fix_path(m.group(1))
                for completion in self.path_completer.get_completions(pt.document.Document(path), complete_event):
                    yield completion


class State(object):
    def __init__(self, parent):
        self.parent = parent
        self._ranges = {}
        self._types = {}
        self._fmts = {}
        self._tkns = {}

    def add_property(self, name, value, acceptable_range, fmt, tkn=Token.Property):
        name = name.lower()
        self._ranges[name] = acceptable_range
        self._types[name] = type(value)
        self._fmts[name] = fmt
        self._tkns[name] = tkn
        setattr(self, name, value)
        print "added %s"%name

    def get_property_token(self, name):
        fmt = self._fmts[name]
        if type(fmt) == unicode:
            fmt = fmt.format
        if type(fmt) == tuple:
            fmt = eng_fmt(*fmt)
        return [(self._tkns[name], fmt(getattr(self, name)))]

    def get_property_dictionary(self):
        d = {}
        for name in self._tkns.keys():
            d[name] = self.__getattribute__(name)
        return d

    def save_state(self, fn, statename = ''):
        state = statename, self._ranges, self._fmts, self._tkns, self._types, self.get_property_dictionary()
        with open(fn, 'wb') as outfile:
            cPickle.dump(state, outfile, -1)

    def load_state(self, fn):
        with open(fn, 'rb') as infile:
            statename, self._ranges, self._fmts, self._tkns, self._types, d = cPickle.load(infile)
        for k, v in d.items():
            setattr(self, k, v)
        return statename

    def read_statenames(self, path):
        statemap = {}
        for fn in os.listdir(path):
            with open(os.path.join(path,fn), 'rb') as infile:
                statemap[int(fn)] = cPickle.load(infile)[0]
        return statemap

    def __setattr__(self, key, value):
        if hasattr(self, '_types'):
            if key in self._types:
                value = self._types[key](value)
                acceptable_range = self._ranges.get(key)
                if type(acceptable_range) == tuple:
                    minv, maxv = acceptable_range
                    if value < minv or value > maxv:
                        self.parent.help_text = u"Value %r out of acceptable range: %r ≤ x ≤ %r"%(value, minv, maxv)
                        return
                elif type(acceptable_range) == list:
                    if value not in acceptable_range:
                        self.parent.help_text = u"Value %r out of acceptable range: %r"%(value, acceptable_range)
                        return
                elif type(acceptable_range) == type(lambda : None):
                    if not acceptable_range(value):
                        self.parent.help_text = u"%r is not a valid value for %r"%(value, key)
                        return
                else:
                    pass
        return object.__setattr__(self, key, value)


class TUI:
    style = pt.styles.style_from_dict({
        Token.Line: '#ansidarkgray',
        Token.Title: 'bold underline',
        Token.Status: '#ansiwhite bg:#ansiblack',
        Token.Prompt: '#ansigreen bold',
        Token.Property: '#ansiblue'
        })
    HELP_DEFAULT = u"^C/^Q: Quit    ^S: Save Settings    ^L: Load Settings    ^R: Run Test"

    def __init__(self):
        self.key_manager = pt.key_binding.manager.KeyBindingManager()
        self.key_registry = self.key_manager.registry
        self.history = pt.history.InMemoryHistory()
        self.valid_commands = {}
        self.help_text = self.HELP_DEFAULT
        self.p = State(self)
        self.p.add_property('angle_single',     0,          (0,359),                u"{:>3d}°")
        self.p.add_property('angle_start',      0,          (0,359),                u"{:>3d}°")
        self.p.add_property('angle_stop',       359,        (0,359),                u"{:>3d}°")
        self.p.add_property('angle_step',       10,         (0,359),                u"{:>3d}°")
        self.p.add_property('angle_mode',       'SWEEP',    ['SWEEP', 'SINGLE'],    u"{}")
        self.p.add_property('txpower',          0,          (-50,10),               u"{:>2d} dBm")
        self.p.add_property('freq_start',       3e9,        (2e9,10e9),             (".3f","Hz"))
        self.p.add_property('freq_stop',        6e9,        (2e9,10e9),             (".3f","Hz"))
        self.p.add_property('freq_step',        10e6,       (100e3,1e9),            (".1f","Hz"))
        self.p.add_property('test_mode',        'VNA',      ['VNA'],                u"{}")
        self.p.add_property('save_location',    'results',  lambda x : True,          u"{}")
        print self.p.get_property_dictionary()
        self.STATE = 'MAIN'

    #-- State filters
    @staticmethod
    @pt.filters.Condition
    def is_selecting_save_load_slot(cli):
        return cli.state in ['SELECTING_SAVE_SLOT', 'SELECTING_LOAD_SLOT']

    @staticmethod
    @pt.filters.Condition
    def is_loading(cli):
        return cli.state == 'SELECTING_LOAD_SLOT'

    @staticmethod
    @pt.filters.Condition
    def is_saving(cli):
        return cli.state in ['SELECTING_SAVE_SLOT', 'ENTERING_SAVE_NAME']

    @staticmethod
    @pt.filters.Condition
    def is_mainscreen(cli):
        return cli.state == 'MAIN'

    #-- Key bindings
    def init_key_bindings(self):
        @registry.add_binding(Keys.ControlQ, eager=True)
        @registry.add_binding(Keys.ControlC, eager=True)
        def exit_(event):
            event.cli.set_return_value(None)

        @registry.add_binding(Keys.Escape, eager=True, filter= ~self.is_mainscreen)
        def escape(event):
            event.cli.state = "MAIN"
            event.cli.application.layout = self.main_layout
            event.cli.focus(u"PROMPT")
            self.help_text = self.HELP_DEFAULT

        @registry.add_binding(Keys.ControlS, eager=True, filter= self.is_mainscreen)
        def save_state(event):
            event.cli.application.layout = self.save_load_layout
            self.help_text = "0-9: Select Save Slot   Esc: Back to main screen"
            event.cli.state = 'SELECTING_SAVE_SLOT'

        @registry.add_binding(Keys.ControlL, eager=True, filter= self.is_mainscreen)
        def load_state(event):
            event.cli.application.layout = self.save_load_layout
            self.help_text = "0-9: Select Load Slot   Esc: Back to main screen"
            event.cli.state = 'SELECTING_LOAD_SLOT'

        @registry.add_binding(Keys.ControlR, eager=True, filter= self.is_mainscreen)
        def run_test(event):
            property_dict = self.p.get_property_dictionary()
            if self.p.test_mode == "VNA":
                import wrapper_vna
                wrapper_vna.vna(property_dict)

        def build_selectSaveLoadBuffer_func(x):
            @registry.add_binding(unicode(x), eager=True, filter= self.is_selecting_save_load_slot)
            def selectSaveLoadBuffer(event):
                if self.is_loading(event.cli):
                    fn = '.ui4_saved_states/%d'%x
                    if os.path.isfile(fn):
                        self.p.load_state(fn)
                        event.cli.state = 'MAIN'
                        event.cli.application.layout = self.main_layout
                        self.help_text = self.HELP_DEFAULT
                if self.is_saving(event.cli):
                    event.cli.focus(u'FN%d'%x)
                    event.cli.state = 'ENTERING_SAVE_NAME'
                    self.help_text = "Enter a name for the saved state.   Esc: Cancel and return to main screen"

        for i in range(10):
            build_selectSaveLoadBuffer_func(i)


    #-- Input prompt definitions
    def define_command(self, name, function, help_string):
        self.valid_commands[name] = (function, help_string)

    def handle_command(self, cli, buffer):
        global HELP_TEXT
        self.help_text = self.HELP_DEFAULT
        cmd = buffer.document.text.upper().split()
        if cmd:
            try:
                f, _ = self.valid_commands[cmd[0]]
                f(self, *cmd[1:])
                buffer.append_to_history()
            except KeyError:
                pass
        buffer.reset()

    def handle_help_bar(self, buffer):
        cmd = buffer.document.text.upper().split()
        try:
            _, h = self.valid_commands[cmd[0]]
            self.help_text = h
        except (KeyError, IndexError):
            self.help_text = self.HELP_DEFAULT

    def save_state(self, cli, buffer):
        filenumber = cli.current_buffer_name[-1]
        statename = buffer.document.text
        self.p.save_state('.ui4_saved_states/%s'%filenumber,statename)
        cli.state = "MAIN"
        cli.application.layout = self.main_layout
        cli.focus(u"PROMPT")
        self.help_text = self.HELP_DEFAULT

    #-- Window definitions
    @staticmethod
    def tick_if_true(val):
        if val: return 'X'
        else:   return ' '

    @staticmethod
    def text_block(source, **kwargs):
        return containers.Window(content=controls.TokenListControl(get_tokens=source),
                                 dont_extend_height=True, **kwargs)

    def tokenize(self, s, force_token=None):
        tokens = []
        for segment in re.split("(\$\w+)",s):
            if segment:
                if segment[0] == "$":
                    tokens += self.p.get_property_token(segment[1:].lower())
                else:
                    tokens += [(Token, segment)]
        if force_token:
            for i in range(len(tokens)):
                tokens[i] = (force_token, tokens[i][1])
        return tokens


    def turn_table_settings(self, cli):
        title = [(Token.Title, u"Turn Table Settings:\n")]
        s = u"""
[{sweep_mode}] Start = $ANGLE_START    Stop = $ANGLE_STOP    Step = $ANGLE_STEP
[{single_mode}] Single Angle = $ANGLE_SINGLE""".format(sweep_mode=self.tick_if_true(self.p.angle_mode == 'SWEEP'),
                                                       single_mode=self.tick_if_true(self.p.angle_mode == 'SINGLE'))
        return title+self.tokenize(s)
        # return [(Token.Title, title), (Token, s)]

    def test_mode(self, cli):
        s = u"Test Mode = $TEST_MODE"
        return self.tokenize(s, force_token=Token.Title)

    def test_settings(self, cli):
        if self.p.test_mode == 'VNA':
            npoints = int((self.p.freq_stop-self.p.freq_start)/self.p.freq_step) + 1
            s=u"""
Start Freq: $FREQ_START       Stop Freq: $FREQ_STOP
Freq Step Size: $FREQ_STEP    Num of Points: {npoints}
Transmit Power: $TXPOWER""".format(npoints=npoints)
        else:
            s = u""
        return self.tokenize(s)

    def save_location_setting(self, cli):
        path = fix_path(self.p.save_location)
        s = u"Save Location: {}".format(path)
        return self.tokenize(s)

    def status_bar(self, cli):
        return [(Token.Status, self.help_text)]

    def file_selection(self, filenum):
        sublayout = containers.VSplit([
            self.text_block(lambda x : [(Token, u" {:>2d}:".format(filenum))], dont_extend_width=True),
            containers.Window(content=controls.BufferControl(buffer_name='FN%d'%filenum), dont_extend_height=True)
        ])
        return sublayout

    def update_state_name_display(self):
        statenames = self.p.read_statenames('.ui4_saved_states')
        for i in range(10):
            # self.buffers['FN%d'%i].document.text = statenames.get(i,u'')
            self.buffers['FN%d'%i].document = pt.document.Document(statenames.get(i,u''))

    #-- Layout definition
    def create(self):
        self.buffer = pt.buffer.Buffer(accept_action=pt.buffer.AcceptAction(handler=self.handle_command),
                                       history=self.history,
                                       completer=CommandCompleter(self.valid_commands),
                                       on_cursor_position_changed=self.handle_help_bar,
                                       )
        self.buffers = {'PROMPT':self.buffer}
        for i in range(10):
            self.buffers['FN%d'%i] = pt.buffer.Buffer(accept_action=pt.buffer.AcceptAction(handler=self.save_state),
                                                        history=None, completer=None)

        divider_line = lambda : containers.Window(content=controls.FillControl('-', token=Token.Line),
                                                  height=dimension.LayoutDimension.exact(1) )

        buffer_sublayout = containers.VSplit([
            # containers.Window(content=controls.TokenListControl(get_tokens=lambda cli : ([Token.Red, u'> ']))),
            self.text_block(lambda x : [(Token.Prompt, u">> ")], dont_extend_width=True),
            containers.Window(content=controls.BufferControl(buffer_name='PROMPT'), dont_extend_height=True),

        ])

        self.main_layout = containers.HSplit([
            divider_line(),
            self.text_block(self.test_mode),
            self.text_block(self.test_settings),
            divider_line(),
            self.text_block(self.turn_table_settings),
            divider_line(),
            self.text_block(self.save_location_setting),
            divider_line(),
            buffer_sublayout,
            containers.Window(content=controls.TokenListControl(get_tokens=self.status_bar)),
        ])

        self.save_load_layout = containers.HSplit(
            [divider_line()]+
            [self.file_selection(i) for i in range(10)]+
            [divider_line(),
             containers.Window(content=controls.TokenListControl(get_tokens=self.status_bar)),
        ])
        self.update_state_name_display()

        loop = pt.shortcuts.create_eventloop()
        application = pt.application.Application(layout=self.main_layout,
                                                 buffers=self.buffers,
                                                 style=self.style,
                                                 initial_focussed_buffer='PROMPT',
                                                 key_bindings_registry=registry)
        cli = pt.interface.CommandLineInterface(application=application, eventloop=loop)
        cli.state = "MAIN"
        self.init_key_bindings()
        cli.run()


#-- Define user commands
def set_angle(p, *args):
    if len(args) == 0:
        if tui.p.angle_mode == 'SINGLE': tui.p.angle_mode = 'SWEEP'
        else: tui.p.angle_mode = 'SINGLE'
    elif len(args) == 1:
        tui.p.angle_mode = "SINGLE"
        tui.p.angle_single = args[0]
    elif len(args) == 3:
        tui.p.angle_mode = "SWEEP"
        tui.p.angle_start = args[0]
        tui.p.angle_stop = args[1]
        tui.p.angle_step = args[2]

def set_txpower(tui, *args):
    if len(args) == 1:
        tui.p.txpower = args[0]

def set_freqs(tui, *args):
    if len(args) == 2:
        tui.p.freq_start = float(args[0])*1e9
        tui.p.freq_stop = float(args[1])*1e9
    if len(args) == 3:
        tui.p.freq_start = float(args[0])*1e9
        tui.p.freq_stop = float(args[1])*1e9
        tui.p.freq_step = float(args[2])*1e6

def set_save_loc(tui, *args):
    if len(args) == 1:
        tui.p.save_location = fix_path(args[0].lower())


tui = TUI()
try: os.mkdir('.ui4_saved_states')
except OSError: pass
if os.path.isfile('.ui4_last_state'):
    tui.p.load_state('.ui4_last_state')
tui.define_command('ANGLE', set_angle, "ANGLE : Toggle sweep/single   ANGLE x : Set single   Angle x y z: Sweep x to y by z")
tui.define_command('TXPOWER', set_txpower, "TXPOWER x : Set VNA TX to x dBm")
tui.define_command('FREQ', set_freqs, "FREQ x y : Sweep from x GHz to y GHz   FREQ x y z : Sweep from x GHz to y GHz by z MHz")
tui.define_command('SAVELOC', set_save_loc, "SAVELOC x : Save results in folder x")
tui.create()
print('Exiting')
tui.p.save_state('.ui4_last_state')
print tui.p.get_property_dictionary()