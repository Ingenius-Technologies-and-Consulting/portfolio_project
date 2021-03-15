class APIError(Exception):
    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
    	if self.message:
    		return 'API Error {}'.format(self.message)
    	else:
    		return 'API Error'
