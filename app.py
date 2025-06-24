from flask import Flask, render_template, request, redirect
from textblob import TextBlob

app = Flask(__name__)

# In-memory task list
tasks = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("task")
        if content:
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
            tasks.append({
                "content": content,
                "completed": False,
                "sentiment": sentiment
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
    app.run(host="0.0.0.0", port=5000)
