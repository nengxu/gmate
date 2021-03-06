# -*- coding: utf-8 -*-
# Smart Indent Plugin
# Copyright © 2008 Alexandre da Silva
#
# This file is part of Gmate.
#
# See LICENTE.TXT for licence information

from gi.repository import Gedit, GObject, Gtk
import re
import os

#GLADE_FILE = os.path.join(os.path.dirname(__file__), "dialog.glade")

DEFAULT_TAB_SIZE = 8
DEFAULT_USE_SPACES = True

default_indent_config = {
    "c_indent_regex"                    : r'(?!^\s*(#|//)).*(\b(if|while|for)\s*\(.*\)|\b(else|do)\b)[^{;]*$',
    "c_unindent_regex"                  : r'^\s*((case\b.*|[\p{Alpha}_][\p{Alnum}_]*)\s*:(?!:)).*$',
    "c_unindent_keystrokes"             : ":",

    "objc_indent_regex"                 : r'\s*(((if|while)\s*\(|else\s*|else\s+if\s*\(|for\s*\(.*\))[^{;]*)',
    "objc_unindent_regex"               : r'^.*(default:\s*|case.*:.*)$',
    "objc_unindent_keystrokes"          : ":",

    "java_indent_regex"                 : r'\s*(((if|while)\s*\(|else\s*|else\s+if\s*\(|for\s*\(.*\))[^{;]*)',
    "java_unindent_regex"               : r'^.*(default:\s*|case.*:.*)$',
    "java_unindent_keystrokes"          : ":",

    "perl_indent_regex"                 : r'[^#]*\.\s*$',
    "perl_unindent_regex"               : '',
    "perl_unindent_keystrokes"          : '',

    "ruby_indent_regex"                 : r'[^#]*\s+\bdo\b(\s*|(\s+\|.+\|\s*))|\s*(\bif\b\s+.*|\belsif\b.*|\belse\b.*|\bdo\b(\s*|\s+.*)|\bcase\b\s+.*|\bwhen\b\s+.*|\bwhile\b\s+.*|\bfor\b\s+.*|\buntil\b\s+.*|\bloop\b\s+.*|\bdef\b\s+.*|\bclass\b\s+.*|\bmodule\b\s+.*|\bbegin\b.*|\bunless\b\s+.*|\brescue\b.*|\bensure\b.*)+',
    "ruby_unindent_regex"               : r'^\s*(else.*|end\s*|elsif.*|rescue.*|when.*|ensure.*)$',
    "ruby_unindent_keystrokes"          : 'edfn',
    "ruby_use_space"                    : True,
    "ruby_tab_size"                     : 2,

    "rubyonrails_indent_regex"          : r'[^#]*\s+\bdo\b(\s*|(\s+\|.+\|\s*))|\s*(\bif\b\s+.*|\belsif\b.*|\belse\b.*|\bdo\b(\s*|\s+.*)|\bcase\b\s+.*|\bwhen\b\s+.*|\bwhile\b\s+.*|\bfor\b\s+.*|\buntil\b\s+.*|\bloop\b\s+.*|\bdef\b\s+.*|\bclass\b\s+.*|\bmodule\b\s+.*|\bbegin\b.*|\bunless\b\s+.*|\brescue\b.*|\bensure\b.*)+',
    "rubyonrails_unindent_regex"        : r'^\s*(else.*|end\s*|elsif.*|rescue.*|when.*|ensure.*)$',
    "rubyonrails_unindent_keystrokes"   : 'edfn',
    "rubyonrails_use_space"             : True,
    "rubyonrails_tab_size"              : 2,

    "python_indent_regex"               : r'\s*[^#]{3,}:\s*(#.*)?',
    "python_unindent_regex"             : r'^\s*(else|elif\s.*|except(\s.*)?|finally)\s*:',
    "python_unindent_keystrokes"        : ':',
    "python_tab_size"                   : 4,

    "javascript_indent_regex"           : r'\s*(((if|while)\s*\(|else\s*|else\s+if\s*\(|for\s*\(.*\))[^{;]*)',
    "javascript_unindent_regex"         : r'^.*(default:\s*|case.*:.*)$',
    "javascript_unindent_keystrokes"    : ':',
    "javascript_use_space"              : True,
    "javascript_tab_size"               : 2,

    "rhtml_indent_regex"                : r'',
    "rhtml_unindent_regex"              : r'',
    "rhtml_unindent_keystrokes"         : '',
    "rhtml_use_space"                   : True,
    "rhtml_tab_size"                    : 2,

    "xml_indent_regex"                  : r'',
    "xml_unindent_regex"                : r'',
    "xml_unindent_keystrokes"           : '',
    "xml_use_space"                     : True,
    "xml_tab_size"                      : 2,

    "html_indent_regex"                 : r'',
    "html_unindent_regex"               : r'',
    "html_unindent_keystrokes"          : '',
    "html_use_space"                    : True,
    "html_tab_size"                     : 2,

    "php_indent_regex"                  : r'\s*(((if|while|else\s*(if)?|for(each)?|switch|declare)\s*\(.*\)[^{:;]*)|(do\s*[^\({:;]*))',
    "php_unindent_regex"                : r'^.*(default:\s*|case.*:.*)$',
    "php_unindent_keystrokes"           : ':',


    "sass_indent_regex"                 : r'(?!^\s*$)(?!^\s*(@|\+|\*|/\*|//))(^\s*?[^:=]+?(?<!,)$)',
    "sass_unindent_regex"               : r'', # XXX E.g., on blank line? (r'^\s*$')
    "sass_unindent_keystrokes"          : '',
    "sass_use_space"                    : True,
    "sass_tab_size"                     : 2
}

size_key_str       = "%s_tab_size"
space_key_str      = "%s_use_space"
indent_key_str     = "%s_indent_regex"
unindent_key_str   = "%s_unindent_regex"
keystrokes_key_str = "%s_unindent_keystrokes"

# Trailsave Plugin Config
crop_spaces_eol_key_str        = "%s_crop_spaces_eol"
insert_newline_eof_key_str     = "%s_insert_newline_eof"
remove_blank_lines_eol_key_str = "%s_remove_blank_lines_eol"

'''
import gtk.glade
import gconf


default_tab_size_key   = "/apps/gedit-2/preferences/editor/tabs/tabs_size"
default_use_spaces_key = "/apps/gedit-2/preferences/editor/tabs/insert_spaces"

gconf_base_uri = u"/apps/gedit-2/plugins/smart_indent"
config_client = gconf.client_get_default()
config_client.add_dir(gconf_base_uri, gconf.CLIENT_PRELOAD_NONE)

DEFAULT_USE_SPACES = config_client.get(default_use_spaces_key)
if DEFAULT_USE_SPACES:
    DEFAULT_USE_SPACES = DEFAULT_USE_SPACES.get_bool()
else:
    DEFAULT_USE_SPACES = True # if setting not set default is True
DEFAULT_TAB_SIZE   = config_client.get_int(default_tab_size_key) or 4




user_interface = """
<ui>
    <menubar name="MenuBar">
        <menu name="EditMenu" action="Edit">
            <placeholder name='EditOps_6'>
                <menuitem name="Smart Indent Configuration" action="SmartIndentConfiguration"/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""
'''

def get_config(key, lang, setting_type, default, other_storage=None):
    key = key % lang
#    value = config_client.get(os.path.join(gconf_base_uri, key))
    value = None
    if value is None:
        if other_storage:
            value = other_storage.get(key)
            if value is None:
                return default
        else:
            return default
    else:
        value = getattr(value, 'get_%s' % setting_type)()
    return value

def get_indent_config(key, lang, setting_type, default):
    return get_config(key, lang, setting_type, default, default_indent_config)


get_indent_regex = lambda lang: get_indent_config(indent_key_str, lang, 'string', '')
get_unindent_regex = lambda lang: get_indent_config(unindent_key_str, lang, 'string', '')
get_unindent_keystrokes = lambda lang: get_indent_config(keystrokes_key_str, lang, 'string', '')
get_use_spaces = lambda lang: get_indent_config(space_key_str, lang, 'bool', DEFAULT_USE_SPACES)
get_tab_size = lambda lang: get_indent_config(size_key_str, lang, 'int', DEFAULT_TAB_SIZE)

# TrailSave Plugin -------------------------------------------------------------

def get_trail_config(lang, key_str):
    return get_config(key_str, lang, 'bool', True)


def get_crop_spaces_eol(lang):
    return get_trail_config(lang, crop_spaces_eol_key_str)


def get_insert_newline_eof(lang):
    return get_trail_config(lang, insert_newline_eof_key_str)


def get_remove_blanklines_eof(lang):
    return get_trail_config(lang, remove_blank_lines_eol_key_str)

# ------------------------------------------------------------------------------

class SmartIndentPluginView(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "SmartIndentPluginViewActivatable"
    view = GObject.property(type=Gedit.View)
    handler_id = None
    lang = 'plain_text'

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.setup_smart_indent()

    def do_deactivate(self):
        self.view.disconnect(self.handler_id)
        self.view.get_buffer().disconnect(self.doc_handler_id)

    def do_update_state(self):
        self.setup_smart_ident()
        self.window.get_ui_manager().ensure_update()

    def setup_smart_indent(self):
        document = self.view.get_buffer()
        if document.get_language() is not None:
            self.lang = document.get_language().get_id()
        if getattr(self.view, 'smart_indent_instance', False) == False:
            setattr(self.view, 'smart_indent_instance', SmartIndent())
        self.register_keypress()
        self.on_document_load()

    def on_document_load(self):
        self.doc_handler_id = self.view.get_buffer().connect('loaded', self.set_language_on_load)

    def register_keypress(self):
        self.handler_id = self.view.connect('key-press-event', self.view.smart_indent_instance.key_press_handler)

    def set_language_on_load(self, doc, *args):
        lang = doc.get_language()
        if lang is not None:
            self.lang = lang.get_id()
        self.view.smart_indent_instance.set_language(self.lang, self.view)

class ConfigurationWindowHelper:

    def __init__(self, plugin, window):
        self.window = window
        self.plugin = plugin
        self.dialog = None

    def configuration_dialog(self):
        glade_xml = Gtk.Blade.add_from_file(GLADE_FILE)
        if self.dialog:
            self.dialog.set_focus(True)
            return

        self.dialog = glade_xml.get_widget('config_dialog')
        self.dialog.connect('delete_event', self.on_close)
        self.dialog.show_all()
        self.dialog.set_transient_for(self.window)

        self.btn_cancel = glade_xml.get_widget('btn_cancel')
        self.btn_cancel.connect('clicked', self.on_cancel)

        self.btn_apply = glade_xml.get_widget('btn_apply')
        self.btn_apply.connect('clicked', self.on_apply)

        # Get data from current document, not from configuration, because user
        # may want to save current options
        view = self.window.get_active_view()
        space   = view.get_insert_spaces_instead_of_tabs()
        size    = view.get_tab_width()

        self.language = view.get_buffer().get_language()

        if self.language:
            lang_name = self.language.get_name()
            self.lang_id = self.language.get_id()
        else:
            lang_name = _(u'Plain Text')
            self.lang_id = 'plain_text'

        self.lbl_language = glade_xml.get_widget('lbl_language')
        self.lbl_language.set_markup("Language: <b>%s</b>" % lang_name)

        self.edt_size = glade_xml.get_widget('edt_size')
        self.edt_size.set_value(size)

        self.cbx_use_spaces = glade_xml.get_widget('cbx_use_spaces')
        self.cbx_use_spaces.set_active(space)

        self.edt_indent_regex = glade_xml.get_widget('edt_indent_regex')
        self.edt_indent_regex.set_text(get_indent_regex(self.lang_id) or '')

        self.edt_unindent_regex = glade_xml.get_widget('edt_unindent_regex')
        self.edt_unindent_regex.set_text(get_unindent_regex(self.lang_id) or '')

        self.edt_unindent_keystrokes = glade_xml.get_widget('edt_unindent_keystrokes')
        self.edt_unindent_keystrokes.set_text(get_unindent_keystrokes(self.lang_id) or '')

        # TrailsSave Options
        crop_spaces = get_crop_spaces_eol(self.lang_id)
        insert_newline = get_insert_newline_eof(self.lang_id)
        remove_blanklines = get_remove_blanklines_eof(self.lang_id)

        self.cbx_crop_spaces_on_eol = glade_xml.get_widget('cbx_crop_spaces_on_eol')
        self.cbx_crop_spaces_on_eol.set_active(crop_spaces)

        self.cbx_insert_newline_at_eof = glade_xml.get_widget('cbx_insert_newline_at_eof')
        self.cbx_insert_newline_at_eof.set_active(insert_newline)

        self.cbx_remove_blank_lines_at_eof = glade_xml.get_widget('cbx_remove_blank_lines_at_eof')
        self.cbx_remove_blank_lines_at_eof.set_active(remove_blanklines)


    def close_dialog(self):
        self.dialog.destroy()
        self.dialog = None
        self.size_picker = None
        self.use_spaces_check = None


    def on_close(self, *args):
        self.close_dialog()


    def on_cancel(self, *args):
        self.close_dialog()


    def deactivate(self):
        self.window = None
        self.plugin = None


    def on_apply(self, *args):
        view = self.window.get_active_view()

        buf = view.get_buffer()

        size = self.edt_size.get_value_as_int()
        use_spaces = self.cbx_use_spaces.get_active()
        indent_regex = self.edt_indent_regex.get_text()
        unindent_regex = self.edt_unindent_regex.get_text()
        unindent_keystrokes = self.edt_unindent_keystrokes.get_text()

        #TrailSave Plugin
        crop_spaces = self.cbx_crop_spaces_on_eol.get_active()
        insert_newline = self.cbx_insert_newline_at_eof.get_active()
        remove_blanklines = self.cbx_remove_blank_lines_at_eof.get_active()

        size_key = size_key_str % self.lang_id
        space_key = space_key_str % self.lang_id
        indent_key = indent_key_str % self.lang_id
        unindent_key = unindent_key_str % self.lang_id
        keystrokes_key = keystrokes_key_str % self.lang_id

        # TrailSave Plugin
        crop_spaces_key = crop_spaces_eol_key_str % self.lang_id
        insert_newline_key = insert_newline_eof_key_str % self.lang_id
        remove_blanklines_key = remove_blank_lines_eol_key_str % self.lang_id

        config_client.set_int(os.path.join(gconf_base_uri,size_key), size)
        config_client.set_bool(os.path.join(gconf_base_uri,space_key), use_spaces)
        config_client.set_string(os.path.join(gconf_base_uri,indent_key), indent_regex)
        config_client.set_string(os.path.join(gconf_base_uri,unindent_key), unindent_regex)
        config_client.set_string(os.path.join(gconf_base_uri,keystrokes_key), unindent_keystrokes)

        # TrailSave Plugin
        config_client.set_bool(os.path.join(gconf_base_uri, crop_spaces_key), crop_spaces)
        config_client.set_bool(os.path.join(gconf_base_uri, insert_newline_key), insert_newline)
        config_client.set_bool(os.path.join(gconf_base_uri, remove_blanklines_key), remove_blanklines)

        view.set_insert_spaces_instead_of_tabs(use_spaces)
        view.set_tab_width(size)
        self.plugin.set_status(view)

        if getattr(view, 'smart_indent_instance', False):
            view.smart_indent_instance.set_language(self.lang_id, view)

        self.close_dialog()


class SmartIndent:

    def __init__(self):
        self.__not_available = True
        self.__line_unindented = -1
        self.__line_no = -1
        self.clear_variables()
        return

    def clear_variables(self):
        self.re_indent_next      = None
        self.re_unindent_curr    = None
        self.unindent_keystrokes = None


    def set_indent_config(self, lang):
        self.clear_variables()
        r_indent = get_indent_regex(lang)
        r_unindent = get_unindent_regex(lang)
        u_keystrokes = get_unindent_keystrokes(lang)
        if r_indent:
            self.re_indent_next = re.compile(r_indent)
        if r_unindent:
            self.re_unindent_curr = re.compile(r_unindent)
        if u_keystrokes:
            self.unindent_keystrokes = u_keystrokes
        # Return configured if some of the options is present
        if r_indent or r_unindent or u_keystrokes:
            return True
        else:
            return False


    def set_language(self, lang, view):
        self.__not_available = not self.set_indent_config(lang)
        tab_size    = get_tab_size(lang)
        use_spaces  = get_use_spaces(lang)
        # Set the buffer tab configuration
        view.set_tab_width(tab_size)
        view.set_insert_spaces_instead_of_tabs(use_spaces)


    def __update_line_no(self, buf):
        cursor_iter = buf.get_iter_at_mark(buf.get_insert())
        self.__line_no = cursor_iter.get_line()
        if self.__line_no != self.__line_unindented:
            self.__line_unindented = -1


    def __get_current_line(self, view, buf):
        cursor_iter = buf.get_iter_at_mark(buf.get_insert())
        line_start_iter = cursor_iter.copy()
        view.backward_display_line_start(line_start_iter)
        return buf.get_text(line_start_iter, cursor_iter, True)


    def key_press_handler(self, view, event):
        buf = view.get_buffer()
        if self.__not_available or buf.get_has_selection(): return
        # Get tabs/indent configuration
        if view.get_insert_spaces_instead_of_tabs():
          indent_width = ' ' * view.get_tab_width()
        else:
          indent_width = '\t'
        keyval = event.keyval
        self.__update_line_no(buf)
        if keyval == 65293:
            # Check next line indentation for current line
            line = self.__get_current_line(view, buf)
            if self.re_indent_next and self.re_indent_next.match(line):
                old_indent = line[:len(line) - len(line.lstrip())]
                indent = '\n'+ old_indent + indent_width
                buf.insert_interactive_at_cursor(indent, -1, True)
                return True
        elif keyval == 65288:
            line = self.__get_current_line(view, buf)
            if line.strip() == '' and line != '':
                length = len(indent_width)
                nb_to_delete = len(line) % length or length
                cursor_position = buf.get_property('cursor-position')
                iter_cursor = buf.get_iter_at_offset(cursor_position)
                iter_before = buf.get_iter_at_offset(cursor_position - nb_to_delete)
                buf.delete_interactive(iter_before, iter_cursor, True)
                return True
        elif self.unindent_keystrokes:
            if keyval in [ord(k) for k in self.unindent_keystrokes]:
                line = self.__get_current_line(view, buf)
                if self.__line_unindented != self.__line_no:
                    line_eval = line+chr(event.keyval)
                    if self.re_unindent_curr and self.re_unindent_curr.match(line_eval):
                        cursor_iter = buf.get_iter_at_mark(buf.get_insert())
                        line_start_iter = cursor_iter.copy()
                        view.backward_display_line_start(line_start_iter)
                        iter_end_del = buf.get_iter_at_offset(line_start_iter.get_offset() + len(indent_width))
                        text = buf.get_text(line_start_iter, iter_end_del, True)
                        if text.strip() == '':
                            buf.delete_interactive(line_start_iter, iter_end_del, True)
                            self.__line_unindented = self.__line_no
                            return False
        return False

