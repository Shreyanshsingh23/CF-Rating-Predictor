import streamlit as st
import requests
import math

def get_user_rating(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    response = requests.get(url).json()
    if response["status"] != "OK":
        return None
    return response["result"][0].get("rating", 1500)

def get_contest_data(contest_id, handle):
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&showUnofficial=true"
    response = requests.get(url).json()
    if response["status"] != "OK":
        return None, None, None
    
    rows = response["result"]["rows"]
    total_participants = 0
    user_rank = None

    for row in rows:
        party = row["party"]
        if party["participantType"] != "CONTESTANT":
            continue
        total_participants += 1
        member = party["members"][0]["handle"]
        if member.lower() == handle.lower():
            user_rank = row["rank"]

    return user_rank, total_participants, rows

def estimate_delta(rank, rating, total_contestants):
    expected_rank = total_contestants / (1 + math.pow(10, -(rating - 1500) / 400))
    delta = (expected_rank - rank) * 0.03
    return round(delta)

# ----------------- Streamlit UI -----------------

st.title("🔮 Codeforces Rating Predictor")
st.markdown("Predict your new Codeforces rating for any contest.")

handle = st.text_input("👤 Enter your Codeforces Handle")
contest_id = st.text_input("🏁 Enter Contest ID (e.g. 1941)")

if st.button("Predict"):
    if not handle or not contest_id:
        st.warning("Please enter both handle and contest ID.")
    else:
        with st.spinner("Fetching data..."):
            rating = get_user_rating(handle)
            rank, total_participants, _ = get_contest_data(contest_id, handle)

        if rating is None or rank is None:
            st.error("Could not retrieve contest or user data. Check inputs.")
        else:
            delta = estimate_delta(rank, rating, total_participants)
            new_rating = rating + delta

            st.success(f"✅ Prediction Complete for `{handle}`")
            st.markdown(f"**🏅 Current Rating:** `{rating}`")
            st.markdown(f"**📊 Rank:** `{rank}` out of `{total_participants}`")
            st.markdown(f"**📈 Predicted Delta:** `{delta:+}`")
            st.markdown(f"**🎯 Predicted New Rating:** `{new_rating}`")

