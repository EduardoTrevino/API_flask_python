from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)
### TO work around the issue of having to give context of the question that the user is responding we may need to have
### Three diffrent webpages, each with the same general prompt, but with the context of the different questions, and load the embedded link accordingly.
### This approach would require us to save the context of the question, user response, and the generated response in a database, or a datastructure.
# Set your OpenAI API key here
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('content')
    # try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
          ]
        )
    assistant_message = response.choices[0].message['content']
    return jsonify(content=assistant_message)
    # except Exception as e:
    #     return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)
