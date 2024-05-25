from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import os
from groq import Groq
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management

# Configure logging
logging.basicConfig(level=logging.DEBUG)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_meetup_info(location1, location2):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are Google Maps. I will give you my location and my friend's location. Find me a place where we both can hangout without both of us having to travel a lot. Tell us why we should go to this place that you are talking about. Feel free to be cretive with the answers. But make sure you are giving a place which is easier for both of us to travel to. Give me a list of places with recommendations on which cafes, restaurants, bars we can go to and what activites we can do. If people mention places which are in 2 separate cities, just make fun of them & ask them to head to the airport."
                },
                {
                    "role": "user",
                    "content": location1
                },
                {
                    "role": "user",
                    "content": location2
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        formatted_response = response.replace("\n", "<br>").replace("**", "<strong>").replace("**", "</strong>")
        logging.debug(f"Generated response: {formatted_response}")
        return response
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_meetup', methods=['POST'])
def find_meetup():
    try:
        location1 = request.form['location1']
        location2 = request.form['location2']
        response = get_meetup_info(location1, location2)
        session['response'] = response
        logging.debug(f"Stored response in session: {response}")
        print(f"Stored response in session: {response}")  # Debugging
        return jsonify({'redirect': url_for('results')})
    except Exception as e:
        logging.error(f"Error in find_meetup: {e}")
        return jsonify({'error': str(e)})

@app.route('/results')
def results():
    response = session.get('response', 'No response available')
    logging.debug(f"Retrieved response from session: {response}")
    print(f"Retrieved response from session: {response}")  # Debugging
    return render_template('results.html', response=response)

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    return jsonify({'error': 'An internal error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)