import sqlite3
from functools import partial
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput



# Класс для экрана списка заметок
class NoteListScreen(Screen):
    def __init__(self, **kwargs):
        super(NoteListScreen, self).__init__(**kwargs)

        #создание списка заметок
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 50))
        self.scrollview.add_widget(self.layout)

        #создание кнопки 'Создать заметку'
        self.container = GridLayout(cols=1)
        self.container.add_widget(self.scrollview)
        self.container.add_widget(Button(text='Создать заметку', size_hint=(1, None), height=50, background_color=(1, 2, 3, 1), on_release=self.go_to_create_note))

        #добавление кнопки на экран
        self.add_widget(self.container)

        self.load_notes()

    def load_notes(self):
        self.layout.clear_widgets()

        connection = sqlite3.connect('notes.db')
        cursor = connection.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT)')
        cursor.execute('SELECT id, title FROM notes ORDER BY id DESC')
        connection.commit()
        notes = cursor.fetchall()
        connection.close()

        for note in notes:
            note_id = note[0]
            title = note[1]
            note_button = Button(text=title, size_hint_y=None, height=40, on_release=partial(self.view_note, note_id))
            self.layout.add_widget(note_button)

    def view_note(self, note_id, *args):
        connection = sqlite3.connect('notes.db')
        cursor = connection.cursor()
        cursor.execute('SELECT title, content FROM notes WHERE id = ?', (note_id,))
        note_data = cursor.fetchone()
        connection.close()

        if note_data:
            title, content = note_data

            view_note_screen = self.manager.get_screen('view_note')
            view_note_screen.load_note_data(title, content)
            self.manager.current = 'view_note'

    def go_to_create_note(self, *args):
        self.manager.current = 'create_note'


class CreateNoteScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateNoteScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1)

        # Создание текстовых полей для ввода названия и содержимого заметки
        self.title_input = TextInput(multiline=False)
        self.content_input = TextInput()

        # Создание кнопок "Создать заметку" и "Отмена"
        create_button = Button(text='Создать заметку', background_color=(1, 2, 3, 1),)
        create_button.bind(on_release=self.create_note)
        cancel_button = Button(text='Отмена', background_color=(1, 2, 3, 1),)
        cancel_button.bind(on_release=self.go_back)

        # Добавление виджетов на экран
        self.layout.add_widget(Label(text='Название заметки:'))
        self.layout.add_widget(self.title_input)
        self.layout.add_widget(Label(text='Содержимое заметки:'))
        self.layout.add_widget(self.content_input)
        self.layout.add_widget(create_button)
        self.layout.add_widget(cancel_button)
        self.add_widget(self.layout)

    def create_note(self, btn):
        title = self.title_input.text
        content = self.content_input.text

        # Создание новой заметки в базе данных
        connection = sqlite3.connect('notes.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
        connection.commit()
        connection.close()

        # Очистка полей ввода
        self.title_input.text = ''
        self.content_input.text = ''

        # Обновление списка заметок на главном экране
        note_list_screen = self.manager.get_screen('note_list')
        note_list_screen.load_notes()

        # Переход на главный экран
        self.manager.current = 'note_list'

    def go_back(self, instance):
        # Переход на главный экран
        self.manager.current = 'note_list'


# Класс для экрана просмотра заметки
class ViewNoteScreen(Screen):
    def __init__(self, **kwargs):
        super(ViewNoteScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1)

        self.title_label = Label()
        self.content_label = Label()

        # Создание кнопки "Вернуться на главную"
        back_button = Button(text='Вернуться на главную', background_color=(1, 2, 3, 1))
        back_button.bind(on_release=self.load_notes)

        # Создание кнопки "Редактировать"
        edit_button = Button(text='Редактировать', background_color=(1, 2, 3, 1))
        edit_button.bind(on_release=self.edit_note)

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.content_label)
        self.layout.add_widget(back_button)
        self.layout.add_widget(edit_button)

        self.add_widget(self.layout)

    def load_note_data(self, title, content):
        self.title_label.text = title
        self.content_label.text = content

    def edit_note(self, instance):
        self.manager.current = 'edit_note'
        self.manager.get_screen('edit_note').load_note_data(self.title_label.text, self.content_label.text)

    def load_notes(self, *args):
        note_list_screen = self.manager.get_screen('note_list')
        note_list_screen.load_notes()
        self.manager.current = 'note_list'



# Класс для экрана редактирования заметки
class EditNoteScreen(Screen):
    def __init__(self, **kwargs):
        super(EditNoteScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1)

        self.title_input = TextInput(size_hint_y=None, height=40, readonly=False)
        self.content_input = TextInput(readonly=False)

        # Создание кнопки "Сохранить"
        save_button = Button(text='Сохранить', background_color=(1, 2, 3, 1),)
        save_button.bind(on_release=self.save_note)

        # Создание кнопки "Удалить"
        delete_button = Button(text='Удалить', background_color=(1, 2, 3, 1),)
        delete_button.bind(on_release=self.delete_note)

        self.layout.add_widget(self.title_input)
        self.layout.add_widget(self.content_input)
        self.layout.add_widget(save_button)
        self.layout.add_widget(delete_button)

        self.add_widget(self.layout)

    def load_note_data(self, title, content):
        self.note_id = None
        connection = sqlite3.connect('notes.db')
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM notes WHERE title = ?', (title,))
        note_id = cursor.fetchone()
        connection.close()

        if note_id:
            self.note_id = note_id[0]

        self.title_input.text = title
        self.content_input.text = content

    def save_note(self, instance):
        connection = sqlite3.connect('notes.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (self.title_input.text,
                                                                               self.content_input.text,
                                                                               self.note_id))
        connection.commit()
        connection.close()

        self.manager.current = 'note_list'
        self.manager.get_screen('note_list').load_notes()

    def delete_note(self, instance):
        connection = sqlite3.connect('notes.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM notes WHERE title = ?', (self.title_input.text,))
        connection.commit()
        connection.close()

        self.manager.current = 'note_list'
        self.manager.get_screen('note_list').load_notes()


# Класс для управления экранами
class NoteApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(NoteListScreen(name='note_list'))
        screen_manager.add_widget(CreateNoteScreen(name='create_note'))
        screen_manager.add_widget(ViewNoteScreen(name='view_note'))
        screen_manager.add_widget(EditNoteScreen(name='edit_note'))

        return screen_manager


if __name__ == '__main__':
    NoteApp().run()
