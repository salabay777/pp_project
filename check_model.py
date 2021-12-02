from all_func.dbmodel import Session, User, Moderator, Article, State, UpdatedArticle

session = Session()

user = User(user_id = 1, username = "Oliver", firstname = "Orest", lastname = "Chukla", email="Orest_chukla@ukr.net", password = "1234")
moderator = Moderator(moderator_id = 1, moderatorname = "Admin", firstname = "Test", lastname = "Test", email="admin@ukr.net", password = "1234", moderatorkey = "1234")
article = Article(article_id = 1, name = "For school", body = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.", version = 1)
article2 = Article(article_id = 2, name = "For school2", body = "Lorem ipвфівфівіфdфadssum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.", version = 1)
state = State(state_id = 1, name = "Approved")
updated_article = UpdatedArticle(updated_article_id = 1, article_id = 1, user_id = 1, moderator_id = 1, state_id = 1, article_body = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.", date = "2021-07-10")

session.add(user)

session.add(moderator)

session.add(article)
session.add(article2)

session.add(state)

session.add(updated_article)

session.commit()

session.close()
