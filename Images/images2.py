from PIL import Image


def process_image(input_path, output_path):
    """
    Преобразование серых цветов в чёрные.
    :param input_path:
    :param output_path:
    :return:
    """
    # Open the image
    image = Image.open(input_path)

    # Convert the image to grayscale
    grayscale_image = image.convert("L")

    # Convert the image to binary (black and white) using a threshold
    threshold = 150  # Adjust the threshold value as needed
    binary_image = grayscale_image.point(lambda x: 0 if x < threshold else 255, '1')

    # Save the processed image
    binary_image.save(output_path)


if __name__ == "__main__":
    input_image_path = r"c:\!SAVE\Numbers\photo_2023-12-25_14-14-03.jpg"  # Replace with the path to your input image
    output_image_path = r"c:\!SAVE\Numbers\new.jpg"  # Replace with the desired output path

    process_image(input_image_path, output_image_path)
