import React,{useEffect,useRef,useState} from 'react';

const CameraStream=()=>{
  const videoref=useRef(null);
  const canvasref=useRef(null);
  const socketref=useRef(null);
  const [processedimage,setimage]=useState(null);
  const [roi,setroi]=useState(null);

  useEffect(()=>{
    socketref.current=new WebSocket('ws://localhost:8000/ws/stream');
    socketref.current.onmessage=(event)=>{
      const data=JSON.parse(event.data);
      setimage(data.image); //image with the green box
      setroi(data.roi); //coordinate data
    };

    //webcam start
    navigator.mediaDevices.getUserMedia({video:true}).then((stream) => {
      videoref.current.srcObject=stream;
      videoref.current.play();
    });

    //frames every 100ms 
    const interval=setInterval(()=>{
      if(socketref.current.readyState===WebSocket.OPEN){
        const canvas=canvasref.current;
        const context=canvas.getContext('2d');
        context.drawImage(videoref.current,0,0,canvas.width,canvas.height);
        
        // canvas to blob
        canvas.toBlob((blob) => {
          socketref.current.send(blob);
        }, 'image/jpeg', 0.7);
      }
    }, 100);
    return () => {
      clearInterval(interval);
      socketref.current.close();
    };
  }, []);

  return (
    <div className="flex flex-col items-center gap-4">
      <video ref={videoref} style={{ display: 'none' }} />
      <canvas ref={canvasref} width="640" height="480" style={{ display: 'none' }} />
      <div className="relative border-4 border-slate-800 rounded-lg overflow-hidden bg-black">
        {processedimage ? (
          <img src={processedimage} alt="Stream" className="w-full max-w-2xl" />
        ) : (
          <div className="w-[640px] h-[480px] flex items-center justify-center text-white">
            Loading Camera
          </div>
        )}
      </div>
      {roi && (
        <div className="bg-slate-900 text-green-400 p-4 rounded-md font-mono text-sm w-full max-w-2xl">
          <p>LIVE ROI: [x1: {roi.x1}, y1: {roi.y1}, x2: {roi.x2}, y2: {roi.y2}]</p>
        </div>
      )}
    </div>
  );
};

export default CameraStream;
