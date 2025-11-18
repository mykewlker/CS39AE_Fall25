Steam Games Analysis Portfolio

A multi-page Streamlit application that serves as both a professional data analyst portfolio and an interactive analytics dashboard. This app explores a dataset of Steam games to uncover insights about pricing, genre popularity, and user reception, demonstrating skills in Python, data visualization, and dashboard design.

Author:

Anthony Myke Walker

LinkedIn: https://www.linkedin.com/in/mykalmotivation/

Email: mykewlker@gmail.com


App Navigation Overview:

This application is divided into four main sections:

Professional Bio: A concise overview of my professional background, core competencies, and technical skills.

EDA Gallery: A static Exploratory Data Analysis gallery featuring four distinct charts with detailed "How to Read" guides and my observations on the data.

Interactive Dashboard: A dynamic dashboard that allows users to filter the dataset by genre, price, review scores, and estimated owners to explore trends and find specific games.

Future Works: An outline of planned features, such as Sentiment Analysis on user reviews and Predictive Modeling for game success.

Dataset Information

Source: Steam Games Dataset on Kaggle

Size: 2,000 records (Sampled from the full dataset)

Preprocessing & Cleaning:

Missing Values: NaN values in key numerical columns (price, metacritic_score, pct_pos_total, num_reviews_total, average_playtime_forever) were filled with 0 to allow for accurate calculations.

Type Conversion: String representations of lists (e.g., ['Action', 'Indie']) in the genres and categories columns were parsed into usable Python lists.

Platform Data: Boolean columns for windows, mac, and linux support were converted to integers (1/0) for visualization purposes.

Ownership Parsing: The estimated_owners column (formatted as ranges like "20000 - 50000") was parsed to extract the lower bound integer for quantitative analysis.

Ethics Note: This dataset consists of public game metadata and aggregated review statistics. No private individual user data is included.

Requirements

All Python dependencies are listed in the requirements.txt file.

To run this project locally, install the requirements:

pip install -r requirements.txt


Key Libraries:

streamlit: For the web application framework.

pandas: For data manipulation and cleaning.

altair: For declarative statistical visualizations.



AI Assistance Acknowledgment

This project was developed with the assistance of an AI language model (Google Gemini). The AI was used for code generation, debugging error traces, and drafting documentation text, while the project structure, data insights, and final logic were reviewed and curated by the author.
