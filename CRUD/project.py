from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/<int:restaurant_id>/new/', methods=["GET", "POST"])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template("newmenuitem.html", restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:MenuID>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, MenuID):
    editedItem = session.query(MenuItem).filter_by(id = MenuID).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            session.add(editedItem)
            session.commit()
            flash("Menu Item has been edited")
            return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        #USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, MenuID = MenuID, item = editedItem)

@app.route('/restaurant/<int:restaurant_id>/<int:MenuID>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, MenuID):
    deletedItem = session.query(MenuItem).filter_by(id = MenuID).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Menu Item has been deleted")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        #USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template('deletemenuitem.html', restaurant_id = restaurant_id, item = deletedItem)

# Making an API Endpoint (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:MenuID>/JSON')
def restaurantItemJSON(restaurant_id, MenuID):
    item = session.query(MenuItem).filter_by(id=MenuID).one()
    return jsonify(MenuItem=item.serialize)
    
if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.debug = True
    app.run(host = '', port = 5000)