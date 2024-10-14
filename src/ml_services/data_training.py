from ultralytics import YOLO


model = YOLO("yolo11s.pt")
data_config = './datasets/data.yaml'

# Check if there's an existing checkpoint to resume from (set your custom path)
checkpoint_path = 'runs/train/nuts_bolts_detection/weights/last.pt'

try:
    # Attempt to resume training
    print(f"Resuming training from {checkpoint_path}...")
    model.train(
        data=data_config,
        epochs=20,
        batch=16,
        imgsz=640,
        name='nuts_bolts_detection',
        project='runs/train',
        resume=True,
        plots=True
    )
except Exception as e:
    if isinstance(e, FileNotFoundError):
        print("No checkpoint found, starting fresh...")
        model.train(
            data=data_config,
            epochs=20,
            batch=16,
            imgsz=640,
            name='nuts_bolts_detection',
            project='runs/train',
            resume=False,
            plots=True
        )
    else:
        print(f"An unexpected error occurred, Type: {type(e).__name__}, Error: {e}")
finally:
    print("Training Completed")
