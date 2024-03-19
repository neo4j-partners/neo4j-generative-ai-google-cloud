mgr_info_tpl="""From the text below, extract the following as json. Do not miss any of these information.
* The tags mentioned below may or may not namespaced. So extract accordingly. Eg: <ns1:tag> is equal to <tag>
* "name" - The name from the <name> tag under <filingManager> tag
* "street1" - The manager's street1 address from the <com:street1> tag under <address> tag
* "street2" - The manager's street2 address from the <com:street2> tag under <address> tag
* "city" - The manager's city address from the <com:city> tag under <address> tag
* "stateOrCountry" - The manager's stateOrCountry address from the <com:stateOrCountry> tag under <address> tag
* "zipCode" - The manager's zipCode from the <com:zipCode> tag under <address> tag
* "reportCalendarOrQuarter" - The reportCalendarOrQuarter from the <reportCalendarOrQuarter> tag under <address> tag
* Just return me the JSON enclosed by 3 backticks. No other text in the response

Text:
$ctext
"""

filing_info_tpl = """From the text below, extract the following as a list of json enclosed by 3 back ticks. You will find many filing information under the <infoTable> tag. Extract all of them.
* The tags mentioned below may or may not namespaced. So extract accordingly. Eg: <ns1:tag> is equal to <tag>
* "nameOfIssuer" - The name from the <nameOfIssuer> tag under <infoTable> tag
* "cusip" - The cusip from the <cusip> tag under <infoTable> tag
* "value" - The value from the <value> tag under <infoTable> tag
* "sshPrnamt" - The sshPrnamt from the <sshPrnamt> tag under <infoTable> tag
* "sshPrnamtType" - The sshPrnamtType from the <sshPrnamtType> tag under <infoTable> tag
* "investmentDiscretion" - The investmentDiscretion from the <investmentDiscretion> tag under <infoTable> tag
* "votingSole" - The votingSole from the <votingSole> tag under <infoTable> tag
* "votingShared" - The votingShared from the <votingShared> tag under <infoTable> tag
* "votingNone" - The votingNone from the <votingNone> tag under <infoTable> tag

Text:
$ctext
"""