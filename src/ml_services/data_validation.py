from ultralytics import YOLO

# Load a model
model = YOLO("./runs/detect/train/weights/best.pt")

data_config = './datasets/data.yaml'


validation_results = model.val(
    data=data_config
)

print(validation_results)
