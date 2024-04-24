from flask import Flask, request
from flask_cors import CORS
from instagrapi import Client
from datetime import datetime
from uploadImage import extract_image_url, upload_image, update_image_link
import os
import json

app = Flask(__name__)
CORS(app)

cl = Client()

def upload_image_and_update_link(markdown_file):
    image_url = extract_image_url(markdown_file)
    if image_url is None:
        return None, None
    new_link = upload_image(image_url)
    if new_link is not None:
        new_link, new_content = update_image_link(markdown_file, image_url, new_link)
        return new_link, new_content
    else:
        return new_link, None        

@app.route('/')
def connected():
    #connect to Instagram using Instagrapi
    # Instagram username and password
    instaUsername = "calvin000503"
    instaPassword = "calvin@000503"

    # Log in to Instagram
    if cl is None: 
        cl.login(instaUsername, instaPassword)
        return 'Connected to Instagram! '
    return 'User logged in already'

@app.route('/function1', methods=['POST', 'GET'])
def function1():
    #execute function 1 (get coffee promo by username)
    if request.method == 'POST':
        username = request.form.get('username')
        media_count = 3
        user_id = cl.user_id_from_username(username)
        medias = cl.user_medias(user_id, media_count)
        destination_folder = 'result'
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        count = 1
        for media in medias:
            media_datetime = media.taken_at.strftime("%Y_%m_%d")
            markdown_content = f"""\
# {username}_promo_{media_datetime}

![image]({media.thumbnail_url})

{media.caption_text}

Source: [https://www.instagram.com/p/{media.code}/](https://www.instagram.com/p/{media.code}/)
"""

            # Write Markdown content to a file
            base_filename = f"{username}_promo_{media_datetime}.md"
            filename = base_filename
            count = 1
            
            while os.path.exists(os.path.join(destination_folder, filename)):
                filename, extension = os.path.splitext(base_filename)
                filename = f"{filename}_{count}{extension}"
                count += 1
                
            file_path = os.path.join(destination_folder, filename)
            
            with open(file_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)
        
        return f"Markdown file '{filename}' generated successfully in '{destination_folder}'."

    else:
        return 'Method Not Allowed', 405


@app.route('/function2', methods=['POST', 'GET'])
def function2():
    #execute function 2 (get coffee promo by link)
    if request.method == 'POST':
        instagram_link = request.form.get('instaLink')
        # Extract data from the given link
        media_id = cl.media_pk_from_url(instagram_link)
        media = cl.media_info(media_id)
        username =  media.user.username
        
        # Print relevant information
        media_datetime = media.taken_at.strftime("%Y_%m_%d")
        markdown_content = f"""\
# {username}_promo_{media_datetime} 

![image]({media.thumbnail_url})

{media.caption_text}

Source: [https://www.instagram.com/p/{media.code}/](https://www.instagram.com/p/{media.code}/)
"""
        destination_folder = 'result'
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        # Write Markdown content to a file
        base_filename = f"{username}_promo_{media_datetime}.md"
        filename = base_filename
        count = 1
        while os.path.exists(os.path.join(destination_folder, filename)):
            filename, extension = os.path.splitext(base_filename)
            filename = f"{filename}_{count}{extension}"
            count += 1
            
        file_path = os.path.join(destination_folder, filename)
        
        with open(file_path, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(markdown_content)
        
        new_link, new_content = upload_image_and_update_link(file_path)
        
        if new_link is not None and new_content is not None:    
            return [f"Markdown file '{filename}' generated successfully in '{destination_folder}'.", filename, new_link, new_content]
        else:
            return [f"Markdown file '{filename}' generated successfully in '{destination_folder}'.", filename, '', markdown_content] 
         
    else:
        return 'Method Not Allowed', 405

if __name__ == '__main__':
    app.run(debug=True, port=8080)
