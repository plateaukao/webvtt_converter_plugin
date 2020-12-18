#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2020, Daniel Kao<daniel.kao@gmail.com>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel, QFileDialog, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt
import os

from calibre_plugins.webvtt_convert.config import prefs
import calibre_plugins.webvtt_convert.convert as convert

from calibre.gui2.tools import convert_single_ebook
from calibre.customize.ui import plugin_for_input_format
from calibre.gui2 import Dispatcher
from calibre.ptempfile import PersistentTemporaryFile

class WebVttConvertDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.outputFmt = 'epub'
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase from db/legacy.py
        # This class has many, many methods that allow you to do a lot of
        # things. For most purposes you should use db.new_api, which has
        # a much nicer interface from db/cache.py
        self.db = gui.current_db

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('Click on Choose Directory button first to set the subtile files\' folder, \nand then set up main language and sub language.')
        self.l.addWidget(self.label)

        self.setWindowTitle('WebVtt Converter')
        self.setWindowIcon(icon)

        #self.about_button = QPushButton('About', self)
        #self.about_button.clicked.connect(self.about)
        #self.l.addWidget(self.about_button)

        self.setup_dir_button = QPushButton('Choose Subtitle Directory', self)
        self.setup_dir_button.clicked.connect(self.setup_dir)
        self.l.addWidget(self.setup_dir_button)

        self.setup_cover_file_button = QPushButton('Choose Cover image (Optional)', self)
        self.setup_cover_file_button.clicked.connect(self.setup_cover)
        self.l.addWidget(self.setup_cover_file_button)

        self.main_lang_combo = QComboBox(self)
        self.main_lang_combo.addItem('-')
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Main language:'), alignment=Qt.AlignLeft)
        hbox.addWidget(self.main_lang_combo)
        self.l.addLayout(hbox)

        self.sub_lang_combo = QComboBox(self)
        self.sub_lang_combo.addItem('-')
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Second language:'), alignment=Qt.AlignLeft)
        hbox.addWidget(self.sub_lang_combo)
        self.l.addLayout(hbox)

        self.resize(self.sizeHint())

    def about(self):
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About the Interface Plugin Demo', text.decode('utf-8'))

    def setup_dir(self):
        self.vtt_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        langs = convert.get_lang_list(self.vtt_dir)
        if len(langs) > 0:
            self.main_lang_combo.removeItem(0)
        for lang in langs:
            self.main_lang_combo.addItem(lang)
            self.sub_lang_combo.addItem(lang)

        self.convert_button = QPushButton('Convert', self)
        self.convert_button.clicked.connect(self.convert_vtt_files)
        self.l.addWidget(self.convert_button)

    def setup_cover(self):
        self.cover_file_path, _ = QFileDialog.getOpenFileName(self, 'Select Cover Image', 'Image Files(*.png *.jpg *.jpeg)')

    def convert_vtt_files(self):
        main_lang = str(self.main_lang_combo.currentText())
        if main_lang == '-':
            QMessageBox.about(self, 'Information', 'Select the main language before conversion.')
            return

        sub_lang = str(self.sub_lang_combo.currentText())
        # if user does not select sub_lang, set it to main_lang, so that when converting, it won't generate sub language.
        if sub_lang == '-':
            sub_lang = main_lang

        # convert to html
        if hasattr(self, 'cover_file_path'):
            cover_file_path = self.cover_file_path
        else:
            cover_file_path = None

        self.book_id = self.convert_to_html_add_to_library(self.vtt_dir, main_lang, sub_lang, cover_file_path)

        # add html to epub conversion job
        self.jobs, changed, bad = convert_single_ebook(self.gui, self.gui.library_view.model().db, [self.book_id], True, self.outputFmt)
        func, args, desc, fmt, id, temp_files = self.jobs[0]

        core_usage = 1
        plugin = plugin_for_input_format('html')
        if plugin is not None:
            core_usage = plugin.core_usage

        self.gui.job_manager.run_job(Dispatcher(self.converted_func), func, args=args, description=desc, core_usage=core_usage)

        self.close()

    def convert_to_html_add_to_library(self, vtt_dir, main_lang, sub_lang, cover_file_path):
        '''
        return book_id when the html is added to library
        '''
        html_file = PersistentTemporaryFile('.html')
        convert.convert_webvtt_to_html(vtt_dir, main_lang, sub_lang, html_file.name)
        # add to library
        new_api = self.db.new_api
        from calibre.ebooks.metadata.meta import get_metadata
        with lopen(html_file.name, 'rb') as stream:
            mi = get_metadata(stream, stream_type='html', use_libprs_metadata=True)
        if cover_file_path != None:
            ext = cover_file_path.rpartition('.')[-1].lower().strip()
            if ext not in ('png', 'jpg', 'jpeg'):
                ext = 'jpg'
            with lopen(cover_file_path, 'rb') as stream:
                mi.cover_data = (ext, stream.read())

        # add book in html format
        book_ids, duplicates = new_api.add_books([(mi,{'HTML':html_file.name})], run_hooks=False)
        self.db.data.books_added(book_ids)
        self.gui.library_view.model().books_added(1)
        os.remove(html_file.name)
        
        return book_ids[0]

    def converted_func(self, job):
        temp_file = self.jobs[0][-1][-1].name
        self.db.new_api.add_format(self.book_id, self.outputFmt, temp_file, run_hooks=False)
        self.gui.library_view.model().refresh_ids((self.book_id,))
        os.remove(temp_file)

        QMessageBox.about(self, 'Conversion', "Conversion is done.")

    def marked(self):
        ''' Show books with only one format '''
        db = self.db.new_api
        matched_ids = {book_id for book_id in db.all_book_ids() if len(db.formats(book_id)) == 1}
        # Mark the records with the matching ids
        # new_api does not know anything about marked books, so we use the full
        # db object
        self.db.set_marked_ids(matched_ids)

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:true')
        self.gui.search.do_search()

    def view(self):
        ''' View the most recently added book '''
        most_recent = most_recent_id = None
        db = self.db.new_api
        for book_id, timestamp in db.all_field_for('timestamp', db.all_book_ids()).items():
            if most_recent is None or timestamp > most_recent:
                most_recent = timestamp
                most_recent_id = book_id

        if most_recent_id is not None:
            # Get a reference to the View plugin
            view_plugin = self.gui.iactions['View']
            # Ask the view plugin to launch the viewer for row_number
            view_plugin._view_calibre_books([most_recent_id])

    def update_metadata(self):
        '''
        Set the metadata in the files in the selected book's record to
        match the current metadata in the database.
        '''
        from calibre.ebooks.metadata.meta import set_metadata
        from calibre.gui2 import error_dialog, info_dialog

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata',
                             'No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        db = self.db.new_api
        for book_id in ids:
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            fmts = db.formats(book_id)
            if not fmts:
                continue
            for fmt in fmts:
                fmt = fmt.lower()
                # Get a python file object for the format. This will be either
                # an in memory file or a temporary on disk file
                ffile = db.format(book_id, fmt, as_file=True)
                ffile.seek(0)
                # Set metadata in the format
                set_metadata(ffile, mi, fmt)
                ffile.seek(0)
                # Now replace the file in the calibre library with the updated
                # file. We dont use add_format_with_hooks as the hooks were
                # already run when the file was first added to calibre.
                db.add_format(book_id, fmt, ffile, run_hooks=False)

        info_dialog(self, 'Updated files',
                'Updated the metadata in the files of %d book(s)'%len(ids),
                show=True)

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])
