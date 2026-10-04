import streamlit as st
import preprocessor
import helper

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import emoji

from collections import Counter
from wordcloud import WordCloud


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Whatsapp Chat Analyzer",
    layout="wide"
)

st.title("Whatsapp Chat Analyzer")


# ============================================================
# UPLOAD FILE
# ============================================================

uploaded_file = st.file_uploader(
    "Choose a WhatsApp chat file",
    type=["txt"]
)


if uploaded_file is not None:

    # --------------------------------------------------------
    # READ CHAT
    # --------------------------------------------------------

    bytes_data = uploaded_file.getvalue()

    data = bytes_data.decode(
        "utf-8",
        errors="replace"
    )

    # --------------------------------------------------------
    # PREPROCESS
    # --------------------------------------------------------

    df = preprocessor.preprocess(data)

    # --------------------------------------------------------
    # USER LIST
    # --------------------------------------------------------

    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()

    user_list.insert(
        0,
        "Overall"
    )

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    st.sidebar.title("Whatsapp Chat Analyzer")

    selected_user = st.sidebar.selectbox(
        "Show analysis wrt",
        user_list
    )

    show_analysis = st.sidebar.button(
        "Show Analysis"
    )

    if show_analysis:

        # ====================================================
        # FILTER DATA
        # ====================================================

        if selected_user != "Overall":

            analysis_df = df[
                df['user'] == selected_user
            ].copy()

        else:

            analysis_df = df.copy()


        # ====================================================
        # WHATSAPP CHAT SUMMARY
        # ====================================================

        st.header("WHATSAPP CHAT SUMMARY")

        total_messages = len(analysis_df)

        total_users = df['user'].nunique()

        total_words = sum(
            len(str(message).split())
            for message in analysis_df['message']
        )

        first_date = analysis_df['date'].min()

        last_date = analysis_df['date'].max()


        st.write(
            f"**Total Messages :** {total_messages}"
        )

        st.write(
            f"**Total Users :** {total_users}"
        )

        st.write(
            f"**Total Words :** {total_words}"
        )

        st.write(
            f"**First Date :** "
            f"{first_date.strftime('%d-%m-%Y')}"
        )

        st.write(
            f"**Last Date :** "
            f"{last_date.strftime('%d-%m-%Y')}"
        )


        # ====================================================
        # USER MESSAGE COUNT
        # ====================================================

        st.header("USER MESSAGE COUNT")

        user_count = (
            analysis_df['user']
            .value_counts()
            .reset_index()
        )

        user_count.columns = [
            "User",
            "Number of Messages"
        ]

        st.dataframe(
            user_count,
            use_container_width=True,
            hide_index=True
        )


        # USER MESSAGE GRAPH

        fig, ax = plt.subplots(
            figsize=(8, 4)
        )

        ax.bar(
            user_count["User"],
            user_count["Number of Messages"]
        )

        ax.set_xlabel("User")

        ax.set_ylabel("Number of Messages")

        ax.set_title("User Message Count")

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()

        st.pyplot(fig)


        # ====================================================
        # MONTHLY MESSAGE COUNT
        # ====================================================

        # ====================================================
        # MONTHLY MESSAGE COUNT
        # ====================================================

        st.header("MONTHLY MESSAGE COUNT")

        # Create a separate Year-Month column
        analysis_df["Year-Month"] = analysis_df["date"].dt.to_period("M").astype(str)

        # Count messages for each month
        monthly_display = (
            analysis_df["Year-Month"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        monthly_display.columns = [
            "Year-Month",
            "Number of Messages"
        ]

        # Show table
        st.dataframe(
            monthly_display,
            use_container_width=True,
            hide_index=True
        )

        # Monthly graph
        fig, ax = plt.subplots(
            figsize=(10, 4)
        )

        ax.plot(
            monthly_display["Year-Month"],
            monthly_display["Number of Messages"],
            marker="o"
        )

        ax.set_xlabel("Year-Month")

        ax.set_ylabel("Number of Messages")

        ax.set_title("Monthly Message Count")

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()

        st.pyplot(fig)
        # ====================================================
        # DAILY MESSAGE COUNT
        # ====================================================

        st.header("DAILY MESSAGE COUNT")

        daily = (
            analysis_df
            .groupby(
                analysis_df['date'].dt.date
            )
            .size()
            .reset_index(name="Number of Messages")
        )

        daily.columns = [
            "Date",
            "Number of Messages"
        ]

        daily["Date"] = pd.to_datetime(
            daily["Date"]
        ).dt.strftime(
            "%d-%m-%Y"
        )

        st.dataframe(
            daily,
            use_container_width=True,
            hide_index=True
        )


        # DAILY GRAPH

        daily_dates = pd.to_datetime(
            daily["Date"],
            format="%d-%m-%Y"
        )

        fig, ax = plt.subplots(
            figsize=(12, 4)
        )

        ax.plot(
            daily_dates,
            daily["Number of Messages"]
        )

        ax.set_xlabel("Date")

        ax.set_ylabel("Number of Messages")

        ax.set_title("Daily Message Count")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        st.pyplot(fig)


        # ====================================================
        # MESSAGES BY DAY OF WEEK
        # ====================================================

        st.header("MESSAGES BY DAY OF WEEK")

        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        day_count = (
            analysis_df["day_name"]
            .value_counts()
            .reindex(
                day_order,
                fill_value=0
            )
            .reset_index()
        )

        day_count.columns = [
            "Day",
            "Number of Messages"
        ]

        st.dataframe(
            day_count,
            use_container_width=True,
            hide_index=True
        )


        fig, ax = plt.subplots(
            figsize=(9, 4)
        )

        ax.bar(
            day_count["Day"],
            day_count["Number of Messages"]
        )

        ax.set_xlabel("Day")

        ax.set_ylabel("Number of Messages")

        ax.set_title("Messages by Day of Week")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        st.pyplot(fig)


        # ====================================================
        # MESSAGES BY HOUR
        # ====================================================

        st.header("MESSAGES BY HOUR")

        hour_count = (
            analysis_df["hour"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        hour_count.columns = [
            "Hour",
            "Number of Messages"
        ]

        st.dataframe(
            hour_count,
            use_container_width=True,
            hide_index=True
        )


        fig, ax = plt.subplots(
            figsize=(10, 4)
        )

        ax.bar(
            hour_count["Hour"],
            hour_count["Number of Messages"]
        )

        ax.set_xlabel("Hour")

        ax.set_ylabel("Number of Messages")

        ax.set_title("Messages by Hour")

        plt.tight_layout()

        st.pyplot(fig)


        # ====================================================
        # MESSAGES BY TIME PERIOD
        # ====================================================

        st.header("MESSAGES BY TIME PERIOD")


        def get_period(hour):

            if 5 <= hour < 12:
                return "Morning"

            elif 12 <= hour < 17:
                return "Afternoon"

            elif 17 <= hour < 21:
                return "Evening"

            else:
                return "Night"


        analysis_df["time_period"] = (
            analysis_df["hour"]
            .apply(get_period)
        )


        period_order = [
            "Morning",
            "Afternoon",
            "Evening",
            "Night"
        ]


        period_count = (
            analysis_df["time_period"]
            .value_counts()
            .reindex(
                period_order,
                fill_value=0
            )
            .reset_index()
        )


        period_count.columns = [
            "Time Period",
            "Number of Messages"
        ]


        st.dataframe(
            period_count,
            use_container_width=True,
            hide_index=True
        )


        fig, ax = plt.subplots(
            figsize=(8, 4)
        )

        ax.bar(
            period_count["Time Period"],
            period_count["Number of Messages"]
        )

        ax.set_xlabel("Time Period")

        ax.set_ylabel("Number of Messages")

        ax.set_title("Messages by Time Period")

        plt.tight_layout()

        st.pyplot(fig)


        # ====================================================
        # WHATSAPP ACTIVITY HEATMAP
        # ====================================================

        st.header("WHATSAPP ACTIVITY HEATMAP")

        heatmap = pd.pivot_table(
            analysis_df,
            index="day_name",
            columns="hour",
            values="message",
            aggfunc="count",
            fill_value=0
        )


        heatmap = heatmap.reindex(
            day_order,
            fill_value=0
        )


        fig, ax = plt.subplots(
            figsize=(14, 6)
        )


        sns.heatmap(
            heatmap,
            annot=True,
            fmt="g",
            cmap="Blues",
            ax=ax
        )


        ax.set_xlabel("Hours of the Day")

        ax.set_ylabel("Days of the Week")

        ax.set_title("WhatsApp Activity Heatmap")


        plt.tight_layout()

        st.pyplot(fig)


        # ====================================================
        # MOST COMMON WORDS
        # ====================================================

        st.header("MOST COMMON WORDS")


        words = []


        for message in analysis_df["message"]:

            message = str(message).lower()

            # Remove URLs

            message = re.sub(
                r'https?://\S+|www\.\S+',
                '',
                message
            )

            # Extract words

            extracted_words = re.findall(
                r'\b[a-zA-Z]+\b',
                message
            )

            words.extend(
                extracted_words
            )


        # Read stop words

        try:

            with open(
                "stop_hinglish.txt",
                "r",
                encoding="utf-8"
            ) as file:

                stop_words = set(
                    file.read().splitlines()
                )

        except FileNotFoundError:

            stop_words = set()


        common_stop_words = {
            "the",
            "is",
            "am",
            "are",
            "was",
            "were",
            "a",
            "an",
            "and",
            "or",
            "to",
            "of",
            "in",
            "on",
            "for",
            "with",
            "this",
            "that",
            "it",
            "i",
            "you",
            "he",
            "she",
            "we",
            "they",
            "me",
            "my",
            "your",
            "our",
            "at",
            "be",
            "have",
            "has",
            "had",
            "do",
            "did",
            "will",
            "would",
            "can",
            "could"
        }


        stop_words.update(
            common_stop_words
        )


        words = [
            word
            for word in words
            if word not in stop_words
        ]


        word_count = (
            Counter(words)
            .most_common(20)
        )


        common_words_df = pd.DataFrame(
            word_count,
            columns=[
                "Word",
                "Number of Occurrences"
            ]
        )


        st.dataframe(
            common_words_df,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # WORD CLOUD
        # ====================================================

        st.header("WORD CLOUD")


        wordcloud_text = " ".join(
            words
        )


        if wordcloud_text.strip():

            wc = WordCloud(
                width=1000,
                height=500,
                background_color="white"
            ).generate(
                wordcloud_text
            )


            fig, ax = plt.subplots(
                figsize=(12, 6)
            )


            ax.imshow(
                wc,
                interpolation="bilinear"
            )


            ax.axis("off")


            st.pyplot(fig)

        else:

            st.info(
                "No words available for Word Cloud."
            )


        # ====================================================
        # MOST USED EMOJIS
        # ====================================================

        st.header("MOST USED EMOJIS")


        emojis = []


        for message in analysis_df["message"]:

            for character in str(message):

                if emoji.is_emoji(character):

                    emojis.append(
                        character
                    )


        emoji_count = (
            Counter(emojis)
            .most_common(20)
        )


        emoji_df = pd.DataFrame(
            emoji_count,
            columns=[
                "Emoji",
                "Number of Uses"
            ]
        )


        st.dataframe(
            emoji_df,
            use_container_width=True,
            hide_index=True
        )


        if not emoji_df.empty:

            fig, ax = plt.subplots(
                figsize=(8, 5)
            )


            ax.bar(
                emoji_df["Emoji"],
                emoji_df["Number of Uses"]
            )


            ax.set_xlabel("Emoji")

            ax.set_ylabel("Number of Uses")

            ax.set_title("Most Used Emojis")


            plt.tight_layout()

            st.pyplot(fig)


        # ====================================================
        # MEDIA ANALYSIS
        # ====================================================

        st.header("MEDIA ANALYSIS")


        media_messages = analysis_df[
            analysis_df["message"]
            .str.contains(
                "Media omitted",
                case=False,
                na=False
            )
        ]


        total_media = len(
            media_messages
        )


        st.write(
            f"**Total Media Messages :** "
            f"{total_media}"
        )


        # ====================================================
        # LINK ANALYSIS
        # ====================================================

        st.header("LINK ANALYSIS")


        url_pattern = (
            r'https?://\S+|www\.\S+'
        )


        total_links = 0


        for message in analysis_df["message"]:

            links = re.findall(
                url_pattern,
                str(message)
            )

            total_links += len(links)


        st.write(
            f"**Total Links Shared :** "
            f"{total_links}"
        )


        # ====================================================
        # MOST ACTIVE USER
        # ====================================================

        st.header("MOST ACTIVE USER")


        active_users = (
            df["user"]
            .value_counts()
        )


        most_active_user = (
            active_users.idxmax()
        )


        most_active_user_count = (
            active_users.max()
        )


        st.write(
            f"**Most Active User :** "
            f"{most_active_user}"
        )


        st.write(
            f"**Messages Sent :** "
            f"{most_active_user_count}"
        )


        # ====================================================
        # MOST ACTIVE DAY
        # ====================================================

        st.header("MOST ACTIVE DAY")


        active_days = (
            analysis_df["day_name"]
            .value_counts()
        )


        most_active_day = (
            active_days.idxmax()
        )


        most_active_day_count = (
            active_days.max()
        )


        st.write(
            f"**Most Active Day :** "
            f"{most_active_day}"
        )


        st.write(
            f"**Messages :** "
            f"{most_active_day_count}"
        )


        # ====================================================
        # MOST ACTIVE HOUR
        # ====================================================

        st.header("MOST ACTIVE HOUR")


        active_hours = (
            analysis_df["hour"]
            .value_counts()
        )


        most_active_hour = (
            active_hours.idxmax()
        )


        most_active_hour_count = (
            active_hours.max()
        )


        st.write(
            f"**Most Active Hour :** "
            f"{most_active_hour:02d}:00"
        )


        st.write(
            f"**Messages :** "
            f"{most_active_hour_count}"
        )


        # ====================================================
        # FINAL CHAT SUMMARY
        # ====================================================

        st.header("FINAL CHAT SUMMARY")


        most_common_word = (
            common_words_df.iloc[0]["Word"]
            if not common_words_df.empty
            else "None"
        )


        most_used_emoji = (
            emoji_df.iloc[0]["Emoji"]
            if not emoji_df.empty
            else "None"
        )


        st.write(
            f"**Total Messages :** "
            f"{total_messages}"
        )

        st.write(
            f"**Total Users :** "
            f"{total_users}"
        )

        st.write(
            f"**Total Words :** "
            f"{total_words}"
        )

        st.write(
            f"**Total Media Messages :** "
            f"{total_media}"
        )

        st.write(
            f"**Total Links :** "
            f"{total_links}"
        )

        st.write(
            f"**Most Active User :** "
            f"{most_active_user}"
        )

        st.write(
            f"**Most Active Day :** "
            f"{most_active_day}"
        )

        st.write(
            f"**Most Active Hour :** "
            f"{most_active_hour:02d}:00"
        )

        st.write(
            f"**Most Common Word :** "
            f"{most_common_word}"
        )

        st.write(
            f"**Most Used Emoji :** "
            f"{most_used_emoji}"
        )


        # ====================================================
        # FIRST FEW MESSAGES
        # ====================================================

        st.header("FIRST FEW MESSAGES")


        first_messages = (
            analysis_df[
                [
                    "date",
                    "user",
                    "message"
                ]
            ]
            .head(10)
            .copy()
        )


        first_messages["Date"] = (
            first_messages["date"]
            .dt.strftime("%d-%m-%Y")
        )


        first_messages["Time"] = (
            first_messages["date"]
            .dt.strftime("%H:%M:%S")
        )


        first_messages = first_messages[
            [
                "Date",
                "Time",
                "user",
                "message"
            ]
        ]


        first_messages.columns = [
            "Date",
            "Time",
            "User",
            "Message"
        ]


        st.dataframe(
            first_messages,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # COMPLETED
        # ====================================================

        st.success(
            "WHATSAPP CHAT ANALYSIS COMPLETED"
        )