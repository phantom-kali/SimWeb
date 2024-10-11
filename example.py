from application import Application, Response
import os

# Ensure the templates directory exists
if not os.path.exists('templates'):
    os.makedirs('templates')

app = Application()

@app.route('/')
def home(request):
    return Response(app.render_template('home.html'))

@app.route('/api/data', methods=['GET', 'POST'])
def api_data(request):
    if request.method == 'GET':
        return Response.json({'message': 'This is GET data', 'query_params': request.query_params})
    elif request.method == 'POST':
        json_data = request.get_json()
        return Response.json({'message': 'This is POST data', 'received_data': json_data})

@app.route('/hello')
def hello(request):
    name = request.query_params.get('name', ['World'])[0]
    return Response.html(f'<h1>Hello, {name}!</h1>')

if __name__ == '__main__':
    app.run()