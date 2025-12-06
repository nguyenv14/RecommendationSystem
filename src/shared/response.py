"""
API Response Helper
Standardized API response format for all endpoints
"""

from typing import Any, Optional, Dict, Tuple
from flask import jsonify, Response


class ApiResponse:
    """
    Standardized API response helper
    Format:
    - Success: { "success": true, "code": 200, "message": "OK", "data": {...} }
    - Error: { "success": false, "code": 400, "message": "Error", "data": null }
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "OK",
        code: int = 200
    ) -> Tuple[Response, int]:
        """
        Return success response
        
        Args:
            data: Response data (can be dict, list, or any serializable object)
            message: Success message
            code: HTTP status code (default: 200)
            
        Returns:
            Tuple of (jsonify response, status code)
        """
        return jsonify({
            "success": True,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    @staticmethod
    def error(
        message: str = "Error",
        code: int = 400,
        data: Any = None
    ) -> Tuple[Response, int]:
        """
        Return error response
        
        Args:
            message: Error message
            code: HTTP status code (default: 400)
            data: Optional error data/details
            
        Returns:
            Tuple of (jsonify response, status code)
        """
        return jsonify({
            "success": False,
            "code": code,
            "message": message,
            "data": data
        }), code

