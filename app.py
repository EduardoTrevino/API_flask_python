from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
import openai
import os
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from traceback import format_exc
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

openai.api_key = os.environ.get('OPENAI_API_KEY')
url = urlparse(os.environ.get('DATABASE_URL'))
url = url._replace(scheme=url.scheme.replace('postgres', 'postgresql'))
DATABASE_URL = urlunparse(url)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/worked_example_1')
def worked_example_1():
    return render_template('worked_example_1.html')

@app.route('/question_page')
def question_page():
    return render_template('question_page.html')


@app.route('/')
def home():
    return render_template('index.html')

# Front end processing
# This route will handle the POST request sent when the user submits their input. 
# It stores the question given to the user, and their response to the question in the session.
@app.route('/store-front-end-data', methods=['POST'])
def store_front_end_data():
    data = request.json
    session['questionInput'] = data['questionInput']
    session['userResponse'] = data['userResponse']

    # Log the received data
    logging.info(f"Stored in session: QuestionInput: {session['questionInput']}, UserResponse: {session['userResponse']}")

    return jsonify({'message': 'Data stored in session successfully'})

# This route will handle the GET request to send the LLM feedback and evaluation
@app.route('/send-llm-feedback-and-eval', methods=['GET'])
def send_llm_feedback_and_eval():
    question_input = session.get('questionInput', 'No user input found')
    user_response = session.get('userResponse', 'No previous response found')

    # Log the retrieved session data
    logging.info(f"Retrieved from session: UserInput: {question_input}, PreviousResponse: {user_response}")

    return llm_for_feedback_and_eval(question_input, user_response)

# Function to process with LLM and stream response
def llm_for_feedback_and_eval(question_input, user_response):
    try:
        # Generating text using GPT-3.5 Turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
You are an expert in evaluating a short answer response by using a rubric, and providing corrective, explanatory, motivating feedback. Experts place an emphasis in praising effort in their feedback. Your action consists of critically examining the short answer response by referring to the rubric for determining the performance of the response. If the short answer response evaluation is less than 85, the corrective aspect of the feedback is “Incorrect”. Further the explanatory aspect of the feedback describes why the answer is incorrect. If the short answer response evaluation is 85 or greater the corrective aspect of the feedback is “Correct”. Further the explanatory feedback describes why the answer was correct, and where they can still use further improvement. Consider that feedback is an instructional event that can pinpoint where and why the user’s response is incorrect, however it should also be motivating to the learner identifying areas where they performed well and why they did well. For context, you will be provided the rubric you will use for your evaluations, and some examples below. To begin your evaluation, you will be given the question the learner answered, “Question:”, and the learner’s response to the question, “Response:”, as inputs for you to evaluate with the rubric and write the corrective, explanatory, and motivating feedback. For further context, the learner is learning about the R.A.C.E framework, which is a framework for prompt engineering. R.A.C.E is an acronym for Role, Action, Context, Expectation (where they mean the following - Action: Detail what action is needed. Context: Provide relevant details of the situation. Expectation: Describe the expected outcome.) As an expert in evaluating short answer responses and providing corrective, explanatory, motivating feedback, your expected outcome is to write the feedback starting with “Feedback: “ then the “Evaluation: [Role: (Grade out of/20), Action: (Grade out of/20), Context: (Grade out of/20), Expectation: (Grade out of/20), Overall Cohesion and Clarity: (Grade out of/20)”

Rubric
“””
Rubric for Evaluating RACE prompt engineering prompts
1. Role (20 points)
- Excellent (16-20 points): Role is explained with sophistication, showing comprehensive understanding of AI.
- Good (11-15 points): Role is systematically defined, reflecting a good grasp of AI.
- Fair (6-10 points): Role is somewhat developed but lacks depth in understanding AI.
- Poor (0-5 points): Role is naively or inaccurately explained.

2. Action (20 points)
- Excellent (16-20 points): Actions are masterfully defined, showing excellent application skills.
- Good (11-15 points): Actions are skilled, showing competent application in context.
- Fair (6-10 points): Actions show limited but growing adaptability.
- Poor (0-5 points): Actions are novice, showing reliance on scripted skills.

3. Context (20 points)
- Excellent (16-20 points): Context is insightful and coherent, offering a thorough perspective.
- Good (11-15 points): Context is considered, showing awareness of different viewpoints.
- Fair (6-10 points): Context is aware but weak in considering the worth of each viewpoint.
- Poor (0-5 points): Context is uncritical or irrelevant.

4. Expectation (20 points)
- Excellent (16-20 points): Expectations are wise, reflecting deep self-awareness.
- Good (11-15 points): Expectations are circumspect, showing good self-awareness.
- Fair (6-10 points): Expectations are thoughtful but may lack full awareness.
- Poor (0-5 points): Expectations are unreflective or unrealistic.

5. Overall Cohesion and Clarity (20 points)
- Excellent (16-20 points): Prompt is mature, showing empathy and disciplined construction.
- Good (11-15 points): Prompt is sensitive, demonstrating an understanding of learner perspectives.
- Fair (6-10 points): Prompt shows some capacity for empathy but is limited.
- Poor (0-5 points): Prompt is egocentric, lacking empathy and clarity.

Total Score: ___ / 100
“””
Example Scenarios
“””
Example 1
[Rubric]

[Question: Imagine you're developing a virtual assistant for a high school history teacher. The assistant's role is to help students learn about the American Civil War in 1861. Your task is to create a prompt for the AI that engages students in an interactive learning session about this historical event.]
[Response: Talk about the civil war in 1861.]

[Feedback: Incorrect. While your response, "Talk about the civil war in 1861," marks an initial effort to address the historical topic, it significantly lacks the depth required to fulfill the educational objectives. A robust role for the AI, which is absent in your reply, could be exemplified by a statement such as, "You are an AI expert in guiding students through the complexities of the American Civil War." The action you've chosen, represented by the verb "Talk," needs further development to actively craft an engaging and educational prompt. Consider what specific actions an assistant should facilitate to aid student learning, particularly in a historical context. In terms of context, your response briefly mentions the type and time of the conflict but omits crucial elements like locations, significant battles, and figures, all of which are essential for high school learners to grasp the subject's full scope. The expected outcome of your prompt should enable the AI to not just relay information but to tailor an interactive and educational dialogue appropriate for the target audience. It's vital to harness the potential of AI to create an immersive learning environment. With more detailed and thoughtfully constructed prompts, you can expect to foster a virtual assistant that truly enhances the educational experience for students. There is considerable potential in your ideas; by incorporating these specific details into your prompt, you can craft an engaging narrative that brings history to life. Keep exploring and refining your approach!]
[Evaluation: Role: Poor 0/20, Action: Poor 2/20, Context: Fair 6/20, Expectation: Poor 2/20. Overall Cohesion and Clarity: Poor: 1/20, Total score: 11/100]

Example 2

[Rubric]
[Question: You are an AI assistant tasked with helping a high school student, Alex, understand the basics of the solar system for a science project]
[Response: Your role is to guide Alex in learning about the solar system. Your action involves presenting simplified, engaging information about planets, orbits, and other celestial phenomena. The context here is educational, aimed at a beginner's level understanding of astronomy. Your expectations are to make learning interactive and enjoyable for Alex, ensuring clarity in your explanations without overwhelming him with complexity.]

[Evaluation: Role: Excellent 17/20, Action: Excellent 18/20, Context: Excellent 17/20, Expectation: Excellent 18/20, Overall Cohesion and Clarity: Excellent: 18/20, Total score: 88/100]
[Feedback: Correct. Excellent effort in crafting your prompt! The response effectively delineates the role of the AI as a guide for Alex, showing a sophisticated understanding of how the AI can facilitate learning. Your action steps are well-defined, presenting the complex subject of the solar system in an engaging and simplified manner appropriate for a high school student's level. The educational context is carefully considered, maintaining the focus on beginner-friendly content while fostering an interest in astronomy. The expectations are thoughtfully set to make the learning process interactive and enjoyable, indicating a deep self-awareness of the student's educational needs. The clarity and cohesion with which you've constructed this prompt reflect a disciplined approach, demonstrating an understanding of both the learner's perspective and the educational goals. To further challenge your creativity and depth of detail, consider exploring how you might incorporate adaptive learning techniques to tailor the information to Alex’s progress. How could the AI evaluate and respond to the student’s changing understanding, and what additional resources could be integrated into the learning experience to provide a comprehensive overview of the solar system?]                             
"""},
                {"role": "user", "content": "Question: " + question_input},
                {"role": "user", "content": "Response: " + user_response}
            ],
            stream=True
        )

        # Streaming the response
        def stream_response():
            assistant_message = ""
            for chunk in response:
                if 'content' in chunk['choices'][0]['delta']:
                    assistant_message += chunk['choices'][0]['delta']['content']
                    yield chunk['choices'][0]['delta']['content']

                if 'finish_reason' in chunk['choices'][0] and chunk['choices'][0]['finish_reason'] == 'stop':
                    yield "END"

        return Response(stream_with_context(stream_response()), content_type='text/event-stream')
    
    except Exception as e:
        return str(e)


@app.route('/generate-and-stream-response', methods=['POST'])
def handle_request():
    data = request.json
    prompt = data.get('prompt', 'Default prompt')
    session['prompt'] = prompt

    # Log the received data
    logging.info(f"Received data: Prompt: {prompt}")

    return "successfully stored the data"

@app.route('/get-response-from-session', methods=['GET'])
def get_response_from_session():
    prompt = session.get('prompt', 'Default prompt')

    # Log the retrieved session data
    logging.info(f"Retrieved from session: Prompt: {prompt}")

    return generate_and_stream_response(prompt)

def generate_and_stream_response(prompt):
    try:
        # Generating text using GPT-3.5 Turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
            ],
            stream=True
        )

        # Streaming the response
        def stream_response():
            assistant_message = ""
            for chunk in response:
                if 'content' in chunk['choices'][0]['delta']:
                    assistant_message += chunk['choices'][0]['delta']['content']
                    yield chunk['choices'][0]['delta']['content']
                
                if 'finish_reason' in chunk['choices'][0] and chunk['choices'][0]['finish_reason'] == 'stop':
                    yield "END"  # Signal the end of the stream

        return Response(stream_with_context(stream_response()), content_type='text/event-stream')

    except Exception as e:
        return str(e)  # Return the error message in case of failure
    
@app.route('/get-response', methods=['POST'])
def get_response():
    
    # Get the user ID and question from the URL parameters PostgreSQL\16rc1
    user_id = request.args.get('username')
    if user_id is None:
        user_id = "default_username"  # or handle this case appropriately as per your app's requirements
    question_message = request.args.get('question')
    if question_message is None:
        question_message = "No question provided"

    
    # Get the current usage count for the user ID from the database
    user = User.query.filter_by(user_id=user_id).first()

    try:
        last_user_id_entry = LastUserID.query.first()
        if not user:
            if not last_user_id_entry:
                last_user_id = 1
                last_user_id_entry = LastUserID(last_user_id=last_user_id)
                db.session.add(last_user_id_entry)
            else:
                last_user_id = last_user_id_entry.last_user_id + 1
                last_user_id_entry.last_user_id = last_user_id
            
            user = User(user_id=str(last_user_id), usage_count=1)
            db.session.add(user)
            user_id = str(last_user_id)
            db.session.commit()
        
        # If the usage count is 3 or more, create a new user ID and reset the usage count
        elif user.usage_count > 3:
            # Increment the last used user ID
            last_user_id = last_user_id_entry.last_user_id + 1
            last_user_id_entry.last_user_id = last_user_id
            
            user = User(user_id=str(last_user_id), usage_count=1)
            db.session.add(user)
            user_id = str(last_user_id)
            db.session.commit()
        else:
            # Increment the usage count for the current user ID
            user.usage_count += 1
            db.session.commit()

        # Get the learner's response from the POST request body
        user_message = request.json.get('content')           
        def generate(user_message, question_message, user_id):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "The learner is going through a course and answering open-ended questions. You are helping a learner, by providing feedback to those open ended questions. The learner is going through a course were they learn how to respond to a student who has recently made an error, in a way that increases engagement and motivation. The course is structured by presenting scenario 1, then research after scenario 1 on how they(the learner) should respond to students, then the learner is asked open ended questions about that research after scenario 1, finally the learner is shown scenario 2. I will now provide context (in cased in single parantheses ex.'context') the learner is reading as he goes throuh the aformentioned structure in the course. This context will help you provide the feedback that is appropriate to what the learner has just read. In scenario 1 the learner is told, 'You are a tutor to a student, Aaron, who has a long history of struggling with math. Aaron is not particularly motivated to learn math. He just finished a math problem adding a 3-digit and 2-digit number and has made a common mistake (118+18=126, forgot to carry the 1).'. In the research after Scenario 1 the learner is told :'Studies have shown that the way tutors intervene or respond when students make mistakes or show misconceptions in their learning can affect the students motivation to learn. Asking students to try and correct their own mistakes before you help them is a great practice. For this reason, the recommended way of responding to Aaron's mistake would be: \"I appreciate your effort. Lets try solving the problem together. Can you tell me what you did first?\" In addition, it is best to respond indirectly and not to explicitly point out the students mistake by asking leading questions such as, Can you tell me what you did first? Having students find their own mistakes is a powerful approach for three reasons: It helps students recognize easy mistakes on their own, such as making a typo or doing basic math operations incorrectly. Oftentimes, once a student looks at their work again, they will find the obvious error themselves. A students ability to recognize their own errors increases their motivation to learn. It helps students to develop critical thinking skills. The ability to recognize their own errors fosters independent learning skills. It involves students in the learning process and gives students ownership of their learning. It is important to note that you do not want students to get too frustrated. Sometimes students may not have the prior knowledge or ability to find their own mistakes. When a student tries and fails to find their own mistake, coaches should be more explicit by giving the correct answer and support behind it. When responding to students making mistakes or errors it is important to praise the student for putting forth the effort, also called praising for effort. Praising for effort gives students positive emotions even after making a mistake or getting a problem wrong. Praising students for effort and encouraging them to continue trying builds resilience and increases their motivation to learn, In Scenario two the learner reads: ' A student named Jedidiah. He is having trouble solving a math problem. He just finished adding a 3-digit and 2-digit number and has made a common mistake. (213+47=683, didnt line up the number appropriately)'. Now that you have the context to which the leaner has read, you can provide feedback to the learner. To do so every question the learner is asked will begin with \"Question:\" The question will provide enough context for you to understand where they are in the structured course. Then the learner\'s response to the question will always begin with \"The learner response \". The learner\'s response will be the answer to the question that was asked. Finally, you will provide feedback to the learner by responding to the learner\'s response. The feedback you provide will be the answer to the question that was asked, and an example (when applicable) to how the learner should respond where the example starts with a \" quote and ends with a \" quote. Assume your feedback starts with \"Green:\", if the learners response is correct, \"Yellow:\", if the learners response is somewhat correct but missing key ideas, or \"Red:\", if the learners response is incorrect."},
                    {"role": "user", "content": "Question: " + question_message},
                    {"role": "user", "content": "The learner response: " + user_message}
                ],
                stream=True
            )
            
            assistant_message = ""
            for chunk in response:
                if 'content' in chunk['choices'][0]['delta']:
                    assistant_message += chunk['choices'][0]['delta']['content']
                    yield chunk['choices'][0]['delta']['content']
                
                if 'finish_reason' in chunk['choices'][0] and chunk['choices'][0]['finish_reason'] == 'stop':
                    # Save the interaction data in the database
                    interaction = Interaction(user_id=user_id, question=question_message, learner_response=user_message, llm_response=assistant_message, timestamp=datetime.utcnow())
                    db.session.add(interaction)
                    db.session.commit()
                    
                    yield "END"  # Signal the end of the stream
        
        return Response(stream_with_context(generate(user_message, question_message, user_id)), content_type='text/event-stream')
    
    except Exception as e:
        # Log the full error message and stack trace
        app.logger.error(format_exc())
        # Rollback the database session if an error occurs
        db.session.rollback()
        return jsonify(error=str(e)), 500
    finally:
        db.session.close()
    #return jsonify(content=assistant_message)

class LastUserID(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    last_user_id = db.Column(db.Integer, nullable=False, default=0)

class User(db.Model):
    user_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    usage_count = db.Column(db.Integer, nullable=False, default=0)

class Interaction(db.Model):
    interaction_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    question = db.Column(db.String, nullable=False)
    learner_response = db.Column(db.String, nullable=True)
    llm_response = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

