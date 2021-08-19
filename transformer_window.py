from functools import partial

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

STYLES_TUPLE = ("Beksinski", "Kandinsky", "Mucha", "Picasso", "The Great Wave off Kanagawa", "Van Gogh")
INITIAL_USER_IMAGE = "styles/init_user_image.jpg"
INITIAL_STYLE_IMAGE = "styles/Picasso.jpg"
INITIAL_RESULT_IMAGE = "styles/black.jpg"


class NeuralStyleTransformerApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bottom_layout = BoxLayout(size_hint=(1, None), height=50)
        self.display_layout = GridLayout(cols=2, padding=50)
        self.title_layout = BoxLayout(size_hint=(1, None), height=50)
        self.style_image = Image(source=INITIAL_STYLE_IMAGE, width=300, height=300)
        self.user_image = Image(source=INITIAL_USER_IMAGE, width=300, height=300)
        self.result_image = Image(source=INITIAL_RESULT_IMAGE, width=300, height=300)

    def display_style_image(self, style, *args):
        image_dir = 'styles/' + style.replace(" ", "_") + '.jpg'
        self.style_image = Image(source=image_dir, width=300, height=300)
        self.rebuild_display_layout()

    def choose_image(self):
        pass

    def build_style_dropdown(self):
        style_dropdown = DropDown()

        for style in STYLES_TUPLE:
            single_dropdown_btn = Button(text=style, size_hint_y=None, height=44,
                                         on_press=partial(self.display_style_image, style))
            single_dropdown_btn.bind(on_release=lambda btn: style_dropdown.select(btn.text))
            style_dropdown.add_widget(single_dropdown_btn)

        style_dropdown_button = Button(text='Choose style', size_hint=(1, 1))
        style_dropdown_button.bind(on_release=style_dropdown.open)
        style_dropdown.bind(on_select=lambda instance, x: setattr(style_dropdown_button, 'text', x))
        return style_dropdown_button

    def build_title_layout(self):
        title_label = Label(text='Neural Style Transformer', height=50, font_size='20sp')
        self.title_layout.add_widget(title_label)

    def build_bottom_layout(self):
        image_chooser_button = Button(text='Choose image',
                                      on_press=partial(self.choose_image))

        self.bottom_layout.add_widget(image_chooser_button)
        self.bottom_layout.add_widget(self.build_style_dropdown())

    def rebuild_display_layout(self):
        self.display_layout.clear_widgets()
        self.display_layout.add_widget(self.user_image)
        self.display_layout.add_widget(self.style_image)
        self.display_layout.add_widget(Image(source="styles/arrow.png", width=150, height=150))
        self.display_layout.add_widget(self.result_image)

    def build(self):
        self.build_title_layout()
        self.build_bottom_layout()

        root = BoxLayout(orientation='vertical')
        root.add_widget(self.title_layout)
        root.add_widget(self.display_layout)
        root.add_widget(self.bottom_layout)

        self.rebuild_display_layout()

        return root


if __name__ == '__main__':
    NeuralStyleTransformerApp().run()
