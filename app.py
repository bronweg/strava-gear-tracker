from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from config import Config
from models import db, User, Equipment
from strava_auth import StravaAuth
from equipment_service import EquipmentService

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Login page with Strava OAuth."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    auth_url = StravaAuth.get_authorization_url()
    return render_template('login.html', auth_url=auth_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle Strava OAuth callback."""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        flash(f'Authentication error: {error}', 'danger')
        return redirect(url_for('login'))

    if not code:
        flash('No authorization code received', 'danger')
        return redirect(url_for('login'))

    try:
        # Exchange code for token
        token_data = StravaAuth.exchange_code_for_token(code)

        # Save user and token
        user = StravaAuth.save_user_and_token(token_data)

        # Log in the user
        login_user(user)

        flash('Successfully logged in with Strava!', 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f'Authentication failed: {str(e)}', 'danger')
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard showing all equipment with statistics."""
    try:
        # Sync bikes from Strava on dashboard load
        try:
            EquipmentService.sync_bikes_from_strava(current_user)
        except Exception as bike_sync_error:
            # Don't fail the whole dashboard if bike sync fails
            flash(f'Could not sync bikes from Strava: {str(bike_sync_error)}', 'warning')

        equipment_with_stats = EquipmentService.get_equipment_with_stats(current_user)
        bikes = EquipmentService.get_user_bikes(current_user)

        return render_template('dashboard.html', equipment_data=equipment_with_stats, bikes=bikes)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html', equipment_data=[], bikes=[])


@app.route('/equipment/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    """Add new equipment."""
    # Get bikes for the dropdown
    bikes = EquipmentService.get_user_bikes(current_user)

    if request.method == 'POST':
        name = request.form.get('name')
        equipment_type = request.form.get('equipment_type')
        installation_date_str = request.form.get('installation_date')
        notes = request.form.get('notes')
        strava_bike_id = request.form.get('strava_bike_id')

        # Validation
        if not name or not installation_date_str:
            flash('Name and installation date are required', 'danger')
            return render_template('add_equipment.html', bikes=bikes)

        try:
            installation_date = datetime.strptime(installation_date_str, '%Y-%m-%d').date()

            # Convert empty string to None for bike_id
            bike_id = strava_bike_id if strava_bike_id else None

            EquipmentService.create_equipment(
                user=current_user,
                name=name,
                equipment_type=equipment_type,
                installation_date=installation_date,
                notes=notes,
                strava_bike_id=bike_id
            )

            flash(f'Equipment "{name}" added successfully!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            flash('Invalid date format', 'danger')
        except Exception as e:
            flash(f'Error adding equipment: {str(e)}', 'danger')

    return render_template('add_equipment.html', bikes=bikes)




@app.route('/equipment/edit/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(equipment_id):
    """Edit existing equipment."""
    equipment = EquipmentService.get_equipment_by_id(equipment_id, current_user)

    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('dashboard'))

    # Get bikes for the dropdown
    bikes = EquipmentService.get_user_bikes(current_user)

    if request.method == 'POST':
        name = request.form.get('name')
        equipment_type = request.form.get('equipment_type')
        installation_date_str = request.form.get('installation_date')
        notes = request.form.get('notes')
        strava_bike_id = request.form.get('strava_bike_id')

        # Validation
        if not name or not installation_date_str:
            flash('Name and installation date are required', 'danger')
            return render_template('edit_equipment.html', equipment=equipment, bikes=bikes)

        try:
            installation_date = datetime.strptime(installation_date_str, '%Y-%m-%d').date()

            # Convert empty string to None for bike_id
            bike_id = strava_bike_id if strava_bike_id else None

            EquipmentService.update_equipment(
                equipment_id=equipment_id,
                user=current_user,
                name=name,
                equipment_type=equipment_type,
                installation_date=installation_date,
                notes=notes,
                strava_bike_id=bike_id
            )

            flash(f'Equipment "{name}" updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            flash('Invalid date format', 'danger')
        except Exception as e:
            flash(f'Error updating equipment: {str(e)}', 'danger')

    return render_template('edit_equipment.html', equipment=equipment, bikes=bikes)


@app.route('/equipment/delete/<int:equipment_id>', methods=['POST'])
@login_required
def delete_equipment(equipment_id):
    """Delete equipment."""
    success = EquipmentService.delete_equipment(equipment_id, current_user)

    if success:
        flash('Equipment deleted successfully', 'success')
    else:
        flash('Equipment not found', 'danger')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
