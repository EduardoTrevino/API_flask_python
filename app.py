from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = "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"

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
