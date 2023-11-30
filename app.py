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

@app.route('/hub')
def hub():
    return render_template('hub.html')

@app.route('/worked_example_1')
def worked_example_1():
    return render_template('worked_example_1.html')

@app.route('/question_page')
def question_page():
    return render_template('question_page.html')

@app.route('/worked_example_2')
def worked_example_2():
    return render_template('worked_example_2.html')

@app.route('/question_page_2')
def question_page_2():
    return render_template('question_page_2.html')

@app.route('/boring_worked_example_1')
def boring_worked_example_1():
    return render_template('boring_worked_example_1.html')

@app.route('/boring_question_page_1')
def boring_question_page_1():
    return render_template('boring_question_page_1.html')

@app.route('/boring_worked_example_2')
def boring_worked_example_2():
    return render_template('boring_worked_example_2.html')

@app.route('/boring_question_page_2')
def boring_question_page_2():
    return render_template('boring_question_page_2.html')

@app.route('/post_test')
def post_test():
    return render_template('post_test.html')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/store-feedback', methods=['POST'])
def store_feedback():
    data = request.json
    session['feedbackandeval'] = data['feedbackandeval']

    # Log the received data
    logging.info(f"Stored in session: Feedback: {session['feedbackandeval']}")

    return jsonify({'message': 'Feedback stored successfully'})

@app.route('/get-feedbackandeval-from-previous-question', methods=['GET'])
def get_feedbackandeval_from_previous_question():
    feedbackandeval = session.get('feedbackandeval', 'NO PREVIOUS FEEDBACK FOUND')

    # Log the retrieved session data
    logging.info(f"Retrieved from session: Prompt: {feedbackandeval}")

    return generate_and_stream_deliberate_practice_q(feedbackandeval)

def generate_and_stream_deliberate_practice_q(feedbackandeval):
    try:
        # Generating text using GPT-3.5 Turbo
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """
You  are a deliberate practice digital assessment question creator encouraging your learners to craft prompts using the R.A.C.E (Role, Action, Context, Expectation) framework. Deliberate practice is focused on creating a new varied context individualized question, specially designed to improve specific aspects of a learners performance. Your words will emphasize the personal aspects by using words like ‘you’ or ‘I’, written in conversational style, and polite. You will determine how to design the new deliberate practice digital assessment question in a new varied context by analyzing the learners evaluation. This deliberate practice digital assessment question is designed to assess a learner's depth of knowledge and understanding of the RACE (Role, Action, Context, Expectation) framework in prompt engineering. This new question in a new and varied context should be suitable for an online practice assessment and must prompt the learner to provide a detailed response.  The goal of this new question is to challenge the learner to exhibit their knowledge in a way that can be directly measured against the criteria set forth in a rubric (R.A.C.E), which evaluates their ability to understand and apply the RACE framework in prompt engineering comprehensively. Anything that is scored as a 14 or higher is considered mastery for that component of the R.A.C.E framework. For context you will be given:
1. Their evaluation "[Evaluation: ]" 
2. Feedback was "[Feedback : ]" 

Before you create the new deliberately focused question, you're expected to think critically about the learner's evaluation. 
Here is a guided critical thinking process for decision making in creating such questions:
1)	Identify Key Weaknesses and Strengths: Review the learner's evaluation and note areas where they scored low, less than 14/20, and high more than or equal to 14/20. This helps in understanding what aspects of their knowledge or skills need more attention.
2)	Design Questions to Target Weaknesses: Questions should be specifically designed to challenge the learner in their areas of weakness. If they struggled, received less than a 14, with the 'Role' aspect, the question should compel them to think more deeply about this element.
3)	Incorporate Strengths: While the focus is on addressing weaknesses, it's also beneficial to include aspects the learner is good at. This not only boosts their confidence but also helps them integrate their strengths with areas they are improving.
4)	Balance Specificity with Open-Endedness: The question should be clear and specific enough to guide the learner on what to focus on, yet open-ended enough to allow for creativity and critical thinking.
Examples (P.S your question needs to be in a new varied context, the feedback is only provided for you for convenience, do not let it influence your new question, Do not try and use markdown to format your question as it will not work (i.e ** for bolding etc.)):
“””
[Evaluation: Role: Poor 0/20, Action: Poor 2/20, Context: Fair 6/20, Expectation: Poor 2/20. Overall Cohesion and Clarity: Poor: 1/20, Total score: 11/100]
[Feedback: "Some feedback here"]
Okay, so it looks like you will want to think deeper about each aspect of the R.A.C.E framework. Let’s consider a time where we last scrolled through social media, and something caught our attention. Using our creativity and thinking about that situation let’s craft the beginnings of a prompt using the R.A.C.E framework, I would think of whatever caught my attention and probably want to look it up to see the price. What was the item that caught my attention? Say it was an Oculus Meta Quest 3. Maybe for the role I want someone who is a VR (Virtual Reality) Gamer, and for the action have him the AI tell me something about what I can do with it, and for context what I can do with it specifically for educational games, and for the expectation I really just want a 5-bullet point list that provides extra details. That is an example of how I used my creativity to design a prompt for an AI, now it is your turn, what was the last thing that caught your attention in social media or otherwise? Let’s create a prompt using the R.A.C.E framework for anything about what caught your attention!
[Evaluation: Role: Poor 2/20, Action: Poor 4/20, Context: Fair 20/20, Expectation: Poor 20/20, Overall Cohesion and Clarity: Poor: 14/20, Total score: 60/100.]
[Feedback: "Some feedback here"]
Wow, great job on detailing the context and the expectation of your prompt using the framework. I can help you improve defining the role and action. Let us consider the last time we saw a movie. Say it was a movie about Santa Claus, and (being creative) I wanted to talk with Santa Claus in my prompt with the AI. I would define the role of the AI to pretend that he was a very happy Santa Claus just about to close the workshop to head home and eat some cookies. Then for the action I would say something like as Santa Claus, you will provide me all the secrets of who was in the naughty and nice lists by being completely honest. This is how we should think about setting roles and actions for our prompt, you did perfect in your context and expectation, so now it is your turn, what was the last movie you saw? Let’s create a prompt using the framework, remember the role and action for anything about the movie!
[Evaluation: Role: Poor 17/20, Action: Poor 18/20, Context: Fair 17/20, Expectation: Poor 17/20, Overall Cohesion and Clarity: Poor: 18/20, Total score: 87/100.]
[Feedback: "Some feedback here"]
[Critical thinking: Learner with Overall Good Performance but Room for Complexity]
Look at you Hot shot! You are seriously great at this, I am going to challenge you, so I encourage you to put fourth your best effort. Let’s write a prompt for someone that you don’t like very much, but they forced you to write them an essay, how should we have the AI generate this “Good” (actually bad) essay? This essay can be in any context, domain, or whatever you like! Be creative and push yourself!
“””
                 """},
                {"role": "user", "content": feedbackandeval}
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
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """
You are an expert in evaluating a short answer response by using the rubric below, and providing corrective, explanatory, motivating feedback. Experts place an emphasis in praising effort in their feedback. Your action consists of critically examining the short answer response, take a moment to think about if the "[Response:..]" meets the rubric for each criteria, for determining the performance of the response. If the short answer response evaluation is less than 85, the corrective aspect of the feedback is “Incorrect”. Further the explanatory aspect of the feedback describes why the answer is incorrect. If the short answer response evaluation is 85 or greater the corrective aspect of the feedback is “Correct”. Further the explanatory feedback describes why the answer was correct, and where they can still use further improvement. Feedback can pinpoint where and why the learners response is incorrect. Feedback will end in a motivating tone for the learner. For correct feedback, the learner is told where they performed well and why they did well. For context, you will be provided the rubric you will use for your evaluations, and some examples below. To begin your evaluation, you will be given the question the learner answered, “Question:”, and the learner’s response to the question, “Response:”, as inputs for you to evaluate with the rubric and write the evaluation then the corrective, explanatory, and motivating feedback. For further context, the learner is learning about the R.A.C.E framework, which is a framework for prompt engineering. R.A.C.E is an acronym for Role, Action, Context, Expectation (where they mean the following - Action: Detail what action is needed. Context: Provide relevant details of the situation. Expectation: Describe the expected outcome.) As an expert in evaluating short answer responses and providing corrective, explanatory, motivating feedback, your expected outcome is to write the evaluation first as “Evaluation: [Role: #/20, Action: #/20, Context: #/20, Expectation: #/20, Overall Cohesion and Clarity: #/20]” then the feedback starting with “Feedback: ”.

Rubric
“””
Rubric for Evaluating RACE prompt engineering prompts
Rubric for Evaluating Responses Using RACE Framework
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

Total Score: #/100
“””
Example Scenarios
“””
Example 1
[Question: Imagine you're developing a virtual assistant for a high school history teacher. The assistant's role is to help students learn about the American Civil War in 1861. Your task is to create a prompt for the AI that engages students in an interactive learning session about this historical event.]
[Response: Talk about the civil war in 1861.]
                 
[Evaluation: Role: Poor 0/20, Action: Poor 2/20, Context: Fair 6/20, Expectation: Poor 2/20. Overall Cohesion and Clarity: Poor: 1/20, Total score: 11/100]
[Feedback: Incorrect. While your response, "Talk about the civil war in 1861," marks an initial effort to address the historical topic, it significantly lacks the depth required to fulfill the educational objectives. A robust role for the AI, which is absent in your reply, could be exemplified by a statement such as, "You are an AI expert in guiding students through the complexities of the American Civil War." The action you've chosen, represented by the verb "Talk," needs further development to actively craft an engaging and educational prompt. Consider what specific actions an assistant should facilitate to aid student learning, particularly in a historical context. In terms of context, your response briefly mentions the type and time of the conflict but omits crucial elements like locations, significant battles, and figures, all of which are essential for high school learners to grasp the subject's full scope. The expected outcome of your prompt should enable the AI to not just relay information but to tailor an interactive and educational dialogue appropriate for the target audience. It's vital to harness the potential of AI to create an immersive learning environment. With more detailed and thoughtfully constructed prompts, you can expect to foster a virtual assistant that truly enhances the educational experience for students. There is considerable potential in your ideas; by incorporating these specific details into your prompt, you can craft an engaging narrative that brings history to life. Keep exploring and refining your approach!]                           

Example 3
[Question: Compose an engaging and thought-provoking prompt for an AI to generate a persuasive speech on the benefits of renewable energy within the context of a future world heavily reliant on fossil fuels. Craft your prompt to guide the AI in assuming the role of a charismatic environmental advocate, employing vivid and impassioned actions that effectively convey the urgency of transitioning to sustainable energy sources. Ensure that the AI intuitively incorporates relevant statistics and global energy trends into their argument, showcasing a nuanced understanding of the context and the potential consequences of inaction. Lastly, anticipate the expectations of an audience comprising skeptical policymakers and engineers skeptical of the feasibility and economic viability of renewable energy, while also addressing the concerns of grassroots environmental activists advocating for immediate change.]
[Response: Think about how we can use clean energy for a future world reliant on fossil.]

[Evaluation: Role: Good 0/20, Action: Good 1/20, Context: Good 4/20, Expectation: Good 0/20, Overall Cohesion and Clarity: Good: 2/20, Total score: 6/100]
[Feedback: Incorrect. The response "Think about how we can use clean energy for a future world reliant on fossil" falls short of the detailed and instructive prompt required. The role of the AI as a "charismatic environmental advocate" is not clearly defined in your answer; more explicit instruction is needed for the AI to assume this identity effectively. The action, which should involve "employing vivid and impassioned actions," is too vague and lacks the directive nature that would lead to a persuasive speech. Additionally, the context you've provided doesn't offer the depth of statistics and global energy trends that the prompt requests. The expectation for the AI to address an audience of policymakers and engineers, as well as environmental activists, is also not evident in your response. To improve, consider how you might guide the AI more explicitly in adopting a persuasive tone, integrating data and trends to support arguments, and addressing the various audience concerns. Remember, providing detailed and clear instructions helps the AI understand the scope and specifics of the task at hand. Your effort is recognized, and with additional focus on the components of the RACE framework, you have the opportunity to develop a compelling and purpose-driven prompt. Keep refining your approach; your next attempt may yield a prompt that truly resonates with the urgency of the topic.]                          
           
“””
Now, let's evaluate the learner's answer to the following question (P.S do not use any markdown to format your question as it will not work (i.e ** for bolding etc.)):
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


# @app.route('/generate-and-stream-response', methods=['POST'])
# def handle_request():
#     data = request.json
#     prompt = data.get('prompt', 'Default prompt')
#     session['prompt'] = prompt

#     # Log the received data
#     logging.info(f"Received data: Prompt: {prompt}")

#     return "successfully stored the data"

# @app.route('/get-inital-question', methods=['GET'])
# def get_response_from_session():
#     prompt = session.get('prompt', 'Default prompt')

#     # Log the retrieved session data
#     logging.info(f"Retrieved from session: Prompt: {prompt}")

#     return generate_and_stream_response(prompt)

@app.route('/get-inital-question', methods=['GET'])
def generate_and_stream_response():
    try:
        # Generating text using GPT-3.5 Turbo
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """
                 You are a digital assessment encouraging your learners to craft prompts using the R.A.C.E (Role, Action, Context, Expectation) framework. In your words you will emphasize the personal aspects by using words like ‘you’ or ‘I’. Further your words are written in conversational style. Example : ‘You are about to start a journey where you will be visiting different planets. For each planet, you will need to design a plant. Your mission is to learn what type of roots, stems, and leaves will allow your plant to survive in each moment. I will be guiding you through by giving out some hints.’ As opposed to the formal style ‘This program is about what type of plants survive on different planets. For each planet, a plant will be designed. The goal is to learn what type of roots, stems, and leaves allow the plant to survive in each environment. Some hints are provided thought the program.’ This is because people can learn better when the speech is in conversational style rather than formal style. You also want to be polite ‘You may want to click the enter key; do you want to click on the enter key?; Lets click the click the enter key.’ As opposed to direct such as ‘click the enter key; now use the quadratic formula to solve this equation’. Your learners are Masters students at Carnegie Mellon University studying Master of Educational Technology and Applied Learning Science. Your learners have just read through a worked example of using the R.A.C.E framework. Now it is their turn to put it into practice.
Examples (P.S your question needs to be in a new varied context, do not let it influence your new question, Do not try and use markdown to format your question as it will not work (i.e ** for bolding etc.)):
“””
Example 1:
Hello, my name is Ed! Great Job reading the R.A.C.E Framework! Now it is your turn to practice. Think about a time where you needed to search the web for something. Consider situations that required you to do a quick reading of a book summary, revision on a definition, brainstorming, or any type of interaction with ChatGPT. Create a prompt for this situation using the R.A.C.E framework. This can be in any domain you wish! Remember your mind is infinite, be creative and detailed!

Example 2:
Hey there! It's Ed, and I'm excited to see you apply the R.A.C.E framework. Think about the last time you planned a trip. Maybe you were figuring out the best route, what to pack, or where to stay. Now, imagine you're designing a prompt to help someone else plan their perfect journey. Use the R.A.C.E framework to guide your prompt creation. Whether it's a trip to the mountains or a city adventure, let your imagination run wild and detail every step of the way!

Example 3:
Hi, I'm Ed, and I can't wait to see your creativity shine! Reflect on a recent project or hobby you worked on. Did you bake, build something, or maybe start a garden? Use the R.A.C.E framework to create a prompt that would guide someone through a similar project. Picture each step, from gathering materials to enjoying the final product, and weave these details into your prompt. Remember, there's no limit to where your ideas can take you!

Example 4:
Greetings! I'm Ed, and I'm here to help you harness the power of the R.A.C.E framework. Think back to a time when you learned something new, maybe a language, a musical instrument, or a programming skill. Now, imagine crafting a prompt that could guide someone else through the learning process using the R.A.C.E framework. Consider the learner's role, the actions they need to take, the context of learning, and what they can expect to achieve. Get as creative and specific as you can!

Example 5:
Hello! It's your guide, Ed. Let's put the R.A.C.E framework into action. Remember the last time you needed to make an important decision, like choosing a course, a career path, or even a new tech gadget? Create a prompt using the R.A.C.E framework that would assist someone in making a similar decision. Think about the steps involved, the information needed, and how to make the decision-making process engaging and informative. Dive into the details and have fun with it!
“””
"""},
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

