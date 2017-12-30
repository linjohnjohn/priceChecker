from common.database import Database
import models.items.constants as ItemConstants
from models.stores.store import Store
import uuid, requests
from bs4 import BeautifulSoup
import re

class Item(object):
	def __init__(self, name, url, price=None, _id=None):
		self.name = name
		self.url = url
		store = Store.find_by_url(url)
		self.tag_name = store.tag_name
		self.query = store.query
		self.price = price
		self._id =_id or uuid.uuid4().hex

	def __repr__(self):
		return "<Item {} with URL {}>".format(self.name, self.url)

	def load_price(self):
		request = requests.get(self.url)
		content = request.content
		soup = BeautifulSoup(content, "html.parser")
		element = soup.find(self.tag_name, self.query)
		string_price = element.text.strip()

		pattern = re.compile("(\d+\.\d+)")
		match = pattern.search(string_price)
		self.price=float(match.group())

		return self.price

	def save(self):
		Database.update(ItemConstants.COLLECTION, {"_id": self._id} ,self.json())

	def json(self):
		return {
			'_id':self._id,
			'name': self.name,
			'url': self.url,
			'price': self.price
		}

	@classmethod
	def find_by_id(cls, id):
		return cls(**Database.find_one(ItemConstants.COLLECTION, {'_id': id}))

	# @classmethod
	# def find_by_name(cls, name):
	# 	foundItem = Database.find_one(ItemConstants.COLLECTION, {'name': name})
	# 	return cls(**foundItem)
