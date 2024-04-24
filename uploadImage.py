import requests
import re
import base64

# function to import image to imgbb
def upload_image(image_url):
    url = "https://api.imgbb.com/1/upload"
    if image_url is not None:
        try:
            response = requests.get(image_url)
            
            image_name = image_url.split("/")[-1].split("?")[0]
            with open(image_name, "wb") as file:
                file.write(response.content)
            with open(image_name, "rb") as file:
                image_data = file.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
                payload = {
                    "key": "41680522a61e85e1c52e3a331b5bd0fd",
                    "image": base64_image
                }
            response = requests.post(url, payload)
            result = response.json()
            if "data" in result and "url" in result["data"]: 
                print("Image uploaded successfully")
                print("Image URL: ", result["data"]["url"])
                return result["data"]["url"]
            else:
                print("Image upload failed. Error: ", result["error"])
                return None

        except requests.exceptions.RequestException as e:
            print("Error fetching image:", e)
            return None
    else:
        print("Image URL is empty.")
        return None
        
# function to extract image url
def extract_image_url(markdown_file):
    with open(markdown_file, "r", encoding="utf-8") as file:
        content = file.read()
        image_link = re.search(r"!\[.*?\]\((.*?)\)", content)
    return image_link.group(1)

# function to replace the image link after upload process
def update_image_link(markdown_file, old_link, new_link):
    with open(markdown_file, "r", encoding="utf-8") as file:
        content = file.read()
    # Replace the old image link with the new one
    if old_link in content:
        new_content = content.replace(old_link, new_link)
        with open(markdown_file, "w", encoding="utf-8") as file:
            file.write(new_content)
        
        return new_link, new_content
    
    else:
        print("Image link not available")
    