from flask import Flask

app = Flask(__name__)

@app.route('/test01')
def test01():
    test01 = "test01"
    return test01

if __name__ == "__main__":
    app.run()
