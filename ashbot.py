import streamlit as st
import ollama
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Cosmic Story Narrative Flow",
    page_icon="🌌",
    layout="centered")

USER_FILE="users.json"

#-----style-----
st.markdown("""
<style>
[data-testid="st.AppViewContainer"]{
    background: linear-gradient(to bottom, #0e1117, #1a2a6c);
    color: #ffffff;           
}  
[data-testid="stHeader"]{
    background: rgba(0,0,0,0);
            
} 
[data-tesstid="stToolbar"]{
    right: 2rem;
            
}

.stApp {
    background: radial-gradient(circle at top left, #1A1A2E, #0F0C29);
    font-family: 'Segoe UI', sans-serif;
    color: #F5F7FA;
}

           
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111122, #0A0A14);
    border-right: 10px solid rgba(130, 100, 255, 0.2);
}


section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] label {
    color: #C6B8FF ;
}

[data-testid="stChatInput"]{ 
    background: transparent;
            
}
[data-testid="stChatInput"] >div{
    background: transparent;
            }
textarea {
    background: rgba(255,255,255,0.07);
    border-radius: 20px;
    border: 1px solid rgba(130, 100, 255, 0.5);
    color: #ffffff;
}

button {
    background: linear-gradient(90deg, #7F5AF0, #2CB67D);
    color: grey ;
    border-radius: 20px ;
    border: none ;
    transition: 0.3s ease ;
}

button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(127, 90, 240, 0.6);
}
            
.stTextInput > div > div  input{
    background: rgba(255, 255,255, 0.1);
    color: #333333;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    padding: 12px;
    backdrop-filter: blur(8px);
}

.stTextInput input::placeholder{
    color: rgba(255, 255, 255, 0.6);            
} 

.stTextInput input:focus{
    box-shadow: 0 0 15px #4cc9f0;
    border: 1px solid #4cc9f0;
}
            
[data-testid="stChatMessage"] p {
    color: #ffffff            
}

   
.main.block-container{
    padding-top: 0rem;
    padding-bottom: 0rem;
    max-width: 100%;         
}
</style>
""", unsafe_allow_html=True)

#-------session state----
if "messages" not in st.session_state:
    st.session_state.messages=[
        {
            "role":"assistant",
            "content":"Hello! I am your AI story companion 🌌\nReady to explore and write your story."
        }
    ]
 
if "story_memory" not in st.session_state:
    st.session_state.story_memory = ""  

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "username" not in st.session_state:
    st.session_state.username= None

if "all_histories" not in st.session_state:
    st.session_state.all_histories={}


if "current_story_id" not in st.session_state:
    st.session_state.current_story_id = None 

if "genre_chats" not in st.session_state:
    st.session_state.genre_chats={}

#------user file func ------

def get_user_history_file():
    return f"{st.session_state.username}_history.json"

def load_user_history():
    file=get_user_history_file()   
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}
    
def save_user_history():
    file=get_user_history_file()
    with open(file, "w") as f:
        json.dump(st.session_state.all_histories, f)

def save_chat_history(title):

    if genre not in st.session_state.all_histories:
        st.session_state.all_histories[genre]=[]

    if st.session_state.current_story_id is not None:
        story=st.session_state.all_histories[genre][st.session_state.current_story_id]
        story["messages"]=st.session_state.messages.copy()
        story["memory"]=st.session_state.story_memory
        story["date"]=datetime.now().strftime("%y-%m-%d %H:%M")

    else:
        new_story={
            "title":title[:40],
            "date":datetime.now().strftime("%y-%m-%d %H:%M"),
            "messages":st.session_state.messages.copy(),
            "memory":st.session_state.story_memory
        }

        st.session_state.all_histories[genre].append(new_story)

        st.session_state.current_story_id=len(st.session_state.all_histories[genre]) - 1
    save_user_history()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

users = load_users()


#-----login -------
if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .login-box{
        width:400px;
        margin:auto;
        margin-top:150px;
        padding:40px;

        background: rgba(20,20,40,0.85);

        border-radius:20px;

        box-shadow:0px 0px 30px rgba(120,80,255,0.5);

        text-align:center;
    }

    </style>
    """, unsafe_allow_html=True)


    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.title("🌌 Cosmic Studio")
    st.caption("AI Story Generator")

    tab1, tab2 = st.tabs(["Login","Sign Up"])


    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username in users and users[username] == password:

                st.session_state.logged_in = True
                st.session_state.username=username
                st.session_state.all_histories=load_user_history()

                st.success("Welcome Back 🌙")
                st.rerun()

            else:
                st.error("Invalid login")

    with tab2:

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Create Account"):

            if new_user in users:
                st.error("Username Exists")

            elif new_user == "" or new_pass == "":
                st.error("Fill All Fields")

            else:
                users[new_user] = new_pass
                save_users(users)
                st.success("Account Created")
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

with st.sidebar:
    st.title("🌙 Studio")
    
    if st.button("👤", "Login", help="Login" ):
        st.session_state.show_login=True

    if st.session_state.get("show_login", False):
        st.subheader("Login")

    if st.session_state.logged_in:
        st.success(" Logged In")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    format = st.selectbox(
        "Story Format",
        ["Short Story", "Movie Script", "Novel","Fanfiction"]
    )
    mode = st.selectbox(
        "Mode",
        ["Word Enhancer", "Story Co-Writer", "Narrative Writer"]
    )
    genre = st.selectbox(
        "Genre",
        ["Sci-Fi", "Fantasy","Horror", "Adventure", "Thriller", "Romance"]
    )
#-------genre memory------   
if "current_genre" not in st.session_state:
    st.session_state.current_genre=genre

if genre!=st.session_state.current_genre:
    st.session_state.genre_chats[st.session_state.current_genre]={
        "messages":st.session_state.messages,
        "memory":st.session_state.story_memory
    }
    st.session_state.current_genre=genre
    if genre in st.session_state.genre_chats:
        st.session_state.messages=st.session_state.genre_chats[genre]["messages"]
        st.session_state.story_memory=st.session_state.genre_chats[genre]["memory"]
    else:
        st.session_state.messages=[
            {
                "role": "assistant",
                "content": "Hello! Continue your story🌌"
            }
        ]
        st.session_state.story_memory=""

GENRE_THEMES = {

    "Sci-Fi": """
    background: radial-gradient(circle at 50% 20%, #00111a, #000000);
    animation: stars 40s linear infinite;
    """,

    "Fantasy": """
    background: linear-gradient(270deg, #2b1055, #7597de, #2b1055);
    background-size: 400% 400%;
    animation: fantasyGlow 15s ease infinite;
    """,

    "Horror": """
    background: linear-gradient(to bottom, #000000, #220000);
    animation: horrorPulse 6s infinite;
    """,

    "Adventure": """
    background: linear-gradient(270deg, #134e5e, #71b280, #134e5e);
    background-size: 400% 400%;
    animation: adventureMove 20s ease infinite;
    """,

    "Thriller": """
    background: linear-gradient(270deg, #232526, #414345, #232526);
    background-size: 400% 400%;
    animation: thrillerShift 10s ease infinite;
    """,

    "Romance": """
    background: linear-gradient(270deg, #ff758c, #ff7eb3, #ff758c);
    background-size: 400% 400%;
    animation: romanceGlow 12s ease infinite;
    """
}

theme = GENRE_THEMES.get(genre, GENRE_THEMES["Sci-Fi"])

#-------story filter -----
def is_story_related(text):

    keywords=[
        "story","character","scene","chapter","plot","write","continue","describe","dialogue",
        "fantasy","romance","horror","scifi","adventure"
    ]

    text=text.lower()

    for word in keywords:
        if word in text:
            return True
    
    return False

#-------start new draft-----
if st.button("✨ Start New Draft"):
    if st.session_state.story_memory.strip():
        title_prompt=f"""
        Generate a short creative title(max 6 words)
        for this {genre} story:
        
        {st.session_state.story_memory}
        """
        try:
            title_response=ollama.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": title_prompt}]
            )
            title=title_response["message"]["content"].strip()

        except:
            title="Untitled Story"

        if genre not in st.session_state.all_histories:
            st.session_state.all_histories[genre]=[]

        st.session_state.all_histories[genre].append({
            "title": title,
            "date": datetime.now().strftime("%y-%m-%d %H:%M"),
            "messages": st.session_state.messages.copy(),
            "memory": st.session_state.story_memory
        })
        save_user_history()

        st.session_state.messages=[]
        st.session_state.story_memory=""

        st.rerun()


st.markdown(f"""
<style>

.stApp {{
{theme}
}}

/* Sci-Fi Stars */
@keyframes stars {{
0% {{ background-position: 0px 0px; }}
100% {{ background-position: 1000px 1000px; }}
}}

/* Fantasy Glow */
@keyframes fantasyGlow {{
0% {{background-position: 0% 50%;}}
50% {{background-position: 100% 50%;}}
100% {{background-position: 0% 50%;}}
}}

/* Horror Pulse */
@keyframes horrorPulse {{
0% {{filter: brightness(0.8);}}
50% {{filter: brightness(1.2);}}
100% {{filter: brightness(0.8);}}
}}

/* Adventure Movement */
@keyframes adventureMove {{
0% {{background-position: 0% 50%;}}
50% {{background-position: 100% 50%;}}
100% {{background-position: 0% 50%;}}
}}

/* Thriller Motion */
@keyframes thrillerShift {{
0% {{background-position: 0% 50%;}}
50% {{background-position: 100% 50%;}}
100% {{background-position: 0% 50%;}}
}}

/* Romance Glow */
@keyframes romanceGlow {{
0% {{background-position: 0% 50%;}}
50% {{background-position: 100% 50%;}}
100% {{background-position: 0% 50%;}}
}}

</style>
""", unsafe_allow_html=True)
#--------history-----

st.sidebar.subheader("📚 History")

if st.session_state.all_histories:

    for genre_name, stories in st.session_state.all_histories.items():
        with st.sidebar.expander(genre_name):
            for idx, story in enumerate(stories):
                label = f"{story['title']} ({story['date']})"
                if st.button(label, key=f"{genre_name}_{idx}"):
                    st.session_state.messages = story["messages"].copy()
                    st.session_state.story_memory = story["memory"]
                    st.session_state.current_story_id = idx
                    st.rerun()

#---------clear------
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.story_memory = ""
    st.session_state.current_story_id = None

#-----download---
if st.sidebar.button("Download Story"):
    st.sidebar.download_button(
        label="Download as TXT",
        data=st.session_state.story_memory,
        file_name="my_story.txt",
        mime="text/plain"
    )


st.markdown("<div class='text_box'>", unsafe_allow_html=True)

#------Main ui------
st.title("🌌 Cosmic Narrative Wave")
st.caption("Turn ideas into immersive stories.Imagine and enjoy the flow.")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#-----chat input -----

prompt=st.chat_input("Let your imagination begin...")

if prompt:

    if not is_story_related(prompt):

        with st.chat_message("assistant"):
            st.markdown("I can only help with **story writing**. Please provide a story idea.")

        st.stop()
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
        )
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.current_story_id is not None:
        save_chat_history(prompt)

#-----system prompt -------
base_genre_rule = f"""
    STRICT GENRE RULE:
    you must ONLY write in the {genre} genre.
    Do NOT mix genres.
"""
if mode == "Word Enhancer":
        system_prompt=f"""
    you are a professional story editor.
                       
    Improve wording and make it more expressive.

    Genre:{genre}
    Format:{format} 
    {base_genre_rule} 
story so far:
{st.session_state.story_memory}                
"""
    
elif mode == "Story Co-Writer":
        system_prompt =f"""
    You are a creative story co-writer.

    Continue the story in a immersive way.

Genre:{genre}
Format:{format}
{base_genre_rule}
story so far:
{st.session_state.story_memory}
"""
        
elif mode == "Narrative Writer":
        system_prompt=f"""
    You are a narrative storyteller.

    Write a vivid cinematic narration.
Genre:{genre}
Format:{format}
{base_genre_rule}
"""
else:
        system_prompt=f"""
        you are a cinematic storyteller.
        write a vivid narration.
        Genre:{genre}
        Format:{format}
{base_genre_rule}
        """
#------ollama response-----
if prompt:
    with st.chat_message("assistant"):
        response_box=st.empty()
        full_response=""
        
        try:
            chat_context=[
                {"role": "system", "content": system_prompt}
                ] + st.session_state.messages
            stream=ollama.chat(
                model="llama3:8b-instruct-q4_0",
                messages=chat_context,
                stream=True
            )

            for chunk in stream:
                token=chunk["message"]["content"]
                full_response += token
                response_box.markdown(full_response)

        except Exception as e:
            st.error("Ollama error:" + str(e))

        if full_response:
            st.session_state.messages.append({
                "role":"assistant",
                "content": full_response
                })
            st.session_state.story_memory += "\n" + full_response
            if prompt:
                save_chat_history(prompt)

st.markdown("</div>", unsafe_allow_html=True)