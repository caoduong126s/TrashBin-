'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { RecyclingLocation } from '@/services/api';

// Fix for default Leaflet icon not appearing correctly in Next.js
const DefaultIcon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface RecyclingMapProps {
    locations: (RecyclingLocation & { distance?: number; travelTime?: number })[];
    center?: [number, number];
    zoom?: number;
}

// Helper to update map view when center changes
function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
    const map = useMap();
    useEffect(() => {
        map.setView(center, zoom);
    }, [center, zoom, map]);
    return null;
}

export default function RecyclingMap({
    locations,
    center = [10.762622, 106.660172], // Default TP.HCM
    zoom = 13
}: RecyclingMapProps) {
    const [isMounted, setIsMounted] = useState(false);
    const [userPos, setUserPos] = useState<[number, number] | null>(null);

    useEffect(() => {
        setIsMounted(true);
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => setUserPos([pos.coords.latitude, pos.coords.longitude]),
                () => console.log("Map popup geolocation failed")
            );
        }
    }, []);

    if (!isMounted) return <div className="h-[500px] w-full bg-gray-100 animate-pulse rounded-xl" />;

    const getGoogleMapsUrl = (lat: number, lng: number) => {
        const origin = userPos ? `${userPos[0]},${userPos[1]}` : '';
        return `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${lat},${lng}&travelmode=driving`;
    };

    return (
        <div className="h-[500px] w-full rounded-xl overflow-hidden shadow-inner border border-gray-200">
            <MapContainer
                center={center}
                zoom={zoom}
                scrollWheelZoom={true}
                style={{ height: '100%', width: '100%' }}
            >
                <ChangeView center={center} zoom={zoom} />
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {locations.map((loc) => (
                    <Marker key={loc.id} position={[loc.latitude, loc.longitude]}>
                        <Popup className="custom-popup">
                            <div className="p-1 min-w-[200px]">
                                <h3 className="font-bold text-green-700 text-base mb-1">{loc.name}</h3>
                                {loc.distance && (
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-bold">
                                            Cách bạn {loc.distance.toFixed(1)} km
                                        </span>
                                        {loc.travelTime && (
                                            <span className="text-[10px] text-orange-500 font-medium">
                                                ~{loc.travelTime} phút xe máy
                                            </span>
                                        )}
                                    </div>
                                )}
                                <p className="text-sm text-gray-600 mb-2">{loc.address}</p>
                                <div className="flex flex-wrap gap-1 mb-3">
                                    {loc.waste_types.split(',').map((type) => (
                                        <span key={type} className="bg-green-100 text-green-800 text-[10px] px-2 py-0.5 rounded-full uppercase font-semibold">
                                            {type.trim()}
                                        </span>
                                    ))}
                                </div>

                                <div className="space-y-1 mb-4 border-t pt-2">
                                    {loc.operating_hours && (
                                        <p className="text-xs text-gray-500 italic flex items-center gap-1">
                                            <span>🕒</span> {loc.operating_hours}
                                        </p>
                                    )}
                                    {loc.contact_phone && (
                                        <p className="text-xs text-gray-500 flex items-center gap-1">
                                            <span>📞</span> {loc.contact_phone}
                                        </p>
                                    )}
                                </div>

                                <a
                                    href={getGoogleMapsUrl(loc.latitude, loc.longitude)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-2 rounded-lg transition-colors"
                                >
                                    Chỉ đường bằng Google Maps
                                </a>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}
