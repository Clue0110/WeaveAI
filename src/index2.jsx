import React from 'react';
import UploadInterface from './UploadInterface'; // Import the component
import './globals.css'; // Ensure global styles are imported

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 md:p-24 bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <UploadInterface />
    </main>
  );
}

