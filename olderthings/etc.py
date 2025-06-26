import os

def changeCountryImagesToPng():
    folder_path = "images/countries2"
    for filename in os.listdir(folder_path):
        base, ext = os.path.splitext(filename)
        new_filename = base + ".png"
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
        print(f"Renamed {filename} to {new_filename}")

def listGoogleDriveContents():
    home_folder = os.path.expanduser("~")
    folder_path = os.path.join(home_folder, "GoogleDrive/My Drive/Projects/Ironinsights/data/extracted")
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            print(f"Folder: {item}")
        else:
            print(f"File: {item}")

#changeCountryImagesToPng()
listGoogleDriveContents()
