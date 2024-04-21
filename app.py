from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Folder to move selected images to
DESTINATION_FOLDER = 'path_to_destination_folder'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['folder_path'] = request.form['folder']
        session['destination_folder'] = request.form['destination_folder']
        return redirect(url_for('view_image'))
    return render_template('index.html')

@app.route('/view_image/', methods=['GET', 'POST'])
def view_image():
    folder_path = session.get('folder_path', None)
    destination_folder = session.get('destination_folder', None)
    if not folder_path or not destination_folder:
        return redirect(url_for('index'))

    if 'images' not in session or not session['images']:
        images = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        images.sort()  # Sort the images alphabetically
        session['images'] = images
        session['index'] = 0
    else:
        images = session['images']

    if request.method == 'POST':
        action = request.form['action']
        current_image = images[session['index']]
        current_image_path = os.path.join(folder_path, current_image)
        if action == 'move':
            shutil.move(current_image_path, os.path.join(destination_folder, current_image))
            images.pop(session['index'])  # Remove moved image from the list
        elif action == 'delete':
            os.remove(current_image_path)
            images.pop(session['index'])  # Remove deleted image from the list
        elif action == 'skip':
            session['index'] += 1

        if session['index'] >= len(images):
            session.pop('images', None)  # Reset the image list if we reach the end
            session.pop('index', None)
            return 'No more images.'

    image_file = images[session['index']]
    return render_template('view_image.html', image_file=image_file, folder_path=folder_path)

@app.route('/images/<path:folder_path>/<filename>')
def send_image(folder_path, filename):
    return send_from_directory(folder_path, filename)

if __name__ == '__main__':
    app.run(debug=True)

