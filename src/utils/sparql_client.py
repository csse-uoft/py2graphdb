import re
import requests
import urllib

POST = 'POST'
GET = 'GET'


class SPARQLResponse:
    def __init__(self, response: requests.Response, is_update=False):
        self.response = response
        self.is_update = is_update
        if response.status_code >= 400:
            raise ValueError(f'{response.status_code}: {response.text}')

    def json(self):
        if self.is_update:
            return
        return self.response.json()


class SPARQLWrapper:
    # https://www.w3.org/TR/rdf-sparql-query/#rPN_CHARS_BASE
    PN_CHARS_BASE = r"[A-Z]|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]" \
                    r"|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]" \
                    r"|[\uFDF0-\uFFFD]|[\U00010000-\U000EFFFF]"
    PN_CHARS_U = PN_CHARS_BASE + r"|_"
    PN_CHARS = PN_CHARS_U + r"|-|[0-9]|\u00B7|[\u0300-\u036F]|[\u203F-\u2040]"
    PN_PREFIX = f'({PN_CHARS_BASE})(({PN_CHARS}|\\.)*({PN_CHARS}))?'
    PNAME_NS = f'({PN_PREFIX})?:'
    IRI_REF = r'<([^<>\"{}|^`\]\[\x00-\x20])*>'
    PrefixDecl = re.compile(f'[Pp][Rr][Ee][Ff][Ii][Xx]\\s({PNAME_NS})\\s({IRI_REF})')

    @staticmethod
    def is_update_request(query_string):
        """
        Get the sparql query type: 'select' or 'update'.
        This is required for the sparql endpoint.
        """
        # Remove prefixes
        query_string = re.sub(re.compile(SPARQLWrapper.PrefixDecl), '', query_string)
        # Remove comments
        query_string = re.sub(r'^\s*#.*$', '', query_string, flags=re.MULTILINE)


        # Trim the query
        query_string = query_string.strip()
        if re.match(r'^(select|construct|describe|ask)', query_string, re.IGNORECASE):
            return False
        else:
            return True

    def __init__(self, endpoint, is_update=False):
        self.endpoint = endpoint
        self.is_update = is_update
        self.username = None
        self.password = None
        self.method = 'POST'
        self.session = None
        self._query = None

    def set_method(self, method):
        self.method = method

    def set_query(self, query):
        self._query = query

    def set_credentials(self, username, password=None):
        self.username = username
        self.password = password

    def query(self, infer=True):
        # Init session
        if self.session is None:
            self.session = requests.Session()
            if self.username:
                self.session.auth = (self.username, self.password)

        if self.method == POST:
            if self.is_update:
                response = self.session.request(self.method, self.endpoint,
                                                data=f'update={urllib.parse.quote(self._query)}',
                                                headers={
                                                    'Accept': 'text/plain',
                                                    'Content-Type': 'application/x-www-form-urlencoded'
                                                })
            else:
                response = self.session.request(self.method, self.endpoint,
                                                data=f'query={urllib.parse.quote(self._query)}&infer={"true" if infer else "false"}',
                                                headers={
                                                    'Accept': 'application/sparql-results+json',
                                                    'Content-Type': 'application/x-www-form-urlencoded'
                                                })
        elif self.method == GET:
            if self.is_update:
                raise ValueError('update operations MUST be done by POST')

            response = self.session.request(self.method, self.endpoint,
                                            params={'query': urllib.parse.quote(self._query), 'infer': "true" if infer else "false"},
                                            headers={
                                                'Accept': 'application/sparql-results+json'
                                            })
        else:
            raise ValueError('Illegal method:', self.method)

        return SPARQLResponse(response, is_update=self.is_update)


class SparqlClient:

    def __init__(self, endpoint, username=None, password=None):
        self.query_client = SPARQLWrapper(endpoint, is_update=False)
        self.update_client = SPARQLWrapper(endpoint + '/statements', is_update=True)
        if username:
            self.query_client.set_credentials(username, password)
            self.update_client.set_credentials(username, password)

    def execute_sparql(self, *query, infer=False, method=None):
        """
        Execute sparql query only without post processing
        method could be 'select', 'update', or None.
        If method is None, SparqlClient.parse_sparql_type is invoked to check SPARQL format.
        """

        # Check which client to use
        if method == 'select' or not SPARQLWrapper.is_update_request(query[0]):
            client = self.query_client
        else:
            client = self.update_client

        client.set_method(POST)
        client.set_query(';'.join(query))
        try:
            result = client.query(infer=infer).json()

            return result

        except:
            print('error with the below sparql query using ' + (
                'update client' if client == self.update_client else 'normal client'))
            print(';'.join(query).strip())
            raise
