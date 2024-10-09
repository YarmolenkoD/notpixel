import os
import struct
import logging
import aiofiles

MAIN_IMAGE_SIZE = 1000
STENCIL_SIZE = 256

IMAGE_CONFIG = [
  { "image_name": "worldtemplate", "initial_coordinate": { x: 372, y: 372 } },
]

# Helper function to convert RGB values to a hex string
def rgb_to_string(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

async def read_binary_file(filepath):
    """Reads binary file asynchronously."""
    async with aiofiles.open(filepath, 'rb') as file:
        return await file.read()

async def compare_pixels_updates(updated_pixels):
    try:
        stencil_path = os.path.join(os.path.dirname(__file__), "assets", "data", f"{IMAGE_CONFIG[0]['image_name']}.bin")

        stencil_pixels = await read_binary_file(stencil_path)

        start_x = IMAGE_CONFIG[0]["initial_coordinate"]["x"]
        start_y = IMAGE_CONFIG[0]["initial_coordinate"]["y"]

        # Process updated pixels from WebSocket
        for pixel_index_str, new_color in updated_pixels.items():
            pixel_index = int(pixel_index_str)
            pixel_index_adjusted = pixel_index - 1

            x = pixel_index_adjusted % MAIN_IMAGE_SIZE
            y = pixel_index_adjusted // MAIN_IMAGE_SIZE

            # If the pixel is outside the stencil's bounds, skip it
            if x < start_x or x >= start_x + STENCIL_SIZE or y < start_y or y >= start_y + STENCIL_SIZE:
                continue

            coordinate_key = f"{x},{y}"

            # Convert the hex color string to RGB
            bigint = int(new_color[1:], 16)
            r_new = (bigint >> 16) & 255
            g_new = (bigint >> 8) & 255
            b_new = bigint & 255

            # Calculate the index in the stencil binary file
            stencil_index = (y - start_y) * STENCIL_SIZE * 4 + (x - start_x) * 4

            # Extract RGB values from the stencil binary data
            r_stencil = stencil_pixels[stencil_index]
            g_stencil = stencil_pixels[stencil_index + 1]
            b_stencil = stencil_pixels[stencil_index + 2]

            # Compare the new pixel color with the stencil color
            if r_new == r_stencil and g_new == g_stencil and b_new == b_stencil:
                pixel_store.remove_difference(coordinate_key)
            else:
                pixel_store.add_difference(coordinate_key, rgb_to_string(r_stencil, g_stencil, b_stencil))

    except Exception as error:
        logging.error(f"Error processing WebSocket updates: {error}")