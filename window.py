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
        self.bottom_layout = BottomLayout(app_instance=self, size_hint=(1, None), height=50)
        self.menu_layout = MenuLayout(app_instance=self, size_hint=(1, None), height=50)
        self.display_layout = GridLayout(cols=3, padding=50)
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
        output_size = self.menu_layout.get_slider_int_value()
        transformer = NeuralStyleTransformerModel(user_image_path=self.user_image.source,
                                                  style_image_path=self.style_image.source,
                                                  output_image_size=(output_size,
                                                                     output_size))
        pil_image = transformer.get_stylized_image()
        self.show_stylized_image_popup(pil_image, output_size)

    @staticmethod
    def show_stylized_image_popup(pil_image, output_size):
        img_bytes = BytesIO()
        pil_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        img = CoreImage(BytesIO(img_bytes.read()), ext='png')

        popup = Popup(title='Stylized image',
                      content=Image(texture=img.texture),
                      size_hint=(None, None), size=(output_size + 30, output_size + 30))
        popup.open()

    def rebuild_display_layout(self):
        self.display_layout.clear_widgets()
        self.display_layout.add_widget(self.user_image)
        self.display_layout.add_widget(Image(source="styles/button.png", width=50, height=50))
        self.display_layout.add_widget(self.style_image)

    def build(self):
        root = BoxLayout(orientation='vertical')
        root.add_widget(self.menu_layout)
        root.add_widget(self.display_layout)
        root.add_widget(self.bottom_layout)

        self.rebuild_display_layout()

        return root


class BottomLayout(BoxLayout):

    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.build_bottom_layout(app_instance)

    def build_bottom_layout(self, app_instance):
        transformation_button = Button(text='Start transformation',
                                       on_release=app_instance.transform)

        self.add_widget(transformation_button)


class MenuLayout(BoxLayout):

    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.image_chooser_button = Button(text='Choose image', size_hint=(1, 1),
                                           on_release=app_instance.choose_image)
        self.style_dropdown_button = self.build_style_dropdown(app_instance)
        self.output_image_size_slider = Slider(min=50, max=600, value=300)
        self.output_image_size_slider_title = Label(text='Output image size:', size_hint=(1, 1))
        self.output_image_size_slider_value = Label(text=str(self.get_slider_int_value()), size_hint=(1 / 3, 1))
        self.output_image_size_slider.fbind('value', self.change_value_on_slider)
        self.build_menu_layout()

    def get_slider_int_value(self):
        return int(self.output_image_size_slider.value)

    def change_value_on_slider(self, instance, value):
        self.output_image_size_slider_value.text = str(int(value))

    @staticmethod
    def build_style_dropdown(app_instance):
        style_dropdown = DropDown()

        for style in STYLES_TUPLE:
            single_dropdown_btn = Button(text=style, size_hint_y=None, height=44,
                                         on_press=partial(app_instance.display_style_image, style))
            single_dropdown_btn.bind(on_release=lambda btn: style_dropdown.select(btn.text))
            style_dropdown.add_widget(single_dropdown_btn)

        style_dropdown_button = Button(text='Choose style', size_hint=(1, 1))
        style_dropdown_button.bind(on_release=style_dropdown.open)
        style_dropdown.bind(on_select=lambda instance, x: setattr(style_dropdown_button, 'text', x))

        return style_dropdown_button

    def build_menu_layout(self):
        self.add_widget(self.image_chooser_button)
        self.add_widget(self.style_dropdown_button)
        self.add_widget(self.output_image_size_slider_title)
        self.add_widget(self.output_image_size_slider)
        self.add_widget(self.output_image_size_slider_value)
