from flask import Flask, jsonify, request
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
from flask_cors import CORS
import fastf1



import fastf1

# Load the session data
year = 2024
race_name = 'Australian Grand Prix'
driver_code = 'RUS'  # Example: George Russell
lap_number = 10  # Specify the lap number you want to pick

# Load the session
session = fastf1.get_session(year, race_name, 'R')  # 'R' for race session
session.load()  # Load the session data

# Load all laps from the session
laps = session.laps

# Pick a specific driver (e.g., 'RUS' for George Russell)
laps_driver = laps.pick_driver(driver_code)

# Attempt to pick the specific lap
try:
    # Filter laps for the specified lap number
    specific_lap = laps_driver[laps_driver['LapNumber'] == lap_number].iloc[0]
    print(f"Lap {lap_number} data for driver {driver_code}:")
    print(specific_lap)
except IndexError:
    print(f"Lap {lap_number} does not exist for driver {driver_code}.")



app = Flask(__name__)
CORS(app)

# Initialize and train the linear regression model
def train_model():
    # Sample data for training the model without tire_wear
    data = {
        'lap_time': [85, 90, 78, 92, 84, 87],  # Lap time (seconds)
        'race_position': [1, 2, 3, 4, 5, 6],  # Example race positions
        'track_length': [5000, 5000, 5000, 5000, 5000, 5000]  # Length of the track in meters
    }
    df = pd.DataFrame(data)

    # Split data into independent variables (X) and dependent variable (y)
    X = df[['race_position', 'track_length']]  # Independent variables without tire_wear
    y = df['lap_time']  # Dependent variable

    # Initialize the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Save the model
    joblib.dump(model, 'linear_regression_model.pkl')

# Endpoint to get pit stop decision
@app.route('/api/get_pit_decision', methods=['POST'])
def get_pit_decision():
    try:
        data = request.get_json()
        race_position = data['race_position']  # Ensure this key is correct
        track_length = data['track_length']  # Include track length
        current_lap = data['current_lap']  # Include current lap

        model = joblib.load('linear_regression_model.pkl')

        new_data = pd.DataFrame({'race_position': [race_position], 'track_length': [track_length]})
        predicted_time = model.predict(new_data)

        pit_threshold = 72.12  # Threshold lap time
        pit_decision = "Pit" if predicted_time[0] < pit_threshold else "No Pit"

        return jsonify({
            'predicted_lap_time': predicted_time[0],
            'pit_decision': pit_decision,
            'current_lap': current_lap  # Return current lap
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New endpoint to pick a specific lap
@app.route('/api/pick_lap', methods=['GET'])
def pick_lap():
    try:
        year = request.args.get('year', type=int)
        race_name = request.args.get('race_name', type=str)
        driver_code = request.args.get('driver_code', type=str)
        lap_number = request.args.get('lap_number', type=int)

        # Load the session data
        session = fastf1.get_session(year, race_name, 'R')  # 'R' for race session
        session.load()  # Load the session data

        # Load all laps from the session and pick the specific driver's laps
        laps = session.laps
        laps_driver = laps.pick_driver(driver_code)

        # Attempt to pick the specific lap
        specific_lap = laps_driver[laps_driver['LapNumber'] == lap_number]

        if specific_lap.empty:
            return jsonify({'error': f'Lap {lap_number} does not exist for driver {driver_code}.'}), 404

        # Convert the specific lap data to a dictionary
        lap_data = specific_lap.iloc[0].to_dict()
        return jsonify(lap_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New endpoint to get car data
@app.route('/api/get_car_data', methods=['GET'])
def get_car_data():
    try:
        year = request.args.get('year', type=int)
        race_name = request.args.get('race_name', type=str)
        driver_code = request.args.get('driver_code', type=str)

        # Load the session data
        session = fastf1.get_session(year, race_name, 'R')  # 'R' for race session
        session.load()  # Load the session data

        # Get car data for the specified driver
        car_data = session.car_data.loc[session.car_data['Driver'] == driver_code]

        if car_data.empty:
            return jsonify({'error': f'No car data found for driver {driver_code}.'}), 404

        # Convert the car data to a dictionary
        car_data_dict = car_data.to_dict(orient='records')
        return jsonify(car_data_dict), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    train_model()  # Train the model when the application starts
    app.run(debug=True)