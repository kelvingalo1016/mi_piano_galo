import urllib.request
import ssl
import os

url = "https://raw.githubusercontent.com/rsms/inter/main/docs/font-files/Inter-Bold.ttf"
dest = "C:\\Users\\kelvin\\Documents\\Proyectos\\mi-piano-app\\raylib-app\\Inter-Bold.ttf"

try:
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=context, timeout=10) as response:
        with open(dest, 'wb') as f:
            f.write(response.read())
    print("Success! Size:", os.path.getsize(dest))
except Exception as e:
    print("Failed:", e)
