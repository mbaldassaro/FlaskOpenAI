
from flask import Flask, request, render_template, session, redirect, url_for
import pandas as pd
import openai
import chardet
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize GPT-3 API
openai.api_key = 'OPENAI_API_KEY'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']
            file.seek(0)

            try:
                df = pd.read_csv(file, encoding=encoding)
            except Exception as e:
                return f"Failed to read the CSV file: {e}", 400

            session['dataframe'] = df.to_json()
            return redirect(url_for('preview_data'))
    return render_template('upload.html')

@app.route('/preview', methods=['GET'])
def preview_data():
    if 'dataframe' not in session:
        return redirect(url_for('upload_file'))

    df = pd.read_json(session['dataframe'])
    data_html = df.head().to_html()
    return render_template('preview.html', table=data_html)

@app.route('/interact', methods=['GET', 'POST'])
def interact_with_data():
    if 'dataframe' not in session:
        return redirect(url_for('upload_file'))
    
    messages = session.get('chat_history', [])
    
    if request.method == 'POST':
        user_input = request.form['query']
        messages.append({"role": "user", "content": user_input})

        # Prepare a summary or key data points from the dataset
        df = pd.read_json(session['dataframe'])
        data_summary = f"Here is a summary of the data: {df.describe().to_string()}"  # Customize this line based on how you want to summarize or represent your data

        # Include the data summary in the conversation with GPT-3
        messages.append({"role": "system", "content": data_summary})

        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        chat_response = completion.choices[0].message.content        
        messages.append({"role": "assistant", "content": chat_response})
        session['chat_history'] = messages

        return render_template('interact.html', answer=chat_response, query=user_input)
    
    return render_template('interact.html', answer=None)

if __name__ == '__main__':
    app.run(debug=True)



"""
messages = [
    {"role": "system", "content": "You're an election observation expert with experience from The Carter Center"}
]

while True:
    content = input("You: ")
    messages.append({"role": "user", "content": content})

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    chat_response = completion.choices[0].message.content
    print(f'ChatGPT: {chat_response}')
    messages.append({"role": "assistant", "content": chat_response})
"""