from flask import Blueprint, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_db
from .auth_middleware import require_auth
from .encryption import encrypt_password, decrypt_password


users_bp = Blueprint("users", __name__)


def _require_manager_or_owner():
    """Check if current user is manager or owner_admin."""
    role = g.auth_claims.get("role", "")
    if role not in ("owner_admin", "manager"):
        return jsonify({"error": "unauthorized - manager or owner required"}), 403
    return None


@users_bp.route("/", methods=["OPTIONS"], strict_slashes=False)
@users_bp.route("/<int:user_id>", methods=["OPTIONS"])
@users_bp.route("/<int:user_id>/activate", methods=["OPTIONS"])
def preflight(user_id=None):
    return ("", 204)


@users_bp.get("/", strict_slashes=False)
@require_auth
def list_users():
    """List all users with decrypted passwords (manager/owner only)."""
    error_response = _require_manager_or_owner()
    if error_response:
        return error_response
    
    db = get_db()
    rows = db.execute(
        "SELECT id, username, role, is_active, password_encrypted, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    
    users = []
    for row in rows:
        user_data = {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "is_active": bool(row["is_active"]),
            "created_at": row["created_at"],
            "password": None
        }
        
        if row["password_encrypted"]:
            try:
                user_data["password"] = decrypt_password(row["password_encrypted"])
            except Exception:
                user_data["password"] = None
        
        users.append(user_data)
    
    return jsonify({"users": users})


@users_bp.post("/", strict_slashes=False)
@require_auth
def create_user():
    """Create a new user (manager/owner only)."""
    error_response = _require_manager_or_owner()
    if error_response:
        return error_response
    
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    role = str(payload.get("role", "")).strip()
    
    if not username or not password or not role:
        return jsonify({"error": "username, password, and role are required"}), 400
    
    if role not in ("manager", "cashier"):
        return jsonify({"error": "role must be 'manager' or 'cashier'"}), 400
    
    if len(password) < 4:
        return jsonify({"error": "password must be at least 4 characters"}), 400
    
    db = get_db()
    
    existing = db.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    if existing:
        return jsonify({"error": "username already exists"}), 409
    
    password_hash = generate_password_hash(password)
    password_encrypted = encrypt_password(password)
    
    result = db.execute(
        "INSERT INTO users (username, password_hash, password_encrypted, role, is_active) VALUES (?, ?, ?, ?, 1)",
        (username, password_hash, password_encrypted, role)
    )
    db.commit()
    
    user_id = result.lastrowid
    
    return jsonify({
        "id": user_id,
        "username": username,
        "role": role,
        "is_active": True,
        "password": password
    }), 201


@users_bp.patch("/<int:user_id>")
@require_auth
def update_user(user_id: int):
    """Update user username and/or password (manager/owner only)."""
    error_response = _require_manager_or_owner()
    if error_response:
        return error_response
    
    payload = request.get_json(silent=True) or {}
    username = payload.get("username", "").strip() if payload.get("username") else None
    password = payload.get("password", "").strip() if payload.get("password") else None
    
    if not username and not password:
        return jsonify({"error": "username or password must be provided"}), 400
    
    db = get_db()
    
    target_user = db.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    if not target_user:
        return jsonify({"error": "user not found"}), 404
    
    if target_user["role"] == "owner_admin":
        return jsonify({"error": "cannot modify owner_admin user"}), 403
    
    if username:
        existing = db.execute(
            "SELECT id FROM users WHERE username = ? AND id != ?",
            (username, user_id)
        ).fetchone()
        if existing:
            return jsonify({"error": "username already exists"}), 409
        
        db.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
    
    if password:
        if len(password) < 4:
            return jsonify({"error": "password must be at least 4 characters"}), 400
        
        password_hash = generate_password_hash(password)
        password_encrypted = encrypt_password(password)
        db.execute(
            "UPDATE users SET password_hash = ?, password_encrypted = ? WHERE id = ?",
            (password_hash, password_encrypted, user_id)
        )
    
    db.commit()
    
    updated_user = db.execute(
        "SELECT id, username, role, is_active, password_encrypted FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    
    decrypted_password = None
    if updated_user["password_encrypted"]:
        try:
            decrypted_password = decrypt_password(updated_user["password_encrypted"])
        except Exception:
            pass
    
    return jsonify({
        "id": updated_user["id"],
        "username": updated_user["username"],
        "role": updated_user["role"],
        "is_active": bool(updated_user["is_active"]),
        "password": decrypted_password
    })


@users_bp.patch("/<int:user_id>/activate")
@require_auth
def toggle_user_active(user_id: int):
    """Toggle user active status (manager/owner only)."""
    error_response = _require_manager_or_owner()
    if error_response:
        return error_response
    
    payload = request.get_json(silent=True) or {}
    is_active = payload.get("is_active")
    
    if is_active is None:
        return jsonify({"error": "is_active is required"}), 400
    
    db = get_db()
    
    target_user = db.execute(
        "SELECT id, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    if not target_user:
        return jsonify({"error": "user not found"}), 404
    
    if target_user["role"] == "owner_admin":
        return jsonify({"error": "cannot modify owner_admin user"}), 403
    
    active_value = 1 if is_active else 0
    db.execute("UPDATE users SET is_active = ? WHERE id = ?", (active_value, user_id))
    db.commit()
    
    return jsonify({"id": user_id, "is_active": bool(is_active)})


@users_bp.delete("/<int:user_id>")
@require_auth
def delete_user(user_id: int):
    """Delete a user after password confirmation (manager/owner only)."""
    error_response = _require_manager_or_owner()
    if error_response:
        return error_response
    
    payload = request.get_json(silent=True) or {}
    confirm_password = str(payload.get("confirm_password", "")).strip()
    
    if not confirm_password:
        return jsonify({"error": "confirm_password is required"}), 400
    
    db = get_db()
    
    current_user_id = g.auth_claims.get("uid")
    current_user = db.execute(
        "SELECT password_hash FROM users WHERE id = ?",
        (current_user_id,)
    ).fetchone()
    
    if not current_user or not check_password_hash(current_user["password_hash"], confirm_password):
        return jsonify({"error": "password confirmation failed"}), 401
    
    target_user = db.execute(
        "SELECT id, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    if not target_user:
        return jsonify({"error": "user not found"}), 404
    
    if target_user["role"] == "owner_admin":
        return jsonify({"error": "cannot delete owner_admin user"}), 403
    
    if target_user["id"] == current_user_id:
        return jsonify({"error": "cannot delete yourself"}), 403
    
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    
    return jsonify({"success": True, "id": user_id})
