from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://vidlink.pro",
    "Referer": "https://vidlink.pro/"
}
API = "https://enc-dec.app/api"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vidlink Resolver</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; min-height: 100vh; padding: 30px 20px; }
  h1 { text-align: center; color: #a78bfa; margin-bottom: 30px; font-size: 1.8rem; letter-spacing: 1px; }
  .card { background: #1a1a2e; border: 1px solid #2d2d4e; border-radius: 12px; padding: 24px; max-width: 700px; margin: 0 auto 24px; }
  label { display: block; margin-bottom: 6px; color: #a0a0c0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
  input, select { width: 100%; background: #0d0d1a; border: 1px solid #3d3d6e; border-radius: 8px; color: #e0e0e0; padding: 10px 14px; font-size: 0.95rem; margin-bottom: 16px; outline: none; transition: border 0.2s; }
  input:focus, select:focus { border-color: #a78bfa; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  button { width: 100%; background: linear-gradient(135deg, #7c3aed, #a78bfa); border: none; border-radius: 8px; color: #fff; padding: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
  button:hover { opacity: 0.85; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  #result { max-width: 700px; margin: 0 auto; }
  .result-card { background: #1a1a2e; border: 1px solid #2d2d4e; border-radius: 12px; padding: 20px; }
  .result-card h2 { color: #a78bfa; margin-bottom: 16px; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
  .field { margin-bottom: 12px; }
  .field .key { color: #6060a0; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 4px; }
  .field .val { background: #0d0d1a; border-radius: 6px; padding: 8px 12px; font-size: 0.9rem; word-break: break-all; }
  .field .val a { color: #a78bfa; text-decoration: none; }
  .field .val a:hover { text-decoration: underline; }
  .error { background: #2a0d0d; border: 1px solid #6e2d2d; border-radius: 12px; padding: 20px; color: #ff6b6b; }
  pre { background: #0d0d1a; border-radius: 8px; padding: 14px; overflow-x: auto; font-size: 0.82rem; line-height: 1.5; color: #c0c0e0; white-space: pre-wrap; word-break: break-all; }
  .loader { text-align: center; padding: 30px; color: #a78bfa; }
  .ep-row { display: none; }
  .ep-row.visible { display: grid; }
</style>
</head>
<body>
<h1>⚡ Vidlink Resolver</h1>
<div class="card">
  <label>Type</label>
  <select id="type" onchange="toggleEp()">
    <option value="movie">Movie</option>
    <option value="tv">TV Show</option>
  </select>
  <label>TMDB ID</label>
  <input id="tmdb_id" type="text" placeholder="e.g. 105248" value="105248">
  <div class="row ep-row" id="ep-row">
    <div>
      <label>Season</label>
      <input id="season" type="text" placeholder="1" value="1">
    </div>
    <div>
      <label>Episode</label>
      <input id="episode" type="text" placeholder="1" value="1">
    </div>
  </div>
  <button id="btn" onclick="resolve()">Resolve</button>
</div>
<div id="result"></div>

<script>
function toggleEp() {
  const row = document.getElementById('ep-row');
  row.classList.toggle('visible', document.getElementById('type').value === 'tv');
}
toggleEp();

async function resolve() {
  const btn = document.getElementById('btn');
  const result = document.getElementById('result');
  btn.disabled = true;
  btn.textContent = 'Resolving...';
  result.innerHTML = '<div class="loader">⏳ Fetching stream data...</div>';

  const payload = {
    type: document.getElementById('type').value,
    tmdb_id: document.getElementById('tmdb_id').value.trim(),
    season: document.getElementById('season').value.trim(),
    episode: document.getElementById('episode').value.trim(),
  };

  try {
    const res = await fetch('/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    btn.disabled = false;
    btn.textContent = 'Resolve';
    if (data.error) {
      result.innerHTML = `<div class="error"><strong>Error:</strong> ${data.error}</div>`;
      return;
    }
    renderResult(data);
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Resolve';
    result.innerHTML = `<div class="error"><strong>Network error:</strong> ${e.message}</div>`;
  }
}

function renderResult(data) {
  const result = document.getElementById('result');
  let fields = '';

  if (data.url) {
    fields += field('Resolved URL', `<a href="${data.url}" target="_blank">${data.url}</a>`);
  }
  if (data.encrypted_id) {
    fields += field('Encrypted ID', data.encrypted_id);
  }
  if (data.vidlink_url) {
    fields += field('Vidlink API URL', `<a href="${data.vidlink_url}" target="_blank">${data.vidlink_url}</a>`);
  }

  const rawJson = JSON.stringify(data.raw, null, 2);
  fields += `<div class="field"><div class="key">Raw Response</div><pre>${rawJson}</pre></div>`;

  result.innerHTML = `<div class="result-card"><h2>✅ Result</h2>${fields}</div>`;
}

function field(key, val) {
  return `<div class="field"><div class="key">${key}</div><div class="val">${val}</div></div>`;
}
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/resolve", methods=["POST"])
def resolve():
    body = request.get_json()
    tmdb_id = body.get("tmdb_id", "").strip()
    media_type = body.get("type", "movie")
    season = body.get("season", "1")
    episode = body.get("episode", "1")

    if not tmdb_id:
        return jsonify({"error": "TMDB ID is required"}), 400

    try:
        # Encrypt TMDB ID
        enc_url = f"{API}/enc-vidlink?text={tmdb_id}"
        enc_resp = requests.get(enc_url, timeout=15).json()
        if enc_resp.get("status") != 200:
            return jsonify({"error": f"Encryption failed: {enc_resp.get('error', 'unknown')}"}), 500
        encrypted = enc_resp["result"]

        # Build vidlink URL
        if media_type == "tv":
            vidlink_url = f"https://vidlink.pro/api/b/tv/{encrypted}/{season}/{episode}"
        else:
            vidlink_url = f"https://vidlink.pro/api/b/movie/{encrypted}"

        # Fetch stream data
        data = requests.get(vidlink_url, headers=HEADERS, timeout=15).json()

        # Try to extract stream URL from common response shapes
        stream_url = (
            data.get("url") or
            data.get("stream") or
            data.get("source") or
            (data.get("sources") or [{}])[0].get("file") or
            None
        )

        return jsonify({
            "encrypted_id": encrypted,
            "vidlink_url": vidlink_url,
            "url": stream_url,
            "raw": data
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)