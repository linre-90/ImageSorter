from RPA.FileSystem import *
from dotenv import load_dotenv, find_dotenv
import datetime as dt
import os
import uuid


# ***** class for binding image and used file creation date together *****


class ImageObjectWithDate:
    def __init__(self, filePath, filmingDate):
        self.file = filePath
        if filmingDate == "":
            self.filmDate = dt.datetime.now().date()
        else:
            self.filmDate = filmingDate

    def get_file(self):
        return self.file

    def get_filming_date(self):
        return self.filmDate


# ****** variables  *******
# Insert messy image folder path here, no sub folders!!! But can contain multiple folders...
# these are in .env file->
load_dotenv(find_dotenv("folders.env"))
pathToStartFolder = os.getenv("SOURCE_FOLDER")
pathToDestinationFolder = os.getenv("TARGET_FOLDER")
duplicateFolder = os.getenv("DUPLICATE_FOLDER")
# <- these are in .env file
duplicateCount = 0
copiedCount = 0
fs = FileSystem()
allfiles = []
imageObjects = []
folders = []
totalImageCount = 0

# ***** get all images from folders ******
directories = fs.list_directories_in_directory(path=pathToStartFolder)
for folder in directories:
    x = fs.list_files_in_directory(folder)
    for file in x:
        allfiles.append(file)


# **** make folder names *****
for file in allfiles:
    dates = [dt.datetime.fromtimestamp(fs.get_file_modified_date(file)).date(),
             dt.datetime.fromtimestamp(fs.get_file_creation_date(file)).date()]
    dates.sort()
    folders.append(dates[0])
    imageObjects.append(ImageObjectWithDate(file, dates[0]))


# ***** duplicate folder creation *****
if not fs.does_directory_exist(pathToDestinationFolder + "\\" + duplicateFolder):
    fs.create_directory(path=pathToDestinationFolder + "\\" + duplicateFolder, parents=False, exist_ok=True)
# ***** create image folders *****
for folder in folders:
    folderYear = pathToDestinationFolder + dt.date.strftime(folder, "%Y")
    folderDate = dt.date.strftime(folder, "%m-%d")
    if not fs.does_directory_exist(folderYear):
        fs.create_directory(path=folderYear, parents=False, exist_ok=True)
        if not fs.does_directory_exist(folderYear+folderDate):
            fs.create_directory(path=folderYear+"\\"+folderDate, parents=False, exist_ok=True)
    else:
        if not fs.does_directory_exist(folderYear + folderDate):
            fs.create_directory(path=folderYear + "\\" + folderDate, parents=False, exist_ok=True)

# ***** move images *****
for fileObject in imageObjects:
    # get actual name from filepath
    actualFileName = str(fileObject.get_file()).split("\\")
    actualFileName = actualFileName[len(actualFileName)-1]
    year = dt.date.strftime(fileObject.get_filming_date(), "%Y")
    date = dt.date.strftime(fileObject.get_filming_date(), "%m-%d")
    # if file exists copy file to duplicates folder and assign uuid to its name to avoid
    # bad things if there is more duplicates of same picture
    if fs.does_file_exist(pathToDestinationFolder + "\\" + year + "\\" + date + "\\" + actualFileName):
        fs.move_file(fileObject.get_file(), pathToDestinationFolder + "\\" + duplicateFolder + "\\" + str(uuid.uuid4()) + actualFileName)
        duplicateCount += 1
        totalImageCount += 1
    else:
        fs.move_file(fileObject.get_file(), pathToDestinationFolder + "\\" + year + "\\" + date + "\\" + actualFileName)
        totalImageCount += 1
        copiedCount += 1

print("Duplicate image count: " + str(duplicateCount))
print("Total image count: " + str(totalImageCount))
print("Original copied images count: " + str(totalImageCount))



