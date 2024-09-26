import streamlit as st
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle
from google.auth.transport.requests import Request

# Authenticate and create a calendar instance
def authenticate_google_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    calendar_service = build('calendar', 'v3', credentials=creds)
    return calendar_service

# Display existing events in a table
def display_events(calendar_service):
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = calendar_service.events().list(calendarId='nikki617@bu.edu', timeMin=now,
                                                    maxResults=10, singleEvents=True,
                                                    orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        st.write('No upcoming events found.')
        return []

    event_data = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_data.append({
            'id': event['id'],
            'Summary': event['summary'],
            'Start': start,
            'Location': event.get('location', 'N/A'),
            'Description': event.get('description', 'N/A'),
            'Attendees': ', '.join([attendee['email'] for attendee in event.get('attendees', [])]),
            'Link': event.get('htmlLink')
        })
    
    # Create a DataFrame to display as a table
    st.table(event_data)
    return event_data  # Return event data for selection

# Main function
def main():
    st.title("Google Calendar Management")

    # Authenticate and create a calendar instance
    calendar_service = authenticate_google_calendar()

    # Display calendar below forms
    st.subheader("Your Google Calendar")
    public_calendar_url = "https://calendar.google.com/calendar/embed?src=nikki617%40bu.edu&ctz=America%2FNew_York"
    st.markdown(f'<iframe src="{public_calendar_url}" style="border: 0; width: 100%; height: 600px;" frameborder="0"></iframe>', unsafe_allow_html=True)

    # Display existing events and capture data for selection
    st.subheader("Existing Events")
    event_data = display_events(calendar_service)

    # Form to show details of the selected event
    st.subheader("Event Details")
    if event_data:
        selected_event_summary = st.selectbox("Select an Event", [event['Summary'] for event in event_data])
        
        if selected_event_summary:
            # Fetch details of the selected event
            selected_event = next(event for event in event_data if event['Summary'] == selected_event_summary)
            st.write(f"### Summary: {selected_event['Summary']}")
            st.write(f"**Start:** {selected_event['Start']}")
            st.write(f"**Location:** {selected_event['Location']}")
            st.write(f"**Description:** {selected_event['Description']}")
            st.write(f"**Attendees:** {selected_event['Attendees']}")
            st.markdown(f"[Event Link]({selected_event['Link']})")

if __name__ == "__main__":
    main()
