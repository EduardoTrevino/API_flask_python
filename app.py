from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)
### This isssue was tested and will not be a probelem, the next thing to test is if the context of the question, pasted as a prompt if it can understan
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
    question_message = request.json.get('question')
    # try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are helping a learner, by providing real-time feedback to open ended questions. The learner is going through a course were they learn how to respond to a student who has recently made an error, in a way that increases engagement and motivation. The course is structured by presenting scenario 1 (open ended questions here), then research after scenario 1 on how to respond, then asked for opinions about that research after scenario 1 (open ended questions here), Shown an example of Carl, how to respond to Carl, finally presented with scenario 2. In scenario 1  the learner is told, 'Imagine you are a tutor to a student, Aaron, who has a long history of struggling with math. Aaron is not particularly motivated to learn math. He just finished a math problem adding a 3-digit and 2-digit number and has made a common mistake (118+18=126, forgot to carry the 1).', Research after Scenario 1 'Studies have shown that the way tutors intervene or respond when students make mistakes or show misconceptions in their learning can affect the student’s motivation to learn. Asking students to try and correct their own mistakes before you help them is a great practice. For this reason, the recommended way of responding to Aaron's mistake would be: I appreciate your effort. Let’s try solving the problem together. Can you tell me what you did first? In addition, it is best to respond indirectly and not to explicitly point out the student’s mistake by asking leading questions such as, Can you tell me what you did first? Having students find their own mistakes is a powerful approach for three reasons: It helps students recognize easy mistakes on their own, such as making a typo or doing basic math operations incorrectly. Oftentimes, once a student looks at their work again, they will find the obvious error themselves. A student’s ability to recognize their own errors increases their motivation to learn. It helps students to develop critical thinking skills. The ability to recognize their own errors fosters independent learning skills. It involves students in the learning process and gives students ownership of their learning. It is important to note that you do not want students to get too frustrated. Sometimes students may not have the prior knowledge or ability to find their own mistakes. When a student tries and fails to find their own mistake, coaches should be more explicit by giving the correct answer and support behind it. When responding to students making mistakes or errors it is important to praise the student for putting forth the effort, also called praising for effort. Praising for effort gives students positive emotions even after making a mistake or getting a problem wrong. Praising students for effort and encouraging them to continue trying builds resilience and increases their motivation to learn', example of Carl 'A tutor is working with a student named Carl. Carl just made a common mistake on the first step of a multi-step algebra problem and does not recognize his error. He continues working on the algebra problem. The tutor stops Carl by stating, Carl, let’s stop here. I see you made a mistake on the first step. Let me show you your mistake.', how to respond to Carl 'Studies show that asking students to try and correct their own mistakes before you help them is a great practice, as it builds critical thinking skills and increases the student’s motivation to learn.  Therefore, a better response in the above situation would be: Hi Carl, I like how hard and focused you are working on this problem. Please explain to me how you approached the first step.' Scenario two, ' A student named Jedidiah. He is having trouble solving a math problem. He just finished adding a 3-digit and 2-digit number and has made a common mistake. (213+47=683, didn't line up the number appropriately'.  Given the context above provide real-time feedback, use the knowledge learned above to help guide your response to any incorrect feedback the learner responds with. The learner is asked the question below:"},
            {"role": "user", "content": question_message + "\n The learner response:"},  # Include the question message in the API request
            {"role": "user", "content": user_message}
          ]
        )
    assistant_message = response.choices[0].message['content']
    return jsonify(content=assistant_message)
    # except Exception as e:
    #     return jsonify(error=str(e)), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

