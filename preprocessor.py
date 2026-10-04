import re
import pandas as pd


def preprocess(data):

    # WhatsApp format:
    # [10/10/25, 3:03:33 PM] Sathvika: Hey hi

    pattern = r'\[(\d{1,2}/\d{1,2}/\d{2}),\s*(\d{1,2}:\d{2}:\d{2}\s*[AP]M)\]\s*'

    parts = re.split(pattern, data)

    dates = []
    users = []
    messages = []

    # First item before the first message is ignored
    i = 1

    while i < len(parts) - 2:

        date = parts[i]
        time = parts[i + 1]
        message_text = parts[i + 2]

        full_date = date + ", " + time

        # Separate user and message
        match = re.match(r'([^:]+):\s*(.*)', message_text, re.DOTALL)

        if match:
            user = match.group(1).strip()
            message = match.group(2).strip()
        else:
            # System message
            user = "group_notification"
            message = message_text.strip()

        dates.append(full_date)
        users.append(user)
        messages.append(message)

        i += 3

    # Create DataFrame
    df = pd.DataFrame({
        'user': users,
        'message': messages,
        'date': dates
    })

    # Convert date column
    df['date'] = pd.to_datetime(
        df['date'],
        format='%m/%d/%y, %I:%M:%S %p'
    )

    # Remove system notifications
    df = df[df['user'] != 'group_notification']

    # Reset index
    df = df.reset_index(drop=True)

    # Create additional columns

    df['only_date'] = df['date'].dt.date

    df['year'] = df['date'].dt.year

    df['month_num'] = df['date'].dt.month

    df['month'] = df['date'].dt.month_name()

    df['day'] = df['date'].dt.day

    df['day_name'] = df['date'].dt.day_name()

    df['hour'] = df['date'].dt.hour

    df['minute'] = df['date'].dt.minute

    # Create time period
    period = []

    for hour in df['hour']:

        if hour == 23:
            period.append("23-00")

        elif hour == 0:
            period.append("00-01")

        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df