# Inspecly Bakckend
The app takes image of nuts & bolts with paint marks on it to check if the bolts are tightening/missed.
It processes the image and gives the output after inspection marking of its alignment.

### Features
- Takes image as input and performs object detection to detect nuts & bolts in image
- On the detected image checks for white paint marks and applies logic to decide alignment
- Saves the original image, and inspection image along with inspection details in the DB.

### Pre-requisites
- Python3
- FastApi (REST APIs)
- cv2, numpy, matplotlib, PIL (Image Processing)
- YOLO (ML Object Detection Model)
- MongoDB (Stores Image Snapshot with Processed Image)

### Getting Started
1. Install all the dependencies preferrably in python virtual environment
`pip install -r requirements.txt`
2. Train the YOLO ML Model for object detection
- Currently, trained using `'yolo11n.pt'` and other options are `'yolo11s.pt'`, `'yolo11m.pt'`, `'yolo11l.pt'`, `'yolo11x.pt'`
- For this need to update the datasets with more images, and annotations.
- Current datasets present in `ml_services/datasets`
- Validatae the YOLO Model (currently validated using `"runs/detect/train/weights/best.pt"`)
3. Use the Best Trained Model for Image detection in Image Services
- Currently beings using `"runs/detect/train/weights/best.pt"`
4. Update the Configs in config/setup.py
5. Run the `python main.py` in src

### Access the APIs
- Access the APIs through Swagger [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)
- Additionaly it can be hosted as public APIs using localhost through `ngrok`
- The Live Endpoints are available at [https://rapid-narwhal-sharply.ngrok-free.app/docs](https://rapid-narwhal-sharply.ngrok-free.app/docs)
