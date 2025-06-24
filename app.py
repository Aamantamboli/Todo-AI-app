from flask import Flask, render_template, request, redirect
from transformers import pipeline

app = Flask(__name__)

# Sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# In-memory to-do list (for now)
tasks = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("task")
        if content:
            sentiment = sentiment_analyzer(content)[0]  # {'label': 'POSITIVE', 'score': 0.99}
            tasks.append({
                "content": content,
                "completed": False,
                "sentiment": sentiment["label"]
            })
        return redirect("/")

    return render_template("index.html", tasks=tasks)

@app.route("/complete/<int:task_id>")
def complete(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]["completed"] = True
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    if 0 <= task_id < len(tasks):
        del tasks[task_id]
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
