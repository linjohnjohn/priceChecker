import uuid, datetime
import requests
import models.alerts.constants as AlertConstants
from common.database import Database
from models.items.item import Item


class Alert(object):
	def __init__(self, user_email, price_limit, item_id, active=True, last_checked=datetime.datetime.utcnow(), _id=uuid.uuid4().hex):
		self.user_email = user_email
		self.price_limit = price_limit
		self.item = Item.find_by_id(item_id)
		self.last_checked=last_checked
		self._id = _id
		self.active = active

	def __repr__(self):
		return "<Alert for {} on item {} with price {}>".format(self.user_email, self.item.name, self.price_limit)

	def send(self):
		return requests.post(
			AlertConstants.URL,
			auth=('api', AlertConstants.API_KEY),
			data={
				'from': AlertConstants.FROM,
				'to': self.user_email,
				'subject': 'Price limit reached for {}'.format(self.item.name),
				'text': "We've found a deal! ({})".format(self.item.url)
			}
		)

	def json(self):
		return {
			'user_email': self.user_email,
			'price_limit': self.price_limit,
			'item_id': self.item._id,
			'last_checked': self.last_checked,
			'_id': self._id,
			'active': self.active
			}

	def save(self):
		Database.update(AlertConstants.COLLECTION, {"_id": self._id}, self.json())
	
	@classmethod
	def find_needing_update(cls, minutes_since_update=AlertConstants.ALERT_TIMEOUT):
		last_updated_limit=datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes_since_update)
		return [cls(**alert) for alert in Database.find(AlertConstants.COLLECTION, {'last_checked': {"$lte": last_updated_limit}, 'active': True})]

	def load_item_price(self):
		self.item.load_price()
		self.last_checked = datetime.datetime.utcnow()
		self.item.save()
		self.save()
		return self.item.price

	def send_email(self):
		if self.item.price < self.price_limit:
			self.send()

	@classmethod
	def find_by_user_email(cls, user_email):
		return [cls(**alert) for alert in Database.find(AlertConstants.COLLECTION, {"user_email": user_email})]

	@classmethod
	def find_by_id(cls, id):
		return cls(**Database.find_one(AlertConstants.COLLECTION, {"_id": id}))

	def deactivate(self):
		self.active=False
		self.save()

	def activate(self):
		self.active=True
		self.save()

	def delete(self):
		Database.remove(AlertConstants.COLLECTION, {"_id": self._id})