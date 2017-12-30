from app import app 

app.run(port=5002, debug=app.config['DEBUG'])
