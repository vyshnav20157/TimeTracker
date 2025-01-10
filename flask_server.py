from flask import Flask, request
import threading

app = Flask(__name__)

# Store the current active URL
current_url = None

@app.route('/set_url', methods=['POST'])
def set_url():
    global current_url
    current_url = request.json.get('url')
    return "URL Updated", 200

@app.route('/get_url', methods=['GET'])
def get_url():
    return current_url or "No URL available", 200

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Run the Flask server in a separate thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

if __name__ == "__main__":
    print("Server started on http://localhost:5000")
    # You can add your existing tracking code here to use the server for URL updates.
