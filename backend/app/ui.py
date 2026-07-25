from fastapi import Request
from fastapi.responses import HTMLResponse


HTML_PAGE = """
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>K8s Troubleshooter UI</title>
    <style>
      :root { color-scheme: dark; }
      body {
        font-family: Inter, Arial, sans-serif;
        margin: 0;
        background: #07111f;
        color: #f3f4f6;
        min-height: 100vh;
        display: grid;
        place-items: center;
      }
      .card {
        width: min(900px, 92vw);
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 20px 45px rgba(0,0,0,0.35);
      }
      h1 { margin-top: 0; }
      textarea {
        width: 100%;
        min-height: 220px;
        border-radius: 10px;
        border: 1px solid #64748b;
        background: #020617;
        color: #e2e8f0;
        padding: 12px;
        font: 14px/1.5 monospace;
        box-sizing: border-box;
      }
      button {
        margin-top: 12px;
        padding: 10px 16px;
        border: none;
        border-radius: 10px;
        background: #2563eb;
        color: white;
        cursor: pointer;
        font-weight: 600;
      }
      .result {
        margin-top: 16px;
        padding: 14px;
        border-radius: 12px;
        background: #111827;
        border: 1px solid #334155;
        white-space: pre-wrap;
      }
      .muted { color: #94a3b8; }
    </style>
  </head>
  <body>
    <div class=\"card\">
      <h1>K8s Troubleshooter</h1>
      <h3>Let's Troubleshoot The Issue !</h3>
      <p class=\"muted\">Paste pod events, error messages, or kubectl output and get a likely root cause instantly.</p>
      <textarea id=\"input\" placeholder=\"Example:\nWarning Backoff restarting failed container\nError: ImagePullBackOff\"> </textarea>
      <button onclick=\"analyze()\">Analyze</button>
      <div id=\"result\" class=\"result\">Waiting for input…</div>
    </div>

    <script>
      async function analyze() {
        const text = document.getElementById('input').value;
        const result = document.getElementById('result');
        result.textContent = 'Analyzing…';
        try {
          const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
          });
          const data = await response.json();
          result.textContent = JSON.stringify(data, null, 2);
        } catch (err) {
          result.textContent = 'Request failed: ' + err;
        }
      }
    </script>
  </body>
</html>
"""


async def ui_page(request: Request) -> HTMLResponse:
    return HTMLResponse(HTML_PAGE)
