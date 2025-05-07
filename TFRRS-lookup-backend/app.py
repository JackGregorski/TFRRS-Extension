from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def search_tfrrs_by_name_only(athlete_name):
    session = requests.Session()

    # Step 1: Load homepage to get authenticity token
    homepage = session.get("https://www.tfrrs.org", headers=HEADERS)
    soup = BeautifulSoup(homepage.text, "html.parser")
    token_input = soup.find("input", {"name": "authenticity_token"})

    if not token_input:
        print("❌ Could not find authenticity token.")
        return None

    auth_token = token_input["value"]

    # Step 2: Submit the search form
    payload = {
        "authenticity_token": auth_token,
        "athlete": athlete_name,
        "team": "",
        "meet": ""
    }
    response = session.post("https://www.tfrrs.org/search.html", data=payload, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    athlete_links = soup.select("a[href^='/athletes/']")

    if not athlete_links:
        print("❌ No athlete results found for:", athlete_name)
        return None

    first_url = "https://www.tfrrs.org" + athlete_links[0]["href"]
    print("✅ Found athlete link:", first_url)
    return first_url

def get_top_marks(athlete_url):
    response = requests.get(athlete_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    marks_table = soup.select_one("table#all_bests")
    if not marks_table:
        print("❌ Could not find marks table.")
        return []

    rows = marks_table.select("tr")
    top_marks = []

    for row in rows[:3]:  # Take the first 3 performances
        cells = [td.get_text(strip=True) for td in row.select("td")]
        if cells:
            top_marks.append(" | ".join(cells))

    print("Top marks found:", top_marks)
    return top_marks


@app.route("/tfrrs_lookup", methods=["GET"])
def tfrrs_lookup():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    try:
        profile_url = search_tfrrs_by_name_only(name)
        if not profile_url:
            return jsonify({"error": f"Athlete '{name}' not found"}), 404

        top_marks = get_top_marks(profile_url)
        return jsonify({
            "name": name,
            "url": profile_url,
            "top_marks": top_marks
        })
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
