import os

def changeCountryImagesToPng():
    folder_path = "images/countries"
    for filename in os.listdir(folder_path):
        base, ext = os.path.splitext(filename)
        new_filename = base + ".png"
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
        print(f"Renamed {filename} to {new_filename}")

changeCountryImagesToPng()
