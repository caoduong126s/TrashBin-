# GreenSort - AI-Powered Waste Classification System

GreenSort is a modern, AI-driven web application designed to help users classify waste accurately and promote environmental sustainability. By leveraging computer vision and real-time detection, GreenSort makes waste sorting intuitive and accessible for everyone.

##  Core Features

- **AI Waste Classification**: Upload or take a photo of waste items to get instant classification results and sorting guidance.
- **Real-time Camera Detection**: Use your device's camera for live detection and bounding box visualization of waste objects.
- **Interactive Waste Map**: Locate nearby recycle bins and waste disposal points with an integrated map interface.
- **Sorting Statistics**: Track your environmental impact with detailed statistics and classification history.
- **Educational Guide**: Learn the rules of waste sorting for different categories (Recyclable, Organic, Hazardous, General).
- **Responsive Design**: A premium, mobile-friendly interface built with glassmorphism and smooth animations.

##  Tech Stack

- **Framework**: [Next.js 16](https://nextjs.org/) (React 19)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Components**: [Radix UI](https://www.radix-ui.com/) & [Lucide Icons](https://lucide.dev/)
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
- **Data Visualization**: [Recharts](https://recharts.org/)
- **Maps**: [React Leaflet](https://react-leaflet.js.org/)
- **Real-time**: [Socket.io](https://socket.io/)

##  Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18.x or later)
- [npm](https://www.npmjs.com/) or [pnpm](https://pnpm.io/)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd green-sort-web-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Configure Environment Variables**:
   Create a `.env.local` file in the root directory and add your backend API URL:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```
   Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

##  Project Structure

- `app/`: Next.js App Router pages and layouts.
- `components/`: Reusable UI components (buttons, cards, sections).
- `hooks/`: Custom React hooks for state management and side effects.
- `lib/`: Utility functions and shared library configurations.
- `services/`: API client and WebSocket service integrations.
- `styles/`: Global CSS and Tailwind configurations.
- `public/`: Static assets (images, icons, fonts).

##  Scripts

- `npm run dev`: Starts the development server.
- `npm run build`: Builds the application for production.
- `npm run start`: Starts the production server.
- `npm run lint`: Runs ESLint for code quality checks.

---

Built by Lê Huỳnh Cao Dương
