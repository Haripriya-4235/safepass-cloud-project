// Live GPS Tracking Service

let locationWatchId = null;

function startLiveLocationTracking(journeyId) {
    if (!navigator.geolocation) {
        console.warn("Geolocation API unavailable.");
        return;
    }

    // Ping server every 10 seconds with current coordinates
    locationWatchId = navigator.geolocation.watchPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const speed = position.coords.speed || 0;

            fetch('/api/location/ping', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    journey_id: journeyId,
                    latitude: lat,
                    longitude: lng,
                    speed: speed
                })
            })
            .then(res => res.json())
            .then(data => {
                console.log("[Live Tracking Ping Recorded]", data);
            })
            .catch(err => console.error("Tracking ping failed:", err));
        },
        (error) => {
            console.error("GPS tracking error:", error);
        },
        { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
    );
}

function stopLiveLocationTracking() {
    if (locationWatchId !== null) {
        navigator.geolocation.clearWatch(locationWatchId);
        locationWatchId = null;
        console.log("Live location tracking stopped.");
    }
}
