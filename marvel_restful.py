import pandas as pd
from flask import Flask, jsonify
from flask_restful import Resource, Api
import sys
import threading
import requests
from PyQt5.QtWidgets import QApplication,QLabel, QTextEdit, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

# Flask app initialization
app = Flask(__name__)
api = Api(app)

# Load and process CSV data
data_frame = pd.read_csv('marvel.csv', encoding='ISO-8859-1')
data_frame = data_frame.drop_duplicates(subset=['Title'])

# Convert movie titles to lowercase for case-insensitive search
data_frame['Title'] = data_frame['Title'].str.lower()
data_store = data_frame.set_index('Title').to_dict(orient='index')

# Define the Flask resource for fetching movie data
class GetMovieData(Resource):
    def get(self, movie_title):
        movie_title = movie_title.lower()  # Convert incoming title to lowercase
        if movie_title in data_store:
            return jsonify(data_store[movie_title])
        else:
            return jsonify({"message": "Movie Not Found"})

# Add resource to API
api.add_resource(GetMovieData, '/movie/<string:movie_title>')

# Function to run Flask in a separate thread
def run_flask():
    app.run(debug=False, use_reloader=False)  # Disable reloader to avoid thread conflict

# Start Flask in a new thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True  # Daemon thread will close when the main program exits
flask_thread.start()

# PyQt5 application setup
def get_movie_data():
    movie_title = movie_input.text().strip()  # Get the input movie title
    if not movie_title:
        QMessageBox.critical(window, "Input Error", "Please Enter a Movie Title")
        return

    movie_title = movie_title.lower()  # Convert to lowercase to match Flask API

    try:
        # Send request to Flask API
        response = requests.get(f"http://127.0.0.1:5000/movie/{movie_title}")
        if response.status_code == 200:
            movie_data = response.json()  # Parse JSON response
            if "message" in movie_data and movie_data["message"] == "Movie Not Found":
                result_label.setText(f"{movie_title} Not Found")
            else:
                # Display movie data
                result = "\n".join([f"{key}: {value}" for key, value in movie_data.items()])
                result_display.setPlainText(result)
                result_label.setText("")
        else:
            result_label.setText(f"{movie_title} Not Found")
    except Exception as e:
        result_display.setText( f"Failed to connect to the server: {e}")
        result_display.setPlainText("")
# PyQt5 GUI setup
app_gui = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('Marvel Movies Data')
window.setGeometry(1000, 900, 700, 700)

# Create layout, input field, and button
layout = QVBoxLayout()
movie_input = QLineEdit()
movie_input.setPlaceholderText("Enter Movie Title")
movie_input.setStyleSheet("font-size:18px; padding: 10px")
search_button = QPushButton("Get Movie Data")
result_label = QLabel("")
result_display = QTextEdit()

# Label to show errors or status messages
result_label.setStyleSheet("color:red;" )
result_label.setAlignment(Qt.AlignCenter)

# Text area to display movie details

result_display.setReadOnly(True)
result_display.setStyleSheet("""
    background-color: #edf6fc;
    font-size: 16px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
""")

search_button.setStyleSheet("""
    QPushButton {
        font-size: 16px;
        padding: 10px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }""")


# Add widgets to layout
layout.addWidget(movie_input)
layout.addWidget(search_button)
layout.addWidget(result_label)
layout.addWidget(result_display)
layout.setSpacing(15)
window.setLayout(layout)


# Connect button click to get_movie_data function
search_button.clicked.connect(get_movie_data)

# Show the window
window.show()

# Execute the PyQt5 event loop
sys.exit(app_gui.exec())
