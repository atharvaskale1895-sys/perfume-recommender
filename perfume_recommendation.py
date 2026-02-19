import re
import streamlit as st
from typing import TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AURA Fragrance AI",
    page_icon="💎",
    layout="wide"
)

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg,#f3e7ff,#ffffff,#ece6ff,#f7edff);
    background-size: 400% 400%;
    animation: gradient 12s ease infinite;
}
@keyframes gradient {
  0% {background-position:0% 50%;}
  50% {background-position:100% 50%;}
  100% {background-position:0% 50%;}
}

.main-title {
    text-align:center;
    font-size:48px;
    font-weight:bold;
    color:#4B0082;
}

.card {
    background: rgba(255,255,255,0.85);
    padding:20px;
    border-radius:15px;
    box-shadow:0px 8px 20px rgba(0,0,0,0.1);
    margin-bottom:15px;
}

.stButton>button {
    background:#4B0082;
    color:white;
    border-radius:10px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- STATE ----------------
class PerfumeState(TypedDict):
    messages: List[HumanMessage | AIMessage]
    gender: str
    fragrance_type: str
    sweat_level: int
    perfume_strength: int
    preferred_scents: str
    occasion: str
    budget: str
    skin_type: str
    additional_notes: str
    recommendation: str


# ---------------- LLM ----------------
llm = ChatGroq(
    temperature=0,
    groq_api_key="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    model_name="llama-3.3-70b-versatile"
)

# ---------------- PROMPT ----------------
perfume_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """
You are a professional perfume recommendation assistant.

Rules:
- Recommend 6 to 8 perfumes.
- Only suggest perfumes commonly available on Amazon India or Flipkart.
- Keep output SHORT.

Format EXACTLY like:

1. Perfume Name
Price: ₹...
Notes: ...
Best For: ...

"""),
    ("human",
     """Gender: {gender}
Fragrance Type: {fragrance_type}
Sweat Level: {sweat_level}
Perfume Strength: {perfume_strength}
Preferred Scents: {preferred_scents}
Occasion: {occasion}
Budget: {budget}
Skin Type: {skin_type}
Additional Notes: {additional_notes}
""")
])

# ---------------- HELPERS ----------------
def process_optional_inputs(state):
    state["preferred_scents"] = state["preferred_scents"] or "fresh"
    state["additional_notes"] = state["additional_notes"] or "none"
    return state


def create_recommendation(state):
    response = llm.invoke(
        perfume_prompt.format_messages(
            gender=state["gender"],
            fragrance_type=state["fragrance_type"],
            sweat_level=state["sweat_level"],
            perfume_strength=state["perfume_strength"],
            preferred_scents=state["preferred_scents"],
            occasion=state["occasion"],
            budget=state["budget"],
            skin_type=state["skin_type"],
            additional_notes=state["additional_notes"],
        )
    )
    return response.content


# ---------------- PARSER ----------------
def parse_perfumes(text):
    pattern = r"\d+\.\s*(.*?)\nPrice:\s*(.*?)\nNotes:\s*(.*?)\nBest For:\s*(.*?)(?=\n\d+\.|\Z)"
    return re.findall(pattern, text, re.S)


# ---------------- MAIN APP ----------------
def main():

    st.markdown("<div class='main-title'>💎 AURA Fragrance AI</div>",
                unsafe_allow_html=True)
    st.write("### Professional AI Perfume Recommendation System")

    if "state" not in st.session_state:
        st.session_state.state = PerfumeState(
            messages=[],
            gender="Male",
            fragrance_type="EDT",
            sweat_level=5,
            perfume_strength=5,
            preferred_scents="",
            occasion="Casual",
            budget="Moderate",
            skin_type="Normal",
            additional_notes="",
            recommendation=""
        )

    st.markdown("## 🧴 Personal Preferences")

    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("Gender", ["Male","Female","Unisex"])
        fragrance_type = st.selectbox(
            "Fragrance Type",
            ["EDT (Light)", "EDP (Strong)", "Parfum (Very Strong)"]
        )
        sweat_level = st.slider("Sweat Level",1,10,5)
        preferred_scents = st.text_input("Preferred Scents")
        budget = st.selectbox("Budget",["Low","Moderate","High","Luxury"])

    with col2:
        perfume_strength = st.slider("Perfume Strength",1,10,5)
        occasion = st.selectbox("Occasion",
                                ["Casual","Formal","Evening","Work","Date"])
        skin_type = st.selectbox("Skin Type",
                                 ["Normal","Oily","Dry","Sensitive"])
        additional_notes = st.text_area("Additional Notes")

    if st.button("✨ Get Recommendations"):

        st.session_state.state.update({
            "gender": gender,
            "fragrance_type": fragrance_type,
            "sweat_level": sweat_level,
            "perfume_strength": perfume_strength,
            "preferred_scents": preferred_scents,
            "occasion": occasion,
            "budget": budget,
            "skin_type": skin_type,
            "additional_notes": additional_notes,
        })

        state = process_optional_inputs(st.session_state.state)

        recommendation = create_recommendation(state)

        st.markdown("## 🎯 Recommended Perfumes")

        perfumes = parse_perfumes(recommendation)

        if not perfumes:
            st.warning("Could not parse output correctly.")
            st.write(recommendation)
            return

        # ---- DISPLAY CARDS ----
        for name, price, notes, best in perfumes:

            amazon = f"https://www.amazon.in/s?k={name.replace(' ','+')}"
            flipkart = f"https://www.flipkart.com/search?q={name.replace(' ','+')}"

            st.markdown(f"""
            <div class="card">
            <h3>🧴 {name}</h3>
            <p><b>💰 Price:</b> {price}</p>
            <p><b>🌸 Notes:</b> {notes}</p>
            <p><b>⭐ Best For:</b> {best}</p>
            <p>
            <a href="{amazon}" target="_blank">🟠 Amazon</a> |
            <a href="{flipkart}" target="_blank">🔵 Flipkart</a>
            </p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
