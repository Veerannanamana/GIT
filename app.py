from flask import Flask, render_template, request, jsonify
import requests
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def parse_github_url(github_url):
    try:
        path = github_url.replace("https://github.com/", "").strip("/")
        owner_repo = path.split("/")
        if len(owner_repo) != 2:
            return None, None
        return owner_repo[0], owner_repo[1]
    except Exception:
        return None, None

def file_exists(api_url, headers):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return True, response.json().get('sha')
    return False, None

@app.route('/push-code', methods=['POST'])
def push_code():
    data = request.json
    github_url = data.get("github_url")
    token = data.get("token")
    branch = data.get("branch", "main")
    filename = data.get("filename")
    code = data.get("code")

    if not github_url or not token or not filename or not code:
        return jsonify({"error": "Missing required fields"}), 400

    owner, repo = parse_github_url(github_url)
    if not owner or not repo:
        return jsonify({"error": "Invalid GitHub URL"}), 400

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    exists, sha = file_exists(api_url + f"?ref={branch}", headers)
    if exists:
        return jsonify({"error": "File already exists"}), 409

    payload = {
        "message": f"Create {filename}",
        "content": base64.b64encode(code.encode()).decode(),
        "branch": branch
    }

    put_response = requests.put(api_url, headers=headers, json=payload)

    if put_response.status_code in [200, 201]:
        return jsonify({"message": "File created successfully!"})
    else:
        error_message = put_response.json().get('message', 'Unknown error')
        return jsonify({"error": error_message}), put_response.status_code

@app.route('/get-code', methods=['POST'])
def get_code():
    data = request.json
    github_url = data.get("github_url")
    token = data.get("token")
    branch = data.get("branch", "main")
    filename = data.get("filename")

    if not github_url or not token or not filename:
        return jsonify({"error": "Missing required fields"}), 400

    owner, repo = parse_github_url(github_url)
    if not owner or not repo:
        return jsonify({"error": "Invalid GitHub URL"}), 400

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}?ref={branch}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        content = response.json().get("content")
        if content:
            code = base64.b64decode(content).decode('utf-8')
            return jsonify({"message": "Code fetched successfully!", "code": code})
        else:
            return jsonify({"error": "Content not found in the file"}), 404
    else:
        error_message = response.json().get('message', 'Unknown error')
        return jsonify({"error": error_message}), response.status_code

@app.route('/update-code', methods=['POST'])
def update_code():
    data = request.json
    github_url = data.get("github_url")
    token = data.get("token")
    branch = data.get("branch", "main")
    filename = data.get("filename")
    code = data.get("code")

    if not github_url or not token or not filename or not code:
        return jsonify({"error": "Missing required fields"}), 400

    owner, repo = parse_github_url(github_url)
    if not owner or not repo:
        return jsonify({"error": "Invalid GitHub URL"}), 400

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    exists, sha = file_exists(api_url + f"?ref={branch}", headers)
    if not exists:
        return jsonify({"error": "File does not exist"}), 404

    payload = {
        "message": f"Update {filename}",
        "content": base64.b64encode(code.encode()).decode(),
        "branch": branch,
        "sha": sha
    }

    put_response = requests.put(api_url, headers=headers, json=payload)

    if put_response.status_code == 200:
        return jsonify({"message": "File updated successfully!"})
    else:
        error_message = put_response.json().get('message', 'Unknown error')
        return jsonify({"error": error_message}), put_response.status_code

@app.route('/delete-code', methods=['POST'])
def delete_code():
    data = request.json
    github_url = data.get("github_url")
    token = data.get("token")
    branch = data.get("branch", "main")
    filename = data.get("filename")

    if not github_url or not token or not filename:
        return jsonify({"error": "Missing required fields"}), 400

    owner, repo = parse_github_url(github_url)
    if not owner or not repo:
        return jsonify({"error": "Invalid GitHub URL"}), 400

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    exists, sha = file_exists(api_url + f"?ref={branch}", headers)
    if not exists:
        return jsonify({"error": "File does not exist"}), 404

    payload = {
        "message": f"Delete {filename}",
        "branch": branch,
        "sha": sha
    }

    delete_response = requests.delete(api_url, headers=headers, json=payload)

    if delete_response.status_code == 200:
        return jsonify({"message": "File deleted successfully!"})
    else:
        error_message = delete_response.json().get('message', 'Unknown error')
        return jsonify({"error": error_message}), delete_response.status_code

if __name__ == '__main__':
    app.run(debug=True)
