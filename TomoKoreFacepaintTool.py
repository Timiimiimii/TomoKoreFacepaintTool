try:
    from PIL import Image, ImageCms, ImageOps
    from pyswizzle import nsw_deswizzle, nsw_swizzle
    from pathlib import Path
    import io
except ImportError as e:
    print(f"An import error occurred: {e}")

SWIZZLE_MODE = 4


def gammaedit(img: Image, gamma: int = 0.4545):
    def gamma_map(x):
        return int(round(((x / 255) ** gamma) * 255))

    if img.mode == 'RGBA':
        r, g, b, a = img.split()
        r = r.point(gamma_map)
        g = g.point(gamma_map)
        b = b.point(gamma_map)
        return Image.merge('RGBA', (r, g, b, a))
    if img.mode == 'RGB':
        return img.point(gamma_map)
    return img.convert('RGB').point(gamma_map)


def canvas_2_png(img):
    convert_size  = (256, 256)
    gob_w, gob_h = 1, 1
    bytes_per_block = 4
    swizzled = nsw_deswizzle(raw_data, (convert_size[0], convert_size[1]), (gob_w, gob_h), bytes_per_block, SWIZZLE_MODE)

    if select == 1:
        img = Image.frombytes('RGBA', convert_size, swizzled, 'raw', 'RGBA')

    img = img.convert()
    img = gammaedit(img)
    img.show()

    save_path = imagePath.with_name(imagePath.stem + "CanvasOUTPUT.png")
    img.save(save_path, 'png')
    print(f'Image file saved to {save_path}')
    return


def png_2_canvas(imagePath, useSrgb=False):
    image_res = 0
    img = Image.open(imagePath)

    if img.size != (256, 256):
        while True:
            try:
                print('''
                    Image is at an incorrect resolution (should be 256x256).
                    Please select an option.
                    --------------------------
                    1. Stretch and Resize
                    2. Keep aspect ratio and resize
                    3. Cancel
                    ''')
                image_res = int(input('Select an option: '))
                if 0 < image_res < 4:
                    break
                else:
                    print('Invalid input. Please provide a number from 1 to 3.')
            except ValueError:
                print('woah man can you input a number please?')

    if image_res == 3:
        return

    if image_res == 1:
        img = img.resize((256, 256), 1)
    elif image_res == 2:
        img = ImageOps.fit(img, (256, 256))

    img = img.convert('RGBA')
    if not useSrgb:
        img = gammaedit(img, 2.2)

    convert_img = img.tobytes('raw')
    save_path = imagePath.with_name(imagePath.stem + "OUTPUT.canvas")

    gob_w, gob_h = 1, 1
    bytes_per_block = 4
    height, width = 256, 256
    linear = nsw_swizzle(convert_img, (width, height), (gob_w, gob_h), bytes_per_block, SWIZZLE_MODE)

    with open(save_path, 'wb') as f:
        f.write(bytes(linear))

    print(f'Canvas file saved to {save_path}. Please note that images with varying transparency may become opaque.')


def ugctex_2_png(img):
    convert_size = (512, 512)
    gob_w, gob_h = 4, 4
    bytes_per_block = 8

    with open(Path('DDSHeader.ugctex'), 'rb') as file:
        dds_header = file.read()

    swizzled = nsw_deswizzle(raw_data, convert_size, (gob_w, gob_h), bytes_per_block, SWIZZLE_MODE)

    img = Image.open(io.BytesIO(dds_header + swizzled))
    img = img.convert()
    img = gammaedit(img)
    img.show()

    save_path = imagePath.with_name(imagePath.stem + "UgcTexOUTPUT.png")
    img.save(save_path, 'png')
    print(f'Image file saved to {save_path}')


def png_2_ugctex(imagePath, useSrgb=False):
    image_res = 0
    img = Image.open(imagePath)
    convert_size = (512, 512)

    if img.size != convert_size:
        while True:
            try:
                print('''
                    Image is at an incorrect resolution (should be 512x512).
                    Please select an option.
                    --------------------------
                    1. Stretch and Resize
                    2. Keep aspect ratio and resize
                    3. Cancel
                    ''')
                image_res = int(input('Select an option: '))
                if 0 < image_res < 4:
                    break
                else:
                    print('Invalid input. Please provide a number from 1 to 3.')
            except ValueError:
                print('woah man can you input a number please?')
                
    if image_res != 3:
        if image_res == 1:
            img = img.resize(convert_size, 1)
        elif image_res == 2:
            img = ImageOps.fit(img, convert_size)

        img = img.convert('RGBA')
        if not useSrgb:
            img = gammaedit(img, 2.2)
    else:
        img = img.convert('RGBA')

    dds_bytes = io.BytesIO()
    img.save(dds_bytes, format='DDS', pixel_format='DXT1')

    save_path = imagePath.with_name(imagePath.stem + "OUTPUT.ugctex")
    gob_w, gob_h = 4, 4
    bytes_per_block = 8

    b_slice = dds_bytes.getvalue()[128:]
    swizzled = nsw_swizzle(b_slice, convert_size, (gob_w, gob_h), bytes_per_block, SWIZZLE_MODE)

    with open(save_path, 'wb') as f:
        f.write(bytes(swizzled))

    print(f'UgcTex file saved to {save_path}. Please note that images with varying transparency may become opaque.')


print('''
    Tomodachi Life: Living the Dream
    Facepaint Tool
    By Timimimi
    Thanks to RealDarkCraft for helping me with the format
    I kinda just made this script to help some friends with this
    Uses Aclios' pyswizzle library and Pillow, the friendly PIL fork (python-pillow.org).
''')
while True:
    print('''
    -------
    Functions
    -------
    1. Canvas/UgcTex to PNG
    2. PNG to Canvas/UgcTex
    3. Exit
''')
    try:
        select = int(input("Select an option: "))
        if select == 1:
            imagePath = Path(input(f"Enter Canvas/UgcTex filepath: ").strip())
            with open(imagePath, 'rb') as file:
                raw_data = file.read()
                if len(raw_data) == 262144:
                    print('Canvas file detected.')
                    canvas_2_png(raw_data)
                elif len(raw_data) == 131072:
                    print('UgcTex file detected.')
                    ugctex_2_png(raw_data)
                else:
                    print('Size of file does not match Canvas nor UgcTex files. Please check your file again.')
        elif select == 2:
            imagePath = Path(input("Enter png filepath: ").strip())
            use_srgb = False
            while True:
                miitopia_ripped = input("Is your image ripped from Miitopia? This means it is in sRGB. (Y/N)")
                if miitopia_ripped.upper() == 'Y':
                    use_srgb = True
                    break
                elif miitopia_ripped.upper() == 'N':
                    break
                else:
                    print('Invalid input...Try that again.')

            while True:
                try:
                    png2type = int(
                        input("What file will you convert this png to?\n1. Canvas\n2. UgcTex\nSelect an option: "))
                    if png2type == 1:
                        png_2_canvas(imagePath, use_srgb)
                        break
                    elif png2type == 2:
                        png_2_ugctex(imagePath, use_srgb)
                        break
                    else:
                        print("Invalid input...Let's try that again...")
                except ValueError:
                    print("Invalid input...Let's try that again...")
        elif select == 3:
            print('Alright, see ya~')
            break
        else:
            print('Invalid input. Please enter a number from 1 to 5.')
    except ValueError as e:
        print(e)
        print('woah man can you input a number please?')
