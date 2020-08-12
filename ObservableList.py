class ObservableList:
	def __init__(self, initial_value=[]):
		self._value = initial_value
		self._callbacks = []

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, new_value):
		old_value = self._value
		self._value = new_value
		self.notify_observers()

	def notify_observers(self):
		for callback in self._callbacks:
			callback()

	def register_callback(self, callback):
		print("adding" + str(callback))
		self._callbacks.append(callback)
