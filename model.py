import matplotlib.pylab as plt
import tensorflow as tf
import tensorflow_hub as hub
from matplotlib import gridspec


class NeuralStyleTransformerModel:

    def __init__(self, user_image_path, style_image_path, style_image_size=(256, 256), output_image_size=(384, 384)):
        self.user_image = self.load_image(user_image_path, output_image_size)
        self.style_image = self.load_image(style_image_path, style_image_size)
        self.stylized_image = self.make_stylized_image()

    def get_stylized_image(self):
        return self.stylized_image

    def make_stylized_image(self):
        style_image = tf.nn.avg_pool(self.style_image, ksize=[3, 3], strides=[1, 1], padding='SAME')

        hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
        hub_module = hub.load(hub_handle)

        outputs = hub_module(tf.constant(self.user_image), tf.constant(style_image))
        stylized_image = outputs[0]

        return tf.keras.preprocessing.image.array_to_img(stylized_image[0])

    @staticmethod
    def crop_center(image):
        shape = image.shape
        new_shape = min(shape[1], shape[2])
        offset_y = max(shape[1] - shape[2], 0) // 2
        offset_x = max(shape[2] - shape[1], 0) // 2
        image = tf.image.crop_to_bounding_box(
            image, offset_y, offset_x, new_shape, new_shape)
        return image

    def load_image(self, image_url, image_size=(256, 256)):
        img = tf.io.decode_image(
            tf.io.read_file(image_url),
            channels=3, dtype=tf.float32)[tf.newaxis, ...]
        img = self.crop_center(img)
        img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)
        return img

    @staticmethod
    def show_n(images, titles=('',)):
        n = len(images)
        image_sizes = [image.shape[1] for image in images]
        w = (image_sizes[0] * 6) // 320
        plt.figure(figsize=(w * n, w))
        gs = gridspec.GridSpec(1, n, width_ratios=image_sizes)
        for i in range(n):
            plt.subplot(gs[i])
            plt.imshow(images[i][0], aspect='equal')
            plt.axis('off')
            plt.title(titles[i] if len(titles) > i else '')
        plt.show()


content_image_url = "styles/cat.jpg"
style_image_url = "styles/Mucha.jpg"

NeuralStyleTransformerModel(content_image_url, style_image_url)
