import { RealtimeDetection } from '@/components/realtime/RealtimeDetection';
import { Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function RealtimePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-8 relative">
      <div className="container mx-auto px-4">
        {/* Quick Home Button */}
        <div className="mb-6 flex justify-start">
          <Link href="/">
            <Button variant="ghost" className="text-green-700 hover:text-green-800 hover:bg-green-50 font-bold gap-2 p-0">
              <Home className="w-5 h-5" />
              Về Trang Chủ
            </Button>
          </Link>
        </div>

        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Phát hiện Real-time
          </h1>
          <p className="text-gray-600">
            Sử dụng camera để phân loại rác tự động
          </p>
        </div>

        <RealtimeDetection />
      </div>
    </main>
  );
}
