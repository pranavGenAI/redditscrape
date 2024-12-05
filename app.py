import praw
import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import hashlib
from datetime import datetime, timedelta, timezone


st.set_page_config(page_title="Reddit Scraper", page_icon="🕸️", layout="wide")
background_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Underwater Bubble Background</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background: linear-gradient(45deg, #161d20 5%, #161d29 47.5%,#161d53 ,#161d52 95%);
         }
        canvas {
            display: block;
        }
    </style>
</head>
<body>
    <canvas id="bubblefield"></canvas>
    <script>
        // Setup canvas
        const canvas = document.getElementById('bubblefield');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Arrays to store bubbles
        let bubbles = [];
        const numBubbles = 100;
        const glowDuration = 1000; // Glow duration in milliseconds

        // Function to initialize bubbles
        function initializeBubbles() {
            for (let i = 0; i < numBubbles; i++) {
                bubbles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    radius: Math.random() * 5 + 2, // Adjusted smaller bubble size
                    speedX: Math.random() * 0.5 - 0.25, // Adjusted slower speed
                    speedY: Math.random() * 0.5 - 0.25, // Adjusted slower speed
                    glow: false,
                    glowStart: 0
                });
            }
        }

        // Draw function
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw bubbles
            for (let i = 0; i < numBubbles; i++) {
                let bubble = bubbles[i];

                // Calculate glow intensity based on time elapsed since glow started
                let glowIntensity = 0;
                if (bubble.glow) {
                    let elapsedTime = Date.now() - bubble.glowStart;
                    glowIntensity = 0.8 * (1 - elapsedTime / glowDuration); // Decreasing glow intensity over time
                    if (elapsedTime >= glowDuration) {
                        bubble.glow = false; // Reset glow state after glow duration
                    }
                }

                ctx.beginPath();
                ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);

                // Set glow effect if bubble should glow
                if (glowIntensity > 0) {
                    let gradient = ctx.createRadialGradient(bubble.x, bubble.y, 0, bubble.x, bubble.y, bubble.radius);
                    gradient.addColorStop(0, `rgba(255, 255, 255, ${glowIntensity})`);
                    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    ctx.fillStyle = gradient;
                } else {
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'; // Adjusted bubble transparency to 70%
                }
                
                ctx.fill();

                // Move bubbles based on speed
                bubble.x += bubble.speedX;
                bubble.y += bubble.speedY;

                // Wrap bubbles around edges of canvas
                if (bubble.x < -bubble.radius) {
                    bubble.x = canvas.width + bubble.radius;
                }
                if (bubble.x > canvas.width + bubble.radius) {
                    bubble.x = -bubble.radius;
                }
                if (bubble.y < -bubble.radius) {
                    bubble.y = canvas.height + bubble.radius;
                }
                if (bubble.y > canvas.height + bubble.radius) {
                    bubble.y = -bubble.radius;
                }
            }
            
            requestAnimationFrame(draw);
        }

        // Mouse move event listener to move bubbles towards cursor
        canvas.addEventListener('mousemove', function(event) {
            let mouseX = event.clientX;
            let mouseY = event.clientY;
            for (let i = 0; i < numBubbles; i++) {
                let bubble = bubbles[i];
                let dx = mouseX - bubble.x;
                let dy = mouseY - bubble.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 50) {
                    bubble.speedX = dx * 0.01;
                    bubble.speedY = dy * 0.01;
                    if (!bubble.glow) {
                        bubble.glow = true;
                        bubble.glowStart = Date.now();
                    }
                }
            }
        });

        // Start animation
        initializeBubbles();
        draw();

        // Resize canvas on window resize
        window.addEventListener('resize', function() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            initializeBubbles();  // Reinitialize bubbles on resize
        });
    </script>
</body>
</html>
"""

# Embed the HTML code into the Streamlit app
st.components.v1.html(background_html, height=1000)
st.markdown("""
<style>
    iframe {
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        border: none;
        height: 100%;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        @keyframes gradientAnimation {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        .animated-gradient-text {
            font-family: "Graphik Semibold";
            font-size: 30px;
            background: linear-gradient(45deg, #22ebe8 30%, #dc14b7 55%, #fe647b 20%);
            background-size: 300% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientAnimation 20s ease-in-out infinite;
        }
    </style>
    <p class="animated-gradient-text">
        Reddit Scraper Tool 🕷- Extract Posts and Comments!
    </p>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Define users and hashed passwords for simplicity
users = {
    "pranav.baviskar": hash_password("pranav123"),
    "d.l.mukherjee": hash_password("debo123")
}

def login():
    col1, col2= st.columns([0.3, 0.7])  # Create three columns with equal width
    with col1:  # Center the input fields in the middle column
        st.title("Login")
        st.write("Username")
        username = st.text_input("",  label_visibility="collapsed")
        st.write("Password")
        password = st.text_input("", type="password",  label_visibility="collapsed")
        
        if st.button("Sign in"):
            hashed_password = hash_password(password)
            if username in users and users[username] == hashed_password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()  # Refresh to show logged-in state
            else:
                st.error("Invalid username or password")

def logout():
    # Clear session state on logout
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged out successfully!")
    st.rerun()  # Refresh to show logged-out state

# Path to the logo image
logo_url = "https://www.vgen.it/wp-content/uploads/2021/04/logo-accenture-ludo.png"

# Authenticate with the Reddit API
reddit = praw.Reddit(
    client_id='M76KeSHxyDtLprwCnw-tAg',
    client_secret='eK2l-nbVzDm3eRZVgdqgF19VxK7Fxw',
    user_agent='MyRedditScraper/1.0 (by u/pranav112358)'
)

# Function to scrape subreddit data
def fetch_data(subreddit_name, num_posts):
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []

    # Fetch the latest posts based on user input (num_posts)
    for post in subreddit.new(limit=num_posts):  # Use .hot() or .top() for other categories
        post_data = {
            "Title": post.title,
            "Description": post.selftext if post.selftext else "No Description",  # Add description
            "Comments": []
        }

        # Fetch comments for the post
        post.comments.replace_more(limit=0)  # Avoid "Load more comments" links
        for comment in post.comments.list():  # Iterate through all comments
            post_data["Comments"].append(comment.body)

        posts_data.append(post_data)

    return posts_data

def fetch_data_by_date(subreddit_name, num_posts, start_date, end_date):
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []
    unique_post_ids = set()  # Set to store unique post IDs

    # Convert date to datetime with time, then to UTC timestamps
    start_datetime = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    end_datetime = datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)
    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())

    # Fetch posts and filter by date
    post_count = 0
    for post in subreddit.new(limit=None):  # Removing the limit here to handle pagination
        post_time = int(post.created_utc)  # Post creation time in UTC

        if start_timestamp <= post_time <= end_timestamp:
            # Convert post time to datetime object (timezone-aware)
            post_created_time = datetime.fromtimestamp(post_time, tz=timezone.utc)

            # Fetch comments
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                post_data = {
                    "Title": post.title,
                    "Description": post.selftext if post.selftext else "No Description",  # Add description
                    "Comment": comment.body,
                    "Created Time": post_created_time.replace(tzinfo=None)  # Remove timezone info from post created time
                }

                posts_data.append(post_data)
                unique_post_ids.add(post.id)  # Add the unique post ID to the set
                post_count += 1

                if post_count >= num_posts:
                    break  # Stop when we reach the desired number of posts

        if post_count >= num_posts:
            break  # Stop when we reach the desired number of posts

    # Print the number of unique posts extracted
    st.write(f"Number of unique posts extracted: {len(unique_post_ids)}")

    return posts_data

# Main function
def main():
    col1, col2 = st.columns(2)
    with col1:
        subreddit_name = st.text_input("Enter Subreddit Name (e.g., BenefitsAdviceUK):", "BenefitsAdviceUK")
        num_posts = st.number_input("Enter Number of Posts to Retrieve:", min_value=1, max_value=1000, value=100)

    with col2:
        # Date range inputs
        start_date = st.date_input("Start Date", datetime.now().date())
        end_date = st.date_input("End Date", datetime.now().date())

        # Validate date range
        if start_date > end_date:
            st.error("Start Date must be earlier than End Date.")

    if st.button("Submit"):
        if subreddit_name:
            st.write(f"Fetching data from r/{subreddit_name} between {start_date} and {end_date}...")
            st.markdown("""
                Create and customize your own word cloud here: 
                [WordCloud Generator](https://wordcloudgeneratorapp.streamlit.app/)
            """, unsafe_allow_html=True)
            # Fetch data with date filtering
            data = fetch_data_by_date(subreddit_name, num_posts, start_date, end_date)
            
            # Convert to DataFrame
            posts_df = pd.DataFrame(data)
            
            # Save to Excel
            excel_file = "reddit_data_filtered.xlsx"
            posts_df.to_excel(excel_file, index=False)
            
            with open(excel_file, "rb") as f:
                st.download_button(
                    "Download Excel File",
                    f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.write(posts_df)

        else:
            st.warning("Please enter a valid subreddit name.")

if __name__ == "__main__":
    if st.session_state.logged_in:
        col1, col2, col3 = st.columns([10, 10, 1.5])
        with col3:
            if st.button("Logout"):
                logout()
        main()
    else:
        login()
