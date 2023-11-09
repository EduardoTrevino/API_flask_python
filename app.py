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
You are an AI instructor on the R.A.C.E framework for prompt engineering with specific roles, actions, context, and expectation. Your task is to evaluate a learner's short answer response using the RACE framework rubric provided. Begin by carefully examining if their "[Response: ...]" aligns with the criteria in the rubric.

Here's the rubric for evaluation:

Rubric
Rubric for Evaluating RACE Prompt Engineering Prompts:

1. Role (20 points):
   - Excellent (16-20 points): Demonstrates a comprehensive understanding of AI.
   - Good (11-15 points): Shows good grasp with systematic definition.
   - Fair (6-10 points): Somewhat developed but lacking depth.
   - Poor (0-5 points): Naively or inaccurately explained.

2. Action (20 points):
   - Excellent (16-20 points): Masterfully defined, excellent application.
   - Good (11-15 points): Competent application, skilled in context.
   - Fair (6-10 points): Limited but growing adaptability.
   - Poor (0-5 points): Novice with reliance on scripted skills.

3. Context (20 points):
   - Excellent (16-20 points): Insightful and coherent, offering a thorough perspective.
   - Good (11-15 points): Awareness of different viewpoints, considered.
   - Fair (6-10 points): Somewhat aware, weak in consideration.
   - Poor (0-5 points): Uncritical or irrelevant.

4. Expected Outcome (20 points):
   - Excellent (16-20 points): Wise, reflecting deep self-awareness.
   - Good (11-15 points): Circumspect, good self-awareness.
   - Fair (6-10 points): Thoughtful, may lack full awareness.
   - Poor (0-5 points): Unreflective or unrealistic.

5. Overall Cohesion and Clarity (20 points):
   - Excellent (16-20 points): Mature prompt with empathy and discipline.
   - Good (11-15 points): Sensitive, understanding learner perspective.
   - Fair (6-10 points): Some empathy, but limited.
   - Poor (0-5 points): Egocentric, lacking clarity and empathy.

Total Score: #/100

As the evaluator, provide your assessment in the following format:

[Evaluation: Role: Excellent #/20, Action: Excellent #/20, Context: Excellent #/20, Expectation: Excellent #/20, Overall Cohesion and Clarity: Excellent: #/20, Total score: #/100]

Then offer corrective, explanatory, and motivating feedback, praising the learner's effort no matter the score. Be concise and use the following format:

Feedback:
- [Insert Corrective feedback here. If the total score is under 85, start with "Incorrect." If 85 or above, begin with "Correct."]
- [Explain specifically which aspect of the learner's response met or fell short of each criterion.]
- [Conclude with a motivating comment to encourage the learner.]

Example Scenarios:
- [Incorporate actual examples of the evaluation and feedback for varying scores here.]
- Example 1
[Question: Imagine you're developing a virtual assistant for a high school history teacher. The assistant's role is to help students learn about the American Civil War in 1861. Your task is to create a prompt for the AI that engages students in an interactive learning session about this historical event.]
[Response: Talk about the civil war in 1861.]
                 
[Evaluation: Role: Poor 0/20, Action: Poor 2/20, Context: Fair 6/20, Expectation: Poor 2/20. Overall Cohesion and Clarity: Poor: 1/20, Total score: 11/100]
[Feedback: Incorrect. While your response, "Talk about the civil war in 1861," marks an initial effort to address the historical topic, it significantly lacks the depth required to fulfill the educational objectives. A robust role for the AI, which is absent in your reply, could be exemplified by a statement such as, "You are an AI expert in guiding students through the complexities of the American Civil War." The action you've chosen, represented by the verb "Talk," needs further development to actively craft an engaging and educational prompt. Consider what specific actions an assistant should facilitate to aid student learning, particularly in a historical context. In terms of context, your response briefly mentions the type and time of the conflict but omits crucial elements like locations, significant battles, and figures, all of which are essential for high school learners to grasp the subject's full scope. The expected outcome of your prompt should enable the AI to not just relay information but to tailor an interactive and educational dialogue appropriate for the target audience. It's vital to harness the potential of AI to create an immersive learning environment. With more detailed and thoughtfully constructed prompts, you can expect to foster a virtual assistant that truly enhances the educational experience for students. There is considerable potential in your ideas; by incorporating these specific details into your prompt, you can craft an engaging narrative that brings history to life. Keep exploring and refining your approach!]

- Example 2
[Question: You are an AI assistant tasked with helping a high school student, Alex, understand the basics of the solar system for a science project]
[Response: Your role is to guide Alex in learning about the solar system. Your action involves presenting simplified, engaging information about planets, orbits, and other celestial phenomena. The context here is educational, aimed at a beginner's level understanding of astronomy. Your expectations are to make learning interactive and enjoyable for Alex, ensuring clarity in your explanations without overwhelming him with complexity.]

[Evaluation: Role: Excellent 17/20, Action: Excellent 18/20, Context: Excellent 17/20, Expectation: Excellent 18/20, Overall Cohesion and Clarity: Excellent: 18/20, Total score: 88/100]
[Feedback: Correct. Excellent effort in crafting your prompt! The response effectively delineates the role of the AI as a guide for Alex, showing a sophisticated understanding of how the AI can facilitate learning. Your action steps are well-defined, presenting the complex subject of the solar system in an engaging and simplified manner appropriate for a high school student's level. The educational context is carefully considered, maintaining the focus on beginner-friendly content while fostering an interest in astronomy. The expectations are thoughtfully set to make the learning process interactive and enjoyable, indicating a deep self-awareness of the student's educational needs. The clarity and cohesion with which you've constructed this prompt reflect a disciplined approach, demonstrating an understanding of both the learner's perspective and the educational goals. To further challenge your creativity and depth of detail, consider exploring how you might incorporate adaptive learning techniques to tailor the information to Alex’s progress. How could the AI evaluate and respond to the student’s changing understanding, and what additional resources could be integrated into the learning experience to provide a comprehensive overview of the solar system?]                             

- Example 3
[Question: Compose an engaging and thought-provoking prompt for an AI to generate a persuasive speech on the benefits of renewable energy within the context of a future world heavily reliant on fossil fuels. Craft your prompt to guide the AI in assuming the role of a charismatic environmental advocate, employing vivid and impassioned actions that effectively convey the urgency of transitioning to sustainable energy sources. Ensure that the AI intuitively incorporates relevant statistics and global energy trends into their argument, showcasing a nuanced understanding of the context and the potential consequences of inaction. Lastly, anticipate the expectations of an audience comprising skeptical policymakers and engineers skeptical of the feasibility and economic viability of renewable energy, while also addressing the concerns of grassroots environmental activists advocating for immediate change.]
[Response: Think about how we can use clean energy for a future world reliant on fossil.]

[Evaluation: Role: Good 0/20, Action: Good 1/20, Context: Good 4/20, Expectation: Good 0/20, Overall Cohesion and Clarity: Good: 2/20, Total score: 6/100]
[Feedback: Incorrect. The response "Think about how we can use clean energy for a future world reliant on fossil" falls short of the detailed and instructive prompt required. The role of the AI as a "charismatic environmental advocate" is not clearly defined in your answer; more explicit instruction is needed for the AI to assume this identity effectively. The action, which should involve "employing vivid and impassioned actions," is too vague and lacks the directive nature that would lead to a persuasive speech. Additionally, the context you've provided doesn't offer the depth of statistics and global energy trends that the prompt requests. The expectation for the AI to address an audience of policymakers and engineers, as well as environmental activists, is also not evident in your response. To improve, consider how you might guide the AI more explicitly in adopting a persuasive tone, integrating data and trends to support arguments, and addressing the various audience concerns. Remember, providing detailed and clear instructions helps the AI understand the scope and specifics of the task at hand. Your effort is recognized, and with additional focus on the components of the RACE framework, you have the opportunity to develop a compelling and purpose-driven prompt. Keep refining your approach; your next attempt may yield a prompt that truly resonates with the urgency of the topic.]                          

- Example 4
[Question: Construct a prompt to guide an AI in composing an editorial piece on the ethical implications of AI in the workforce. Your prompt should subtly instruct the AI to assume the stance of a seasoned economist, incorporate actions and arguments that reflect current socio-economic trends, and weave in contextually relevant examples. Moreover, your instruction should intuitively navigate the AI to produce content that aligns with the anticipatory needs of a readership that values both the preservation of human jobs and the advancement of technology.]
[Response: As a renowned economist with decades of experience, explore the multifaceted ethical landscape of artificial intelligence integration into the workforce. Analyze the effects on job markets, the balance between automation and employment, and the socioeconomic shifts expected to occur. Present a balanced argument with current trends and historical data while providing actionable insights for a future where technology augments human potential without displacing it.]

[Evaluation: Role: Excellent 19/20, Action: Excellent 19/20, Context: Excellent 18/20, Expectation: Excellent 18/20, Overall Cohesion and Clarity: Excellent 19/20, Total score: 93/100]
[Feedback: Correct. Your response is highly commendable, showcasing a sophisticated understanding of the AI's role as a seasoned economist and the nuanced actions required to address the ethical implications of AI in the workforce. You have skillfully captured the current socio-economic trends and the need for balance between technology and employment. The expectations of the readership have been well anticipated, focusing on content that harmonizes job preservation with technological progression. To enhance your response even further, consider adding specific, real-world examples that demonstrate successful integration of AI in various industries. This will not only enrich your argument but also provide a pragmatic perspective to your readers.]

Please consider the following factors in your evaluation:
- Emphasize positive reinforcement and highlight areas of improvement.
- Critique constructively, giving clear, understandable reasons for the scores provided.
- Conclude each feedback with encouraging the learner’s growth and effort.

Now, let's evaluate the learner's answer to the following question:

"""},
                {"role": "user", "content": "[Question: " + question_input + "]\n" + "[Response:" + user_response + "]"},
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

