import os

folder_path = r"C:\Users\User\OneDrive\Desktop\Github desktop\deep_learning_acute_illness_pri\data\unparsed\healthy"

# Get all files in the folder
files = sorted(os.listdir(folder_path))  # Sorting ensures consistency

# Loop through files and rename them
for index, filename in enumerate(files, start=1):
    old_path = os.path.join(folder_path, filename)
    
    # Extract file extension
    # file_extension = os.path.splitext(filename)[1]  # Includes the dot (e.g., .jpg, .png)
    file_extension = ".jpg"

    # # Extract whole file name
    filename = os.path.splitext(filename)[0]  # Excludes the dot (e.g., .jpg, .png)

    # Create new filename in the format "s1-m", "s2-m", etc.
    new_filename = f"h-{index+91}-b3{file_extension}"

    # for me to prepend "rug"
    # new_filename = f"rug_{filename}{file_extension}" 
    # new_filename = f"ai{filename}{file_extension}" 


    # # add on the word "new_" to the start of the filename
    # new_filename = f"new_{filename}{file_extension}"

    new_path = os.path.join(folder_path, new_filename)


    # Rename the file
    os.rename(old_path, new_path)
    print(f"Renamed: {filename} → {new_filename}")

print("✅ Done renaming all files!")
