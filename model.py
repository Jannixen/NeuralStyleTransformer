import tensorflow as tf
import tensorflow_hub as hub


class NeuralStyleTransformerModel:

    def __init__(self, user_image_path, style_image_path, style_image_size=(256, 256), output_image_size=(384, 384)):
        self.user_image = self.load_image(user_image_path, output_image_size)
        self.style_image = self.load_image(style_image_path, style_image_size)
        self.generated_image = self.make_generated_image()

    def get_generated_image(self):
        return self.generated_image

    def make_generated_image(self):
        style_image = tf.nn.avg_pool(self.style_image, ksize=[3, 3], strides=[1, 1], padding='SAME')

        hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
        hub_module = hub.load(hub_handle)

        outputs = hub_module(tf.constant(self.user_image), tf.constant(style_image))
        generated_image = outputs[0]

        return tf.keras.preprocessing.image.array_to_img(generated_image[0])

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
