#!/usr/bin/python
import lxml
import pycurl
import StringIO
from lxml import etree
from lxml.builder import ElementMaker
from lxml.builder import E

class PennytelConException(Exception):
	def __init__(self, message, response=None):
		Exception.__init__(self, message)
		self.response = response

class PennytelCon:
	def __init__(self, username="_none_", password="_none_", connection=pycurl.Curl(), post_url="https://www.pennytel.com/pennytelapi/services/PennyTelAPI"):
		self._username = username
		self._password = password
		self._post_url = post_url
		self._connection = connection
		self._build_soap_base()

	def _post_using_over_https(self, post_data=None):
		string_s = StringIO.StringIO()
		if post_data is not None:
			self._connection.setopt(pycurl.POSTFIELDS, post_data)

		self._connection.setopt(pycurl.HTTPHEADER, ['SOAPAction:ebXML'])
		self._connection.setopt(pycurl.USERAGENT, "pennytel python bindings version 0.01")
		self._connection.setopt(pycurl.FOLLOWLOCATION, False) #Do not follow redirects.
		self._connection.setopt(pycurl.SSL_VERIFYPEER, 1)
		self._connection.setopt(pycurl.SSL_VERIFYHOST, 2)
		self._connection.setopt(pycurl.SSLVERSION, 3)
		self._connection.setopt(pycurl.WRITEFUNCTION, string_s.write)
		self._connection.setopt(pycurl.URL, self._post_url)
		self._connection.perform()
		the_page = string_s.getvalue()
		http_code = self._connection.getinfo(pycurl.HTTP_CODE)
		return http_code, the_page


	def _build_soap_base(self):
		self._base_xml = ElementMaker (
			namespace = 'http://schemas.xmlsoap.org/soap/envelope/',
			nsmap =
			{
				'xsd' : 'http://www.w3.org/2001/XMLSchema',
				'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
				'soap' : 'http://schemas.xmlsoap.org/soap/encoding/'
			}
		)

	def _send_soap_request(self):
		self._request_xml = self._base_xml.Envelope(self._base_xml.Body(self._action_specific_xml))
		post_data = etree.tostring(self._request_xml, xml_declaration=True, encoding='UTF-8', pretty_print=True)

		http_code, the_page =  self._post_using_over_https(post_data)

		if http_code != 200:
			message = "api failure, http code = " + str(http_code)
			raise PennytelConException(message, the_page)
		return the_page

	def send_sms(self, message, destination, date="2007-02-01T09:37:00"):
		self._action_specific_xml = (
			E.sendSMS (
				E.id(self._username), E.password(self._password),
				E.type('0'), E.to(destination),
				E.message(message),
				E.date(date)
			)
		)
		return self._send_soap_request()

	def trigger_callback(self, leg1, leg2, date="2007-02-01T09:37:00"):
		self._action_specific_xml = (
			E.triggerCallback (
				E.id(self._username), E.password(self._password),
				E.leg1(leg1), E.leg2(leg2),
				E.date(date)
			)
		)
		return self._send_soap_request()

	def get_contacts(self, criteria="%"):
		self._action_specific_xml = (
			E.getAddressBookEntries (
				E.id(self._username), E.password(self._password),
				E.criteria(criteria)
			)
		)
		return self._send_soap_request()

	def get_account_info(self):
		self._action_specific_xml = (
			E.getAccount (
				E.id(self._username), E.password(self._password)
			)
		)
		return self._send_soap_request()

def main():
	penny = PennytelCon("bob", "jane")
	print penny.send_sms("hi", "123123")
	print penny.trigger_callback("123", "456")
	print penny.get_contacts()

if __name__ == "__main__":
	main()

