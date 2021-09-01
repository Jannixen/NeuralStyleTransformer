import os
from functools import partial
from io import BytesIO

from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider

from model import NeuralStyleTransformerModel

STYLES_TUPLE = ("Beksinski", "Kandinsky", "Mucha", "Picasso", "The Great Wave off Kanagawa", "Van Gogh")
INITIAL_USER_IMAGE = "styles/init_user_image.jpg"
INITIAL_STYLE_IMAGE = "styles/Picasso.jpg"


class NeuralStyleTransformerApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bottom_layout = BoxLayout(size_hint=(1, None), height=50)
        self.menu_layout = BoxLayout(size_hint=(1, None), height=50)
        self.display_layout = GridLayout(cols=3, padding=50)
        self.title_layout = BoxLayout(size_hint=(1, None), height=50)
        self.style_image = Image(source=INITIAL_STYLE_IMAGE, width=300, height=300)
        self.user_image = Image(source=INITIAL_USER_IMAGE, width=300, height=300)

    def display_style_image(self, style, *args):
        image_dir = 'styles/' + style.replace(" ", "_") + '.jpg'
        self.style_image = Image(source=image_dir, width=300, height=300)
        self.rebuild_display_layout()

    def choose_image(self, *args):
        image_chooser = FileChooserIconView(filters=["*.png", "*.jpg"], path=os.getcwd())
        image_chooser.bind(on_submit=partial(self.update_user_image, image_chooser))
        popup = Popup(title='Choose file',
                      content=image_chooser,
                      size_hint=(None, None), size=(500, 500))
        popup.open()

    def update_user_image(self, image_chooser, *args):
        image_path = image_chooser.selection[0]
        self.user_image = Image(source=image_path, width=300, height=300)
        self.rebuild_display_layout()

    def transform(self, *args):
        transformer = NeuralStyleTransformerModel(self.user_image.source, self.style_image.source)
        pil_image = transformer.get_stylized_image()
        img_bytes = BytesIO()
        pil_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        img = CoreImage(BytesIO(img_bytes.read()), ext='png')

        popup = Popup(title='Stylized image',
                      content=Image(texture=img.texture),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def build_style_dropdown(self):
        style_dropdown = DropDown()

        for style in STYLES_TUPLE:
            single_dropdown_btn = Button(text=style, size_hint_y=None, height=44,
                                         on_press=partial(self.display_style_image, style))
            single_dropdown_btn.bind(on_release=lambda btn: style_dropdown.select(btn.text))
            style_dropdown.add_widget(single_dropdown_btn)

        return style_dropdown

    def build_menu_layout(self):
        image_chooser_button = Button(text='Choose image', size_hint=(1, 1),
                                      on_release=self.choose_image)

        style_dropdown = self.build_style_dropdown()
        style_dropdown_button = Button(text='Choose style', size_hint=(1, 1))
        style_dropdown_button.bind(on_release=style_dropdown.open)
        style_dropdown.bind(on_select=lambda instance, x: setattr(style_dropdown_button, 'text', x))

        output_image_size_slider = Slider(min=50, max=1000, value=300)
        output_image_size_slider_title = Label(text='Output image size:', size_hint=(1, 1))
        output_image_size_slider_value = Label(text=str(output_image_size_slider.value), size_hint=(1 / 3, 1))

        self.menu_layout.add_widget(image_chooser_button)
        self.menu_layout.add_widget(style_dropdown_button)
        self.menu_layout.add_widget(output_image_size_slider_title)
        self.menu_layout.add_widget(output_image_size_slider)
        self.menu_layout.add_widget(output_image_size_slider_value)

    def build_bottom_layout(self):
        transformation_button = Button(text='Start transformation',
                                       on_release=self.transform)

        self.bottom_layout.add_widget(transformation_button)

    def rebuild_display_layout(self):
        self.display_layout.clear_widgets()
        self.display_layout.add_widget(self.user_image)
        self.display_layout.add_widget(Image(source="styles/button.png", width=50, height=50))
        self.display_layout.add_widget(self.style_image)

    def build(self):
        self.build_menu_layout()
        self.build_bottom_layout()

        root = BoxLayout(orientation='vertical')
        root.add_widget(self.menu_layout)
        root.add_widget(self.display_layout)
        root.add_widget(self.bottom_layout)

        self.rebuild_display_layout()

        return root
