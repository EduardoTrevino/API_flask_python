from flask import Flask, render_template, request, jsonify
import openai
import os
from flask import session, redirect

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
### This isssue was tested and will not be a probelem, the next thing to test is if the context of the question, pasted as a prompt if it can understan
### TO work around the issue of having to give context of the question that the user is responding we may need to have
### Three diffrent webpages, each with the same general prompt, but with the context of the different questions, and load the embedded link accordingly.
### This approach would require us to save the context of the question, user response, and the generated response in a database, or a datastructure.
# Set your OpenAI API key here
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/name_submission', methods=['GET', 'POST'])
def name_submission():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('name_submission.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('content')
    question_message = request.json.get('question')
    # Retrieve the username from the session
    username = session.get('username', 'Guest')
    # try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "The learner is going through a course and answering open-ended questions. You are helping a learner, by providing feedback to those open ended questions. The learner is going through a course were they learn how to respond to a student who has recently made an error, in a way that increases engagement and motivation. The course is structured by presenting scenario 1, then research after scenario 1 on how they(the learner) should respond to students, then the learner is asked open ended questions about that research after scenario 1, finally the learner is shown scenario 2. I will now provide context (in cased in single parantheses ex.'context') the learner is reading as he goes throuh the aformentioned structure in the course. This context will help you provide the feedback that is appropriate to what the learner has just read. In scenario 1 the learner is told, 'You are a tutor to a student, Aaron, who has a long history of struggling with math. Aaron is not particularly motivated to learn math. He just finished a math problem adding a 3-digit and 2-digit number and has made a common mistake (118+18=126, forgot to carry the 1).'. In the research after Scenario 1 the learner is told :'Studies have shown that the way tutors intervene or respond when students make mistakes or show misconceptions in their learning can affect the students motivation to learn. Asking students to try and correct their own mistakes before you help them is a great practice. For this reason, the recommended way of responding to Aaron's mistake would be: \"I appreciate your effort. Lets try solving the problem together. Can you tell me what you did first?\" In addition, it is best to respond indirectly and not to explicitly point out the students mistake by asking leading questions such as, Can you tell me what you did first? Having students find their own mistakes is a powerful approach for three reasons: It helps students recognize easy mistakes on their own, such as making a typo or doing basic math operations incorrectly. Oftentimes, once a student looks at their work again, they will find the obvious error themselves. A students ability to recognize their own errors increases their motivation to learn. It helps students to develop critical thinking skills. The ability to recognize their own errors fosters independent learning skills. It involves students in the learning process and gives students ownership of their learning. It is important to note that you do not want students to get too frustrated. Sometimes students may not have the prior knowledge or ability to find their own mistakes. When a student tries and fails to find their own mistake, coaches should be more explicit by giving the correct answer and support behind it. When responding to students making mistakes or errors it is important to praise the student for putting forth the effort, also called praising for effort. Praising for effort gives students positive emotions even after making a mistake or getting a problem wrong. Praising students for effort and encouraging them to continue trying builds resilience and increases their motivation to learn, In Scenario two the learner reads: ' A student named Jedidiah. He is having trouble solving a math problem. He just finished adding a 3-digit and 2-digit number and has made a common mistake. (213+47=683, didnt line up the number appropriately)'. Now that you have the context to which the leaner has read, you can provide feedback to the learner. To do so every question the learner is asked will begin with \"Question:\" The question will provide enough context for you to understand where they are in the structured course. Then the learner\'s response to the question will always begin with \"The learner response (learners name):\". The learner\'s response will be the answer to the question that was asked. Finally, you will provide feedback to the learner by responding to the learner\'s response. The feedback you provide will be the answer to the question that was asked, and an example (when applicable) to how the learner should respond where the example starts with a \" quote and ends with a \" quote. Assume your feedback starts with \"Green:\", if the learners response is correct, \"Yellow:\", if the learners response is somewhat correct but missing key ideas, or \"Red:\", if the learners response is incorrect."},
            {"role": "user", "content": "Question:" + question_message},  # Include the question message in the API request
            {"role": "user", "content": f"The learner response (The learners name is {username}):" + user_message}
          ]
        )
    assistant_message = response.choices[0].message['content']
    return jsonify(content=assistant_message)
    # except Exception as e:
    #     return jsonify(error=str(e)), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

