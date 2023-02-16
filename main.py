from api import init_app

app = init_app()

@app.route("/")
def home():
    return "<h1>Flask Calculator API</h1>"

#if __name__ == "__main__":
#  app.run(debug=True)