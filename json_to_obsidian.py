import json
import os
import re
import requests
import shutil
import yaml

def get_correct_image_extension(url):
    if url.startswith("https://storage.googleapis.com/mem"):
        for ext in [".png", ".jpg", ".jpeg"]:
            if ext in url:
                return ext
    return None

def download_file(url, output_file_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_file_path, "wb") as file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, file)

    # Handle images with UUID appended to their filename
    correct_ext = get_correct_image_extension(url)
    if correct_ext is not None:
        output_file_path_with_ext = output_file_path + correct_ext
        os.rename(output_file_path, output_file_path_with_ext)
        return output_file_path_with_ext

    return output_file_path

def write_markdown_file(output_file_path, data):
    frontmatter = {
        "created": data.get("created"),
        "updated": data.get("updated"),
        "tags": data.get("tags", [])
    }

    with open(output_file_path, "w") as file:
        # Write YAML frontmatter
        file.write("---\n")
        file.write(yaml.dump(frontmatter))
        file.write("---\n\n")

        # Write the content
        file.write(data.get("content", ""))


def process_attachments(content, attachments_base_url):
    for attachment in attachments_base_url:
        content = content.replace(attachment["original_url"], attachment["local_url"])
    return content


def sanitize_filename(name):
    # Allow emojis and specific special characters
    return re.sub(r'[^a-zA-Z0-9_!$%&*()\-=+{}\[\];\'",.<>?`~\s]', '', name)

def truncate_filename(filename, max_length=50):
    name, extension = os.path.splitext(filename)

    if len(filename) > max_length:
        name = name[: max_length - len(extension)]

    return f"{name}{extension}"

def find_image_urls(content):
    image_urls = re.findall(r'!\[.*?\]\((https?://[\S]+)\)', content)
    return image_urls

input_file_path = "notes.json"
output_folder = "output"

with open(input_file_path, "r") as file:
    data = json.load(file)

items = data

for item in items:
    title = item.get("title", "Untitled")
    created = item.get("created")
    updated = item.get("updated")
    tags = item.get("tags", [])
    content = item.get("markdown", "")

    title_sanitized = sanitize_filename(title)
    file_name = f"{title_sanitized}.md"
    file_name = truncate_filename(file_name)
    output_file_path = os.path.join(output_folder, file_name)

    image_urls = find_image_urls(content)
    attachments_base_url = []

    for url in image_urls:
        file_name = os.path.basename(url)
        output_attachments_folder = os.path.join(output_folder, "attachments")
        os.makedirs(output_attachments_folder, exist_ok=True)

        output_attachment_path = os.path.join(output_attachments_folder, file_name)

        try:
            output_attachment_path = download_file(url, output_attachment_path)
            local_url = f"./attachments/{os.path.basename(output_attachment_path)}"
            attachments_base_url.append({"original_url": url, "local_url": local_url})
        except requests.exceptions.RequestException as e:
            print(f"Failed to download attachment {url} due to {e}")

    content = process_attachments(content, attachments_base_url)

    # Strip the title from the content
    content = re.sub(r'^#\s.*\n\n', '', content)

    # Skip empty notes and mention them
    if not content.strip() or content.strip() == f"# {title}":
        print(f"Skipping empty note: {title}")
        continue

    write_markdown_file(output_file_path, {
        "created": created,
        "updated": updated,
        "tags": tags,
        "content": content.strip(),
    })
    print("done")
