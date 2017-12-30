import uuid
import models.users.errors  as UserErrors
from common.utils import Utils
from common.database import Database
from models.alerts.alert import Alert 
import models.users.constants as UserConstants

class User(object):
	def __init__(self, email, password, _id=uuid.uuid4().hex):
		self.email = email
		self.password = password
		self._id = _id 
	
	def __repr__(self):
		return "<User {}>".format(self.email)

	def json(self):
		return {
			"email": self.email,
			"password": self.password,
			"_id": self._id
		}

	def save(self):
		Database.insert(UserConstants.COLLECTION, self.json())


	@staticmethod
	def is_login_valid(email, password):
	# This method verifies that a email//pw combo is valid 
		user = Database.find_one(UserConstants.COLLECTION, {'email': email})
		if user:
			if Utils.check_hashed_password(password, user['password']):
				return True
			else:
				raise UserErrors.IncorrectPasswordError("wrong pw")
		else:
			raise UserErrors.UserNotExistsError("no such user")

	@classmethod
	def register_user(cls, email, password):
		if cls.find_by_email(email):
			raise UserErrors.UserExistsError("user already exists")
		if not Utils.email_is_valid(email):
			raise UserErrors.InvalidEmailError("invalid email")
		else:
			User(email, Utils.hash_password(password)).save()
			return True

	@classmethod
	def find_by_email(cls, email):
		foundUser = Database.find_one(UserConstants.COLLECTION, {'email':email})
		if foundUser:
			return cls(**foundUser)
		return None

	def get_alerts(self):
		return Alert.find_by_user_email(self.email)