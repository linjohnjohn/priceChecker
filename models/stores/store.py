import models.stores.constants as StoreConstants
from common.database import Database
import models.stores.errors as StoreErrors
import uuid

class Store(object):
	def __init__(self, name, url_prefix, tag_name, query, _id=None):
		self.name = name
		self.url_prefix = url_prefix
		self.tag_name =tag_name
		self.query =query
		self._id=_id or uuid.uuid4().hex

	def __repr__(self):
		return "<Store {}>".format(self.name)

	def json(self):
		return {
			'_id': self._id,
			'name': self.name,
			'url_prefix': self.url_prefix,
			'tag_name': self.tag_name,
			'query': self.query
		}	

	@classmethod
	def find_by_id(cls, id):
		return cls(**Database.find_one(StoreConstants.COLLECTION, {"_id": id}))

	def save(self):
		Database.update(StoreConstants.COLLECTION, {"_id": self._id}, self.json())

	@classmethod
	def find_by_name(cls, name):
		return cls(**Database.find_one(StoreConstants.COLLECTION, {"name": name}))

	@classmethod
	def find_by_url_prefix(cls, url_prefix):
		return cls(**Database.find_one(StoreConstants.COLLECTION, {"url_prefix": {'$regex': '^{}'.format(url_prefix)}}))

	@classmethod
	def find_by_url(cls, url):
		for i in range(len(url), -1, -1):
			if Database.find_one(StoreConstants.COLLECTION, {"url_prefix": {'$regex': '^{}'.format(url[:i])}}):
				try:
					store = cls.find_by_url_prefix(url[:i])
					if store:
						return store 
				except:
					raise StoreErrors.StoreNotFoundException("Store not found")

	@classmethod
	def all(cls):
		return [cls(**store) for store in Database.find(StoreConstants.COLLECTION, {})]

	def delete(self):
		Database.remove(StoreConstants.COLLECTION, {"_id": self._id})