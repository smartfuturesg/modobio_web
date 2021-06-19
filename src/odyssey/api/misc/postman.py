from flask import current_app, json, Response
from flask_restx import Resource, Namespace

ns = Namespace('postman', description='Endpoint to download a Postman collection of the API.')

@ns.route('/')
class PostmanEndpoint(Resource):
    @ns.doc(security=None)
    def get(self):
        """ Download API as a Postman collection.

        This endpoint provides a convenient way to download the entire API as a Postman collection.
        It returns a JSON file for download. That JSON file can be imported into Postman and provides
        a collection containing all endpoints in this API.
        """
        data = json.dumps(ns.apis[0].as_postman(urlvars=True, swagger=True), indent=2)

        response = Response(
            data,
            mimetype='application/json',
            direct_passthrough=True)

        version = current_app.config['API_VERSION']
        filename = f'ModoBio API v{version}.json'
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        return response
