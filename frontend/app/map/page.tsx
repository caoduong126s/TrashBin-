'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { getLocations, RecyclingLocation } from '@/services/api';
import { MapPin, Info, Navigation, Search, Filter, Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';

// Import map dynamically to avoid SSR issues with Leaflet
const RecyclingMap = dynamic(
    () => import('@/components/map/RecyclingMap'),
    {
        ssr: false,
        loading: () => <div className="h-[500px] w-full bg-gray-100 animate-pulse rounded-xl flex items-center justify-center">Đang tải bản đồ...</div>
    }
);

const HCM_CENTER: [number, number] = [10.762622, 106.660172];

// Haversine formula to calculate distance between two points in km
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c;
    return d;
}

interface LocationWithDistance extends RecyclingLocation {
    distance?: number;
    travelTime?: number;
}

export default function MapPage() {
    const [locations, setLocations] = useState<LocationWithDistance[]>([]);
    const [filteredLocations, setFilteredLocations] = useState<LocationWithDistance[]>([]);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
    const [center, setCenter] = useState<[number, number]>(HCM_CENTER);
    const [zoom, setZoom] = useState(13);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterType, setFilterType] = useState('all');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchLocations();
        // Try to get user location on load
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos: [number, number] = [position.coords.latitude, position.coords.longitude];
                    setUserLocation(pos);
                    setCenter(pos);
                    setZoom(14);
                },
                (error) => console.log("Init geolocation failed:", error)
            );
        }
    }, []);

    useEffect(() => {
        let result = [...locations];

        // 1. Calculate distances if user location is available
        if (userLocation) {
            result = result.map(loc => {
                const dist = calculateDistance(userLocation[0], userLocation[1], loc.latitude, loc.longitude);
                return {
                    ...loc,
                    distance: dist,
                    travelTime: Math.round(dist / 25 * 60) // Assume 25km/h avg speed
                };
            });
            // 2. Sort by distance
            result.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        }

        // 3. Apply Search Filter
        if (searchQuery) {
            result = result.filter(loc =>
                loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                loc.address.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        // 4. Apply Waste Type Filter
        if (filterType !== 'all') {
            result = result.filter(loc =>
                loc.waste_types.toLowerCase().includes(filterType.toLowerCase())
            );
        }

        setFilteredLocations(result);
    }, [searchQuery, filterType, locations, userLocation]);

    const fetchLocations = async () => {
        setIsLoading(true);
        const data = await getLocations();
        setLocations(data);
        setIsLoading(false);
    };

    const handleUseCurrentLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos: [number, number] = [position.coords.latitude, position.coords.longitude];
                    setUserLocation(pos);
                    setCenter(pos);
                    setZoom(15);
                },
                (error) => {
                    console.error("Geolocation error:", error);
                    alert("Không thể lấy vị trí của bạn.");
                }
            );
        }
    };

    const focusOnLocation = (loc: RecyclingLocation) => {
        setCenter([loc.latitude, loc.longitude]);
        setZoom(16);
    };

    return (
        <main className="min-h-screen bg-gray-50 pb-20 relative">
            {/* Quick Home Button */}
            <div className="absolute top-24 left-6 z-20">
                <Link href="/">
                    <Button variant="outline" className="bg-white/90 backdrop-blur-sm border-white/20 shadow-md hover:bg-white text-green-700 font-bold gap-2">
                        <Home className="w-4 h-4" />
                        Về Trang Chủ
                    </Button>
                </Link>
            </div>

            {/* Hero Section */}
            <div className="bg-[#10b981] pt-32 pb-16 px-6 text-white text-center">
                <h1 className="text-4xl md:text-5xl font-bold mb-4">Bản đồ Điểm thu gom TPHCM</h1>
                <p className="text-lg opacity-90 max-w-2xl mx-auto">
                    Tìm kiếm các trạm thu gom pin, rác điện tử và điểm tái chế gần bạn nhất để bảo vệ môi trường Sài Gòn.
                </p>
            </div>

            <div className="max-w-7xl mx-auto px-6 -mt-10">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

                    {/* Controls & List */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="bg-white p-6 rounded-2xl shadow-lg space-y-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Filter className="w-5 h-5 text-green-600" />
                                <h3 className="font-bold text-gray-900">Bộ lọc</h3>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-gray-500 uppercase">Tìm kiếm</label>
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <Input
                                        placeholder="Tên đường, phường..."
                                        className="pl-9"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-gray-500 uppercase">Loại rác</label>
                                <Select value={filterType} onValueChange={setFilterType}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Tất cả loại rác" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="all">Tất cả</SelectItem>
                                        <SelectItem value="pin">Pin cũ</SelectItem>
                                        <SelectItem value="điện tử">Rác điện tử</SelectItem>
                                        <SelectItem value="nhựa">Nhựa</SelectItem>
                                        <SelectItem value="giấy">Giấy</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <Button
                                onClick={handleUseCurrentLocation}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                            >
                                <Navigation className="w-4 h-4 mr-2" />
                                Vị trí của tôi
                            </Button>
                        </div>

                        <div className="bg-white rounded-2xl shadow-lg flex flex-col max-h-[500px]">
                            <div className="p-4 border-b flex justify-between items-center">
                                <h3 className="font-bold text-gray-900">Danh sách ({filteredLocations.length})</h3>
                                {userLocation && <span className="text-[10px] text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded-full">Đã sắp xếp theo vị trí</span>}
                            </div>
                            <div className="overflow-y-auto flex-1 p-2 space-y-2">
                                {filteredLocations.map(loc => (
                                    <button
                                        key={loc.id}
                                        onClick={() => focusOnLocation(loc)}
                                        className="w-full text-left p-3 rounded-xl hover:bg-green-50 transition-colors border border-transparent hover:border-green-100 group relative"
                                    >
                                        <div className="flex justify-between items-start gap-2">
                                            <h4 className="font-bold text-sm text-gray-800 group-hover:text-green-700">{loc.name}</h4>
                                            {loc.distance && (
                                                <span className="text-[10px] font-bold text-gray-400 whitespace-nowrap shrink-0">
                                                    {loc.distance.toFixed(1)} km
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-xs text-gray-500 line-clamp-1 mt-1">{loc.address}</p>

                                        <div className="flex items-center justify-between mt-2">
                                            <div className="flex gap-1">
                                                {loc.waste_types.split(',').slice(0, 2).map(t => (
                                                    <span key={t} className="text-[9px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                                                        {t.trim()}
                                                    </span>
                                                ))}
                                            </div>
                                            {loc.travelTime && (
                                                <span className="text-[10px] text-orange-500 font-medium">
                                                    ~{loc.travelTime} phút xe máy
                                                </span>
                                            )}
                                        </div>
                                    </button>
                                ))}
                                {filteredLocations.length === 0 && (
                                    <div className="p-8 text-center text-gray-400">
                                        <Info className="w-8 h-8 mx-auto mb-2 opacity-20" />
                                        <p className="text-sm">Không tìm thấy địa điểm nào</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Map Area */}
                    <div className="lg:col-span-3">
                        <div className="bg-white p-2 rounded-2xl shadow-xl border border-white h-[600px]">
                            <RecyclingMap
                                locations={filteredLocations.map(l => ({
                                    ...l,
                                    distance: l.distance,
                                    travelTime: l.travelTime
                                }))}
                                center={center}
                                zoom={zoom}
                            />
                        </div>

                        <div className="mt-6 p-6 bg-white rounded-2xl shadow-md border border-gray-100 flex items-start gap-4">
                            <div className="w-12 h-12 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center shrink-0">
                                <Info className="w-6 h-6" />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900">Hướng dẫn sử dụng bản đồ</h4>
                                <p className="text-sm text-gray-600 mt-1">
                                    Hệ thống tự động sắp xếp các trạm thu gom từ gần đến xa dựa trên vị trí hiện tại của bạn.
                                    Nhấp vào từng trạm trên bản đồ để xem chi tiết địa chỉ, thời gian mở cửa và hướng dẫn chỉ đường bằng Google Maps.
                                </p>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </main>
    );
}
