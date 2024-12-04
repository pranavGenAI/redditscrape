import praw
import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
st.set_page_config(page_title="Reddit Scraper", page_icon=">", layout="wide")
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
spacer, col = st.columns([5, 1])  
with col:  
	st.image('https://www.vgen.it/wp-content/uploads/2021/04/logo-accenture-ludo.png', width = 120)

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
        Reddit Scraper Tool - Extract Posts and Comments!
    </p>
""", unsafe_allow_html=True)
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
        post_data = {"Title": post.title, "Comments": []}

        # Fetch comments for the post
        post.comments.replace_more(limit=0)  # Avoid "Load more comments" links
        for comment in post.comments.list():  # Iterate through all comments
            post_data["Comments"].append(comment.body)

        posts_data.append(post_data)
    
    return posts_data

# Streamlit UI components
col1, col2, col3 = st.columns([1,1,1])
# Input for subreddit and number of posts
with col1:
	subreddit_name = st.text_input("Enter Subreddit Name (e.g., BenefitsAdviceUK):", "BenefitsAdviceUK")
	num_posts = st.number_input("Enter Number of Posts to Retrieve:", min_value=1, max_value=100, value=10)

# Button to scrape and display data
if st.button("Submit"):
    if subreddit_name:
        # Fetch data
        st.write(f"Fetching data from r/{subreddit_name}...")
        data = fetch_data(subreddit_name, num_posts)

        # Convert to DataFrame
        posts_df = pd.DataFrame(columns=["Title", "Comments"])
        all_comments = []  # List to store all comments for word cloud

        for post in data:
            for comment in post["Comments"]:
                posts_df = posts_df.append({"Title": post["Title"], "Comments": comment}, ignore_index=True)
                all_comments.append(comment)  # Add each comment to list for word cloud

        # Display data in Streamlit
        st.write(posts_df)

        # Generate WordCloud without stopwords
        stopwords = set(STOPWORDS)  # Built-in stopwords
        text = " ".join(all_comments)  # Combine all comments into a single string

        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            stopwords=stopwords,  # Remove common stopwords
            max_words=200,        # Limit to top 200 words
            colormap='viridis',   # Use a color map for better aesthetics
            contour_color='black', 
            contour_width=2       # Add contour to the word cloud
        ).generate(text)

        # Display the word cloud
        st.subheader("Word Cloud of Comments (without stopwords)")
        plt.figure(figsize=(8, 8), facecolor=None)
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

        # Save DataFrame to Excel
        excel_file = "reddit_data.xlsx"
        posts_df.to_excel(excel_file, index=False)

        # Provide download link
        with open(excel_file, "rb") as f:
            st.download_button("Download Excel File", f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("Please enter a valid subreddit name.")
