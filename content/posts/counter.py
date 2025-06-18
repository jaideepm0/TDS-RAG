import os

def count_files():
    json_count = 0
    md_count = 0
    
    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".json") and (not file.startswith('p')):
                json_count += 1
            elif file.endswith(".md"):
                md_count += 1

    return json_count, md_count

# Get the counts
json_files, md_files = count_files()

print(f"JSON files: {json_files}")
print(f"Markdown files: {md_files}")
