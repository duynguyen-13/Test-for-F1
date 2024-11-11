
async function getPitStopDecision() {
    const tireHealth = parseFloat(document.getElementById('tire_health').value);
    const racePosition = parseInt(document.getElementById('race_position').value);
    const trackLength = parseInt(document.getElementById('track_length').value);
    const currentLap = parseInt(document.getElementById('current_lap').value);  // Lấy thông tin current lap

    const response = await fetch('http://127.0.0.1:5000/api/get_pit_decision', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tire_health: tireHealth,
            race_position: racePosition,
            track_length: trackLength,
            current_lap: currentLap  // Gửi thông tin current lap
        })
    });

    const data = await response.json();

    // Kiểm tra lỗi
    if (response.ok) {
        document.getElementById('result').innerText = 
            `Predicted lap time: ${data.predicted_lap_time.toFixed(2)} seconds, Decision: ${data.pit_decision}, Current Lap: ${data.current_lap}`;
    } else {
        document.getElementById('result').innerText = `Error: ${data.error}`;
    }
}
