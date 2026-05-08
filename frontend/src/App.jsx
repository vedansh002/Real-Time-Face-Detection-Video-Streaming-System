import CameraStream from './camera';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-blue-400">Real Time Face Detection</h1>
        <p className="text-slate-400">Detect faces in real-time</p>
      </header>
      
      <main className="flex justify-center">
        <CameraStream/>
      </main>
    </div>
  );
}

export default App;