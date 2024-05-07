import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        # result = list()
        # for drink in drinks:
        #     result.append(drink.short())
        result = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': result
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        result = list()
        for drink in drinks:
            result.append(drink.long())
        return jsonify({
            'success': True,
            'drinks': result
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        if not (title and recipe):
            raise ValueError('Invalid request body')
        
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
        
        return jsonify({
            'success': True,
            'drink': [new_drink.long()]
        })
    except (KeyError, TypeError, ValueError) as e:
        print("error", e)
        return jsonify({
            'success': False,
            'error': str(e)
        })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        body = request.get_json()
        if not body:
            raise ValueError('Request doesnt have valid JSON body')
        
        drink_to_update = Drink.query.get(drink_id)
        if not drink_to_update:
            raise ValueError('No drink found')
        
        title = body.get('title')
        recipe = body.get('recipe')
        if title:
            drink_to_update.title = title
        if recipe:
            drink_to_update.recipe = json.dumps(recipe)
        drink_to_update.update()
        
        return jsonify({
            'success': True,
            'drink': drink_to_update.long()
        })
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink_to_delete = Drink.query.get(drink_id)
        if not drink_to_delete:
            raise ValueError('Drink ID {} not found'.format(drink_id))
        
        drink_to_delete.delete()
        
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except (ValueError, Exception) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Errror"
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_failed(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "Authentication Failed"
    }), 403
