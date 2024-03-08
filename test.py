from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def replay():
    return render_template('replay1.html')

if __name__ == '__main__':
    app.run(debug=True)
