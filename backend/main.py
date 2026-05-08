#importing libraries
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import io
import numpy as np
from PIL import Image
import mediapipe as mp
import json
import base64
from database import SessionLocal,init_db
from models import roilog

app=FastAPI(title="Face Detection API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )
init_db() #initialize the database tables

#initialize MediaPipe AI
mp_face_detection=mp.solutions.face_detection
face_detector=mp_face_detection.FaceDetection(min_detection_confidence=0.5)

@app.websocket("/ws/stream")
async def video_stream(websocket: WebSocket):
    """
    This WebSocket accepts raw image bytes from the React frontend,
    processes them to find the face, draws the NumPy box, and returns
    both the processed image and the ROI data.
    """
    await websocket.accept()
    print("Frontend connected to WebSocket")
    try:
        while 1:
            #raw JPEG frame from the browser
            image_bytes=await websocket.receive_bytes()
            #bytes->PIL Image->NumPy Array
            image=Image.open(io.BytesIO(image_bytes)).convert("RGB")
            frame=np.array(image)
            h,w,_=frame.shape
            roi_data=None
            results=face_detector.process(frame)
            if results.detections:
                for detection in results.detections:
                    box=detection.location_data.relative_bounding_box
                    x1=max(0,int(box.xmin*w))
                    y1=max(0,int(box.ymin*h))
                    x2=min(w,int((box.xmin+box.width)*w))
                    y2=min(h,int((box.ymin+box.height)*h))
                    roi_data={"x1":x1,"y1":y1,"x2":x2,"y2":y2}
                    #saving to the database
                    db=SessionLocal()
                    try:
                        new_log=roilog(
                            x1=roi_data["x1"], 
                            y1=roi_data["y1"], 
                            x2=roi_data["x2"], 
                            y2=roi_data["y2"]
                        )
                        db.add(new_log)
                        db.commit()
                    except Exception as e:
                        print(f"Database error: {e}")
                    finally:
                        db.close()
                    #Drawing
                    thickness=3
                    color=[0,255,0] #green
                    #top edge
                    frame[y1:min(y1+thickness,h),x1:x2]=color
                    #bottom edge
                    frame[max(y2-thickness,0):y2,x1:x2]=color
                    #left edge
                    frame[y1:y2,x1:min(x1+thickness,w)]=color
                    #right edge
                    frame[y1:y2,max(x2-thickness,0):x2]=color

            #NumPy array->PIL Image->Base64 String
            processed_image=Image.fromarray(frame)
            buffer=io.BytesIO()
            processed_image.save(buffer,format="JPEG")
            base64_encoded=base64.b64encode(buffer.getvalue()).decode("utf-8")
            #send the image and data back to the frontend
            response={"image":f"data:image/jpeg;base64,{base64_encoded}", "roi": roi_data}
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        print("Frontend disconnected.")