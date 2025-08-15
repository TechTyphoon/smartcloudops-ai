#!/usr/bin/env python3
"""
Enterprise Authentication Endpoints
Login, logout, token refresh, user management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from app.auth import auth_manager, authenticate_user, get_user_by_id, require_auth, require_admin, ENTERPRISE_USERS

logger = logging.getLogger(__name__)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Enterprise login endpoint with JWT tokens"""
    try:
        # For GET requests, return login form info
        if request.method == "GET":
            return jsonify({
                'status': 'ready',
                'message': 'Enterprise Login Service',
                'method': 'POST',
                'required_fields': ['username', 'password'],
                'test_users': {
                    'admin': 'Enterprise administrator',
                    'operator': 'System operator', 
                    'viewer': 'Read-only access',
                    'analyst': 'Data analyst'
                },
                'endpoint': '/auth/login',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'JSON data required',
                'status': 'error'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'error': 'Invalid credentials', 
                'message': 'Username and password required',
                'status': 'error'
            }), 400
        
        # Authenticate user
        user = authenticate_user(username, password)
        if not user:
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid username or password',
                'status': 'error'
            }), 401
        
        # Generate tokens
        tokens = auth_manager.generate_tokens(
            user_id=user['id'],
            username=user['username'],
            role=user['role'],
            tenant_id=user.get('tenant_id')
        )
        
        logger.info(f"Successful login for user: {username} (role: {user['role']})")
        
        return jsonify({
            'message': 'Login successful',
            'status': 'success',
            'data': {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role'],
                    'email': user.get('email'),
                    'tenant_id': user.get('tenant_id')
                },
                'tokens': tokens
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'error': 'Login failed',
            'message': 'Internal server error',
            'status': 'error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth()
def logout():
    """Enterprise logout with token revocation"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            auth_manager.revoke_token(token)
        
        logger.info(f"User logged out: {request.user['username']}")
        
        return jsonify({
            'message': 'Logout successful',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'error': 'Logout failed',
            'message': 'Internal server error',
            'status': 'error'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT access token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token') if data else None
        
        if not refresh_token:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Refresh token required',
                'status': 'error'
            }), 400
        
        # Verify refresh token
        payload = auth_manager.verify_token(refresh_token)
        if payload.get('type') != 'refresh':
            return jsonify({
                'error': 'Invalid token',
                'message': 'Invalid refresh token',
                'status': 'error'
            }), 401
        
        # Get user info
        user = get_user_by_id(payload['user_id'])
        if not user or not user['active']:
            return jsonify({
                'error': 'User not found',
                'message': 'User account not active',
                'status': 'error'
            }), 401
        
        # Generate new tokens
        tokens = auth_manager.generate_tokens(
            user_id=user['id'],
            username=user['username'],
            role=user['role'],
            tenant_id=user.get('tenant_id')
        )
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'status': 'success',
            'data': {'tokens': tokens},
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'error': 'Token refresh failed',
            'message': str(e),
            'status': 'error'
        }), 401

@auth_bp.route('/profile', methods=['GET'])
@require_auth()
def get_profile():
    """Get current user profile"""
    try:
        user = get_user_by_id(request.user['id'])
        if not user:
            return jsonify({
                'error': 'User not found',
                'status': 'error'
            }), 404
        
        return jsonify({
            'message': 'Profile retrieved successfully',
            'status': 'success',
            'data': {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role'],
                    'email': user.get('email'),
                    'tenant_id': user.get('tenant_id'),
                    'permissions': request.user['permissions'],
                    'created_at': user.get('created_at')
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        return jsonify({
            'error': 'Profile retrieval failed',
            'message': 'Internal server error',
            'status': 'error'
        }), 500

@auth_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """List all users (admin only)"""
    try:
        users = []
        for user in ENTERPRISE_USERS.values():
            users.append({
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'email': user.get('email'),
                'tenant_id': user.get('tenant_id'),
                'active': user['active'],
                'created_at': user.get('created_at')
            })
        
        return jsonify({
            'message': 'Users retrieved successfully',
            'status': 'success',
            'data': {'users': users, 'count': len(users)},
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"User list error: {e}")
        return jsonify({
            'error': 'User list failed',
            'message': 'Internal server error',
            'status': 'error'
        }), 500

@auth_bp.route('/validate', methods=['GET'])
@require_auth()
def validate_token():
    """Validate current token and return user info"""
    return jsonify({
        'message': 'Token is valid',
        'status': 'success',
        'data': {
            'user': request.user,
            'valid': True
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# Enterprise roles and permissions info
@auth_bp.route('/roles', methods=['GET'])
@require_auth()
def get_roles():
    """Get available roles and permissions"""
    return jsonify({
        'message': 'Roles retrieved successfully',
        'status': 'success',
        'data': {
            'roles': auth_manager.roles,
            'current_user_role': request.user['role'],
            'current_user_permissions': request.user['permissions']
        },
        'timestamp': datetime.utcnow().isoformat()
    })
