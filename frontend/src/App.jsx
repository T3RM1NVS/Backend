import React from 'react';
import 'leaflet/dist/leaflet.css';
import './index.css';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// ===== Leaflet Icon Setup =====
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

const VW_BLUE = '#004d9e';
const VW_LIGHT_BLUE = '#4a90e2';
const SUCCESS_GREEN = '#28a745';
const ERROR_RED = '#dc3545';

const UserLocationIcon = L.divIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" fill="none" stroke="${VW_LIGHT_BLUE}" stroke-width="1.8" viewBox="0 0 24 24"><circle cx="12" cy="10" r="3.2"/><path d="M21 21v-1a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v1"/></svg>`,
  className: 'custom-svg-icon',
  iconSize: [34, 34],
  iconAnchor: [17, 34],
  popupAnchor: [0, -32],
});

const ParkingSpotIcon = (color) =>
  L.divIcon({
    html: `<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="${color}" stroke="white" stroke-width="1" viewBox="0 0 24 24"><path d="M12 2C7.03 2 3 7.03 3 12s4.03 10 9 10 9-4.03 9-10S16.97 2 12 2zm1 14h-4v-2h2v-2h-2V7h4v2h-2v2h2v5z"/></svg>`,
    className: 'custom-svg-icon',
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36],
  });

function ChangeView({ center, zoom }) {
  const map = useMap();
  React.useEffect(() => {
    if (center) map.flyTo(center, zoom, { animate: true, duration: 1 });
  }, [center, zoom, map]);
  return null;
}

const LoadingSpinner = ({ message }) => (
  <div className="loading-wrap">
    <div className="spinner" />
    <div className="loading-text">{message}</div>
  </div>
);

export default function App() {
  const [userLocation, setUserLocation] = React.useState(null);
  const [parkingSpots, setParkingSpots] = React.useState([]);
  const [selectedSpot, setSelectedSpot] = React.useState(null);
  const [loading, setLoading] = React.useState({ init: true, booking: false, spots: false });
  const [bookingStatus, setBookingStatus] = React.useState(null);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let cancelled = false;
    const fallback = { lat: 12.9716, lng: 77.5946 };

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (!cancelled) setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
      },
      () => {
        if (!cancelled) {
          setUserLocation(fallback);
          setError('Location access denied — using default location.');
        }
      },
      { timeout: 8000 }
    );
    return () => (cancelled = true);
  }, []);

  React.useEffect(() => {
    if (!userLocation) return;
    const fetchSpots = async () => {
      setLoading((l) => ({ ...l, spots: true }));
      try {
        const res = await fetch(
          `http://localhost:8000/ml/nearest-parkings?latitude=${userLocation.lat}&longitude=${userLocation.lng}`
        );
        const data = await res.json();
        setParkingSpots(Array.isArray(data) ? data : []);
      } catch {
        setError('Unable to reach parking service.');
      } finally {
        setLoading((l) => ({ ...l, spots: false, init: false }));
      }
    };
    fetchSpots();
  }, [userLocation]);

  const handleBooking = async (spot) => {
    setBookingStatus({ state: 'loading', text: 'Booking...' });
    try {
      const res = await fetch('http://localhost:8000/bookings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parking_id: spot.parking_id, user_id: 1 }),
      });
      const result = await res.json();
      setBookingStatus({ state: 'success', text: `Booked ✓ (ID: ${result.booking_id || '—'})` });
      setParkingSpots((prev) =>
        prev.map((p) => (p.parking_id === spot.parking_id ? { ...p, reserved: true } : p))
      );
    } catch {
      setBookingStatus({ state: 'error', text: 'Booking failed' });
    } finally {
      setTimeout(() => setBookingStatus(null), 4000);
    }
  };

  const markerColor = (spot) => {
    if (spot.reserved) return '#b0b0b0';
    if (spot.occupancy_percent < 60) return VW_BLUE;
    if (spot.occupancy_percent < 85) return VW_LIGHT_BLUE;
    return '#ff8c00';
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img src="/volkswagen.svg" alt="logo" width={28} />
          <div>
            <h1>Parking Finder</h1>
            <p>Predictive • Book • Park</p>
          </div>
        </div>

        <div className="search-container">
          <input className="search-input" placeholder="Search location (mock)" />
          <button
            className="refresh-btn"
            onClick={() => {
              setError(null);
              setParkingSpots([]);
              setSelectedSpot(null);
              setLoading({ init: true });
              navigator.geolocation.getCurrentPosition(
                (pos) => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
                () => setUserLocation({ lat: 12.9716, lng: 77.5946 })
              );
            }}
          >
            Refresh
          </button>
        </div>

        {loading.init && <LoadingSpinner message="Locating nearby parkings..." />}
        {error && <div className="error-block">{error}</div>}

        <ul className="parking-list">
          {parkingSpots.map((spot) => (
            <li
              key={spot.parking_id}
              className={`parking-card ${
                selectedSpot?.parking_id === spot.parking_id ? 'selected' : ''
              }`}
              onClick={() => setSelectedSpot(spot)}
            >
              <div className="parking-meta">
                <h3>{spot.name || `Parking ${spot.parking_id}`}</h3>
                <p>{spot.address || 'No address'}</p>
              </div>
              <div className="parking-actions">
                <span className="distance">{spot.distance?.toFixed(2)} km</span>
                <button
                  className={`btn-book ${spot.reserved ? 'disabled' : ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    if (!spot.reserved) handleBooking(spot);
                  }}
                >
                  {spot.reserved ? 'Reserved' : 'Book'}
                </button>
              </div>
            </li>
          ))}
        </ul>

        {bookingStatus && (
          <div
            className={`status-pill ${
              bookingStatus.state === 'success'
                ? 'status-success'
                : bookingStatus.state === 'error'
                ? 'status-error'
                : ''
            }`}
          >
            {bookingStatus.text}
          </div>
        )}
      </aside>

      <div className="map-area">
        {userLocation && (
          <MapContainer center={userLocation} zoom={14}>
            <ChangeView center={userLocation} zoom={14} />
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <Marker position={userLocation} icon={UserLocationIcon}>
              <Popup>Your location</Popup>
            </Marker>
            {parkingSpots.map((spot) => (
              <Marker
                key={spot.parking_id}
                position={[spot.latitude, spot.longitude]}
                icon={ParkingSpotIcon(markerColor(spot))}
              >
                <Popup>
                  {spot.name || 'Parking Spot'} <br />
                  {spot.distance?.toFixed(2)} km away
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  );
}
