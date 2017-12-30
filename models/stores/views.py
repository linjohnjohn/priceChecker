from flask import Blueprint, render_template, request, url_for, redirect
from models.stores.store import Store
import models.users.decorators as user_decorators
import json

store_blueprint = Blueprint('stores', __name__)

@store_blueprint.route('/')
def index():
	stores = Store.all()
	return render_template('stores/store_list.html', stores=stores)

@store_blueprint.route('/new', methods=["GET", "POST"])
@user_decorators.requires_admin
def create_store():
	if request.method == "POST":
		name = request.form['name']
		url_prefix = request.form['url_prefix']
		tag_name = request.form['tag_name']
		query = json.loads(request.form['query'])
		Store(name, url_prefix, tag_name, query).save()
		return redirect(url_for('.index'))
	return render_template('stores/create_store.html')

@store_blueprint.route('/edit/<string:store_id>', methods=["GET", "POST"])
@user_decorators.requires_admin
def edit_store(store_id):
	if request.method == "POST":
		name = request.form['name']
		url_prefix = request.form['url_prefix']
		tag_name = request.form['tag_name']
		query = json.loads(request.form['query'])
		store = Store(name, url_prefix, tag_name, query, store_id)
		store.save()
		return redirect(url_for('.store_page', store_id=store_id))

	return render_template('stores/edit_store.html', store=Store.find_by_id(store_id))

@store_blueprint.route('/delete/<string:store_id>')
@user_decorators.requires_admin
def delete_store(store_id):
	Store.find_by_id(store_id).delete()
	return redirect(url_for('.index'))


@store_blueprint.route('/store/<string:store_id>')
def store_page(store_id):
	return render_template('stores/store.html', store=Store.find_by_id(store_id))

