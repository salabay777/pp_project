__version__ = '0.1.0'
from flask import Flask, Response
from waitress import serve

from  all_func.moderator import moderator
from  all_func.user import user
from  all_func.state import state
from  all_func.article import article
from  all_func.updatedArticle import updatedArticle

app = Flask(__name__)
app.register_blueprint(state)
app.register_blueprint(moderator)
app.register_blueprint(user)
app.register_blueprint(article)
app.register_blueprint(updatedArticle)


@app.route('/api/v1/hello-world-5')
def myendpoint():
    return   Response(status=200, response="Hello World 5")

# session = Session()
# @app.route('/api/v1/article', methods=['POST'])
# def create_article():
#     # Get data from request body
#     data = request.get_json()

#     # Validate input data
#     try:
#         ArticleSchema().load(data)
#     except ValidationError as err:
#         return jsonify(err.messages), 400

#     # Check if article already exists
#     exists = session.query(Article.article_id).filter_by(name=data['name']).first()
#     if exists:
#         return Response(status=403, response='article with such number already exists.')

#     # Create new article
#     new_article = Article(name=data['name'], body=data['body'], version=data['version'])

#     # Add new article to db
#     session.add(new_article)
#     session.commit()

#     return Response(response='New audience was successfully created!')
serve(app, host='0.0.0.0', port=8089, threads=1)